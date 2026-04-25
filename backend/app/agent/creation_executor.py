"""CreationExecutor: Blueprint 실행 로직 (DB 생성, 블록 배치, 후처리, 검증, 롤백)

orchestrator.py에서 분리된 생성 실행 전담 클래스.
스트리밍/논스트리밍 두 인터페이스를 제공:
- execute_streaming(): AsyncGenerator — 진행 이벤트를 yield, 최종 결과는 "result" 이벤트로 반환
- execute_blueprint(): 논스트리밍 편의 래퍼 — 결과 dict만 반환
"""

import logging
from typing import Any, AsyncGenerator

from app.agent.tools.add_blocks import spec_to_block
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.agent.view_builder import build_view_configuration
from app.notion.block_builder import build_database_properties
from app.notion.client import NotionClient

logger = logging.getLogger("notionforge.creation_executor")


class CreationExecutor:
    """Blueprint의 Notion 리소스 생성을 담당하는 실행기."""

    def __init__(self, client: NotionClient, add_items_tool: AddDatabaseItemsTool):
        self.client = client
        self.add_items_tool = add_items_tool

    # ── DB 생성 + 샘플 데이터 + 뷰 ─────────────────────────────

    async def create_database_with_data(self, parent_id: str, db_spec: dict) -> dict[str, Any]:
        """DB 생성 + 샘플 데이터 + 뷰 자동 생성"""
        # relation/rollup/formula는 후처리에서 추가 (target DB ID 필요)
        # AI가 "properties" 또는 "db_properties" 키를 사용할 수 있음
        all_props = db_spec.get("properties") or db_spec.get("db_properties") or {}
        deferred_prop_names: set[str] = set()
        filtered_props = {}
        for k, v in all_props.items():
            if isinstance(v, dict) and v.get("type") in ("relation", "rollup"):
                deferred_prop_names.add(k)
                continue
            if isinstance(v, dict) and v.get("type") == "formula":
                deferred_prop_names.add(k)
                continue
            if isinstance(v, dict) and "target_db_index" in v:
                deferred_prop_names.add(k)
                continue
            if v == "relation" or v == "rollup" or v == "formula":
                deferred_prop_names.add(k)
                continue
            filtered_props[k] = v
        properties = build_database_properties(filtered_props)
        db = await self.client.create_database(
            parent_id=parent_id,
            title=db_spec["title"],
            properties=properties,
            is_inline=db_spec.get("is_inline", True),
            description=db_spec.get("description", ""),
            icon=db_spec.get("icon"),
            cover_url=db_spec.get("cover_url"),
        )

        db_id = db["id"]

        # status 속성 한국어 옵션으로 업데이트
        await self._localize_status_options(db_id, filtered_props)

        # 샘플 데이터 추가 (relation/rollup/formula 속성은 제거 — DB에 아직 없으므로)
        if "sample_items" in db_spec and db_spec["sample_items"]:
            try:
                clean_items = []
                for item in db_spec["sample_items"]:
                    if not isinstance(item, dict):
                        continue
                    clean_item = {k: v for k, v in item.items() if k not in deferred_prop_names}
                    clean_items.append(clean_item)
                sample_result = await self.add_items_tool.execute(
                    database_id=db_id,
                    items=clean_items,
                    db_properties=filtered_props,
                )
                inserted = sample_result.get("item_count", 0)
                total = len(db_spec["sample_items"])
                if inserted < total:
                    logger.info(f"[샘플 데이터] {inserted}/{total}개만 성공")
                else:
                    logger.info(f"[샘플 데이터] {inserted}개 전부 성공")
            except Exception as e:
                logger.info(f"[샘플 데이터 실패] {str(e)[:120]}")

        # 뷰 자동 생성 (Views API — group_by, quick_filters, configuration 포함)
        # property name → ID 매핑 (calendar/timeline의 date_property_id 변환에 필요)
        prop_name_to_id = {}
        try:
            db_info = await self.client.get_database(db_id)
            for pname, pdata in db_info.get("properties", {}).items():
                prop_name_to_id[pname] = pdata.get("id", "")
        except Exception:
            pass

        views = db_spec.get("views", [])
        for view in views:
            view_spec = view if isinstance(view, dict) else {"type": view}
            # date_property 이름을 ID로 변환
            for key in ("date_property", "date_property_id"):
                dp = view_spec.get(key)
                if dp and dp in prop_name_to_id:
                    view_spec[key] = prop_name_to_id[dp]
            try:
                configuration = build_view_configuration(view_spec)
                await self.client.create_view(
                    database_id=db_id,
                    view_type=view_spec.get("type", "table"),
                    title=view_spec.get("title", ""),
                    filters=view_spec.get("filters"),
                    sorts=view_spec.get("sorts"),
                    group_by=view_spec.get("group_by"),
                    sub_group_by=view_spec.get("sub_group_by"),
                    quick_filters=view_spec.get("quick_filters"),
                    properties=view_spec.get("properties"),
                    configuration=configuration,
                )
            except Exception as e:
                logger.info(f"[뷰 생성 스킵] {view.get('type', '?') if isinstance(view, dict) else view}: {str(e)[:80]}")

        return {"id": db_id, "title": db_spec["title"], "views": len(views)}

    # ── Status 속성 한국어화 ────────────────────────────────────

    async def _localize_status_options(self, db_id: str, properties: dict) -> None:
        """status 속성의 기본 영어 옵션을 한국어로 변경"""
        status_keys = [
            k for k, v in properties.items()
            if v == "status" or (isinstance(v, dict) and v.get("type") == "status")
        ]
        if not status_keys:
            return

        try:
            db_info = await self.client.get_database(db_id)
            for key in status_keys:
                prop_data = db_info.get("properties", {}).get(key)
                if not prop_data or prop_data.get("type") != "status":
                    continue

                groups = prop_data.get("status", {}).get("groups", [])
                new_options = []
                rename_map = {
                    "Not started": "시작 전",
                    "In progress": "진행 중",
                    "Done": "완료",
                }
                for group in groups:
                    for opt in group.get("option_ids", []):
                        pass
                    for opt in group.get("options", []):
                        old_name = opt.get("name", "")
                        if old_name in rename_map:
                            new_options.append({
                                "id": opt["id"],
                                "name": rename_map[old_name],
                                "color": opt.get("color", "default"),
                            })

                if new_options:
                    await self.client.update_database(db_id, {
                        "properties": {
                            key: {
                                "status": {
                                    "options": new_options,
                                }
                            }
                        }
                    })
                    logger.info(f"[Status 한국어화] {key}: {[o['name'] for o in new_options]}")
        except Exception as e:
            logger.info(f"[Status 한국어화 스킵] {str(e)[:100]}")

    # ── 칼럼 블록 빌드 ──────────────────────────────────────────

    async def build_column_with_db(self, block: dict, page_id: str, sub_page_map: dict, result: dict) -> dict | None:
        """칼럼 블록 생성"""
        from app.notion import block_builder as bb

        columns_data = block.get("columns", [])
        col_blocks = []

        for col in columns_data:
            col_children = []
            # AI가 columns를 두 가지 형태로 생성할 수 있음:
            # 형식 A: {"blocks": [...]}  (dict)
            # 형식 B: [block1, block2, ...]  (list — 바로 블록 배열)
            if isinstance(col, list):
                col_items = col
            elif isinstance(col, dict):
                col_items = col.get("blocks", [])
            else:
                continue
            for b in col_items:
                if b.get("type") == "database_ref":
                    # AI가 column 안에 database_ref를 넣은 경우 (프롬프트 규칙 위반)
                    # Notion API 제한으로 column 안에 inline DB 삽입 불가
                    # DB는 column 밖에서 별도 생성됨 → 안내 표시
                    db_idx = b.get("db_index", 0)
                    created_dbs = result.get("databases", [])
                    if db_idx < len(created_dbs):
                        db_title = created_dbs[db_idx].get("title", "데이터베이스")
                        col_children.append(bb.callout(f"📊 {db_title}", icon="📊"))
                    else:
                        col_children.append(bb.callout("📊 데이터베이스", icon="📊"))
                elif b.get("type") == "bulleted_list" and any(name in b.get("text", "") for name in sub_page_map):
                    matched = False
                    for name, pid in sub_page_map.items():
                        if name in b.get("text", ""):
                            col_children.append(bb.link_to_page(pid))
                            matched = True
                            break
                    if not matched:
                        col_children.append(spec_to_block(b))
                else:
                    try:
                        col_children.append(spec_to_block(b))
                    except Exception:
                        pass
            col_blocks.append(col_children)

        # Apply width_ratios if AI specified them (e.g., [0.3, 0.7] for dashboard layout)
        width_ratios = block.get("width_ratios")
        return bb.column_list(col_blocks, width_ratios=width_ratios) if col_blocks else None

    # ── 칼럼 내 DB 참조 수집 ────────────────────────────────────

    def collect_db_refs_in_columns(self, block: dict) -> list[int]:
        refs = []
        for col in block.get("columns", []):
            col_items = col if isinstance(col, list) else col.get("blocks", []) if isinstance(col, dict) else []
            for b in col_items:
                if b.get("type") == "database_ref":
                    refs.append(len(refs))
        return refs

    # ── 하위 페이지 블록 채우기 ────────────────────────────────

    async def fill_sub_pages(self, blueprint: dict, sub_page_map: dict[str, str], result: dict) -> None:
        """하위 페이지에 블록 내용 채우기"""
        from app.notion import block_builder as bb

        for sub in blueprint.get("sub_pages", []):
            sub_id = sub_page_map.get(sub["title"])
            if not sub_id:
                continue
            sub_blocks = sub.get("blocks", [])
            if sub_blocks:
                try:
                    notion_blocks = [spec_to_block(b) for b in sub_blocks if isinstance(b, dict) and b.get("type") != "database_ref"]
                    if notion_blocks:
                        await self.client.add_blocks(sub_id, notion_blocks)
                except Exception as e:
                    logger.info(f"[하위 페이지 블록 스킵] {sub['title']}: {str(e)[:80]}")
            else:
                color = blueprint.get("metadata", {}).get("color_theme", "blue")
                bg = f"{color}_background" if color != "default" else "default"
                desc = sub.get("description", f"{sub['title']} 페이지입니다.")
                default_blocks = [
                    bb.callout(desc, icon=sub.get("icon", "📄"), color=bg),
                    bb.divider(),
                    bb.heading(f"📋 {sub['title']} 개요", level=2, color=color),
                    bb.paragraph("이 페이지의 내용을 자유롭게 작성해보세요."),
                    bb.paragraph(""),
                    bb.toggle("📖 활용 팁", children=[
                        bb.paragraph(f"• {sub['title']}에 관련된 정보를 정리해보세요"),
                        bb.paragraph("• 필요한 내용을 자유롭게 추가하고 수정하세요"),
                    ]),
                ]
                try:
                    await self.client.add_blocks(sub_id, default_blocks)
                except Exception as e:
                    logger.info(f"[하위 페이지 기본 블록 실패] {sub['title']}: {str(e)[:80]}")

    # ── Relation / Rollup / Formula 후처리 ──────────────────────

    async def post_process_relations(self, blueprint: dict, result: dict) -> None:
        """DB 생성 후 relation/rollup/formula 속성 후처리 — target_db_index → 실제 DB ID 매핑"""
        created_dbs = result.get("databases", [])
        if len(created_dbs) < 2:
            return  # relation은 최소 2개 DB 필요

        databases = blueprint.get("databases", [])
        for i, db_spec in enumerate(databases):
            if i >= len(created_dbs):
                break
            db_id = created_dbs[i]["id"]
            props = db_spec.get("properties", db_spec.get("db_properties", {}))

            relation_props: dict[str, Any] = {}
            for prop_name, prop_spec in props.items():
                if not isinstance(prop_spec, dict):
                    continue

                prop_type = prop_spec.get("type", "")

                # relation: target_db_index → 실제 database_id
                if prop_type == "relation" and "target_db_index" in prop_spec:
                    target_idx = prop_spec["target_db_index"]
                    if target_idx < len(created_dbs):
                        target_db_id = created_dbs[target_idx]["id"]
                        relation_props[prop_name] = {
                            "relation": {
                                "database_id": target_db_id,
                                "single_property": {},
                            }
                        }

                # formula: expression 그대로
                elif prop_type == "formula" and "expression" in prop_spec:
                    relation_props[prop_name] = {
                        "formula": {"expression": prop_spec["expression"]}
                    }

                # rollup: relation_property + target_property + function
                elif prop_type == "rollup" and "relation_property" in prop_spec:
                    relation_props[prop_name] = {
                        "rollup": {
                            "relation_property_name": prop_spec["relation_property"],
                            "rollup_property_name": prop_spec.get("target_property", "이름"),
                            "function": prop_spec.get("function", "count"),
                        }
                    }

            if relation_props:
                try:
                    await self.client.update_database(db_id, {"properties": relation_props})
                    logger.info(f"[Relation 후처리] {created_dbs[i]['title']}: {list(relation_props.keys())}")
                except Exception as e:
                    logger.info(f"[Relation 후처리 실패] {created_dbs[i]['title']}: {str(e)[:100]}")

    # ── 생성 후 검증 ────────────────────────────────────────────

    async def validate_creation(self, page_id: str, blueprint: dict, result: dict) -> list[str]:
        """생성 후 검증: 실제 Notion 페이지를 읽어서 기대값과 비교"""
        issues: list[str] = []
        try:
            children = await self.client.get_block_children(page_id)
            actual_blocks = len(children.get("results", []))
            expected_blocks = len(blueprint.get("blocks", []))

            # 블록 수 검증 (±50% 이내)
            if expected_blocks > 0 and actual_blocks < expected_blocks * 0.5:
                issues.append(f"블록 수 부족: 기대 {expected_blocks}개, 실제 {actual_blocks}개")

            # DB 수 검증
            expected_dbs = len(blueprint.get("databases", []))
            actual_dbs = len(result.get("databases", []))
            if actual_dbs < expected_dbs:
                issues.append(f"DB 수 부족: 기대 {expected_dbs}개, 실제 {actual_dbs}개")

            # 서브페이지 수 검증
            expected_subs = len(blueprint.get("sub_pages", []))
            actual_subs = len([p for p in result.get("pages", []) if p.get("id") != page_id])
            if actual_subs < expected_subs:
                issues.append(f"서브페이지 부족: 기대 {expected_subs}개, 실제 {actual_subs}개")

        except Exception as e:
            logger.info(f"[Post-Creation Validation 스킵] {str(e)[:80]}")

        return issues

    # ── link_to_page 동적 주입 (서브페이지 참조 치환) ────────────

    @staticmethod
    def resolve_sub_page_refs(blocks: list[dict], sub_page_map: dict[str, str]) -> None:
        """블록 트리를 순회하면서 sub_page_ref → 실제 page_id로 치환

        AI가 {"type": "link_to_page", "sub_page_ref": "가이드"} 형태로 생성하면,
        서브페이지 생성 후 실제 ID로 치환하여 link_to_page 블록이 정상 동작하게 함.
        """
        for block in blocks:
            if not isinstance(block, dict):
                continue
            # link_to_page with sub_page_ref 치환
            if block.get("type") == "link_to_page" and block.get("sub_page_ref"):
                ref_name = block["sub_page_ref"]
                # 정확한 매칭 시도
                page_id = sub_page_map.get(ref_name)
                # 부분 매칭 시도 (AI가 약간 다른 이름을 쓸 수 있음)
                if not page_id:
                    for title, pid in sub_page_map.items():
                        if ref_name in title or title in ref_name:
                            page_id = pid
                            break
                if page_id:
                    block["page_id"] = page_id
                    block.pop("sub_page_ref", None)

            # children 재귀 처리
            children = block.get("children", [])
            if children:
                CreationExecutor.resolve_sub_page_refs(children, sub_page_map)

            # column_list의 columns 처리
            if block.get("type") == "column_list":
                for col in block.get("columns", []):
                    if isinstance(col, list):
                        CreationExecutor.resolve_sub_page_refs(col, sub_page_map)

    # ── Blueprint 전체 실행 (스트리밍) ──────────────────────────

    async def execute_streaming(
        self, blueprint: dict, parent_page_id: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Blueprint 스트리밍 실행 — 진행 이벤트를 yield, 최종 "result" 이벤트로 결과 반환.

        yield 되는 이벤트 타입:
        - {"type": "progress", ...}: 진행 상황
        - {"type": "error", ...}: 에러 (조기 종료 시)
        - {"type": "result", "result": dict}: 최종 결과 (항상 마지막에 yield)
        """
        yield {"type": "progress", "step": "creating", "message": "🏗️ 노션에 생성을 시작합니다..."}

        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}
        main = blueprint["main_page"]

        # 1. 메인 페이지 생성
        yield {"type": "progress", "step": "page", "message": f"📄 페이지 생성 중: {main.get('icon', '')} {main['title']}"}
        try:
            page = await self.client.create_page(
                parent_id=parent_page_id,
                title=main["title"],
                icon=main.get("icon"),
                cover_url=main.get("cover_url"),
            )
            main_page_id = page["id"]
            result["pages"].append({"id": main_page_id, "title": main["title"], "url": page.get("url", "")})
            result["main_url"] = page.get("url", "")
            yield {"type": "progress", "step": "page_done", "message": f"✅ 페이지 생성됨: {main.get('icon', '')} {main['title']}"}
        except Exception as e:
            yield {"type": "error", "content": f"메인 페이지 생성 실패: {str(e)[:200]}"}
            yield {"type": "result", "result": result}
            return

        # 2. 하위 페이지 먼저 생성
        sub_page_map: dict[str, str] = {}
        for sub in blueprint.get("sub_pages", []):
            yield {"type": "progress", "step": "sub_page", "message": f"📁 하위 페이지: {sub.get('icon', '')} {sub['title']}"}
            try:
                sub_page = await self.client.create_page(
                    parent_id=main_page_id,
                    title=sub["title"],
                    icon=sub.get("icon"),
                    cover_url=sub.get("cover_url") or main.get("cover_url"),
                    position="page_end",
                )
                sub_page_map[sub["title"]] = sub_page["id"]
                result["pages"].append({"id": sub_page["id"], "title": sub["title"]})
            except Exception as e:
                yield {"type": "progress", "step": "warning", "message": f"⚠️ {sub['title']} 스킵: {str(e)[:50]}"}

        # 2.5. sub_page_ref 치환
        CreationExecutor.resolve_sub_page_refs(blueprint.get("blocks", []), sub_page_map)
        for sub in blueprint.get("sub_pages", []):
            CreationExecutor.resolve_sub_page_refs(sub.get("blocks", []), sub_page_map)

        # 3. 블록 + DB를 순서대로 삽입
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        pending_regular: list[dict] = []

        async def _flush_pending():
            nonlocal pending_regular
            if not pending_regular:
                return
            notion_blocks = [spec_to_block(b) for b in pending_regular]
            try:
                await self.client.add_blocks(main_page_id, notion_blocks)
                result["blocks"] += len(notion_blocks)
            except Exception as e:
                logger.info(f"[블록 배치 추가 실패] {len(notion_blocks)}개: {str(e)[:80]}")
            pending_regular = []

        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "?")
            try:
                if block_type == "database_ref":
                    await _flush_pending()
                    if db_index < len(databases):
                        db_spec = databases[db_index]
                        db_title = db_spec.get("title", db_spec.get("db_name", "DB"))
                        db_parent_name = db_spec.get("db_parent", "")
                        db_parent_id = sub_page_map.get(db_parent_name, main_page_id) if db_parent_name else main_page_id
                        yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title}"}
                        try:
                            db_result = await self.create_database_with_data(parent_id=db_parent_id, db_spec=db_spec)
                            result["databases"].append(db_result)
                            yield {"type": "progress", "step": "db_created", "message": f"✅ {db_title} DB 생성됨"}
                        except Exception as e:
                            yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:50]}"}
                        db_index += 1

                elif block_type == "column_list":
                    await _flush_pending()
                    yield {"type": "progress", "step": "block", "message": "🔲 칼럼 레이아웃 생성 중..."}
                    for _ in self.collect_db_refs_in_columns(block):
                        if db_index < len(databases):
                            db_spec = databases[db_index]
                            try:
                                db_result = await self.create_database_with_data(parent_id=main_page_id, db_spec=db_spec)
                                result["databases"].append(db_result)
                            except Exception as e:
                                yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:80]}"}
                            db_index += 1
                    column_block = await self.build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            logger.info(f"[칼럼 블록 추가 실패] {str(e)[:100]}")
                    yield {"type": "progress", "step": "block_done", "message": "✅ 칼럼 레이아웃 생성됨"}

                elif block_type == "linked_view":
                    await _flush_pending()
                    linked_db_idx = block.get("db_index", 0)
                    created_dbs = result.get("databases", [])
                    if linked_db_idx < len(created_dbs):
                        db_id = created_dbs[linked_db_idx].get("id", "")
                        if db_id:
                            try:
                                await self.client.create_linked_view(
                                    source_database_id=db_id, target_page_id=main_page_id,
                                    view_type=block.get("view_type", "table"),
                                    title=block.get("title", ""), filters=block.get("filter"),
                                )
                                result["blocks"] += 1
                            except Exception as e:
                                logger.info(f"[링크드 뷰 스킵] {str(e)[:80]}")

                else:
                    pending_regular.append(block)

            except Exception as e:
                logger.info(f"[블록 처리 오류] {block_type}: {str(e)[:80]}")

        await _flush_pending()

        # 남은 DB 추가
        while db_index < len(databases):
            try:
                db_result = await self.create_database_with_data(parent_id=main_page_id, db_spec=databases[db_index])
                result["databases"].append(db_result)
            except Exception:
                pass
            db_index += 1

        # 4. 하위 페이지 블록
        await self.fill_sub_pages(blueprint, sub_page_map, result)

        # 5. Relation/Rollup/Formula 후처리
        await self.post_process_relations(blueprint, result)
        relation_count = sum(
            1 for db in databases
            for _, v in db.get("properties", db.get("db_properties", {})).items()
            if isinstance(v, dict) and (v.get("type") in ("relation", "rollup", "formula") or "target_db_index" in v)
        )
        if relation_count > 0:
            yield {"type": "progress", "step": "relations", "message": f"🔗 DB 간 연결 완료 ({relation_count}개)"}

        # 6. 검증
        validation_issues = await self.validate_creation(main_page_id, blueprint, result)
        if validation_issues:
            yield {"type": "progress", "step": "validation", "message": f"🔍 검증: {len(validation_issues)}개 항목 확인"}
        else:
            yield {"type": "progress", "step": "validation", "message": "✅ 생성 결과 검증 완료 — 모든 항목 정상"}

        # 최종 결과 이벤트
        yield {"type": "result", "result": result}

    # ── Blueprint 전체 실행 (논스트리밍 편의 래퍼) ──────────────

    async def execute_blueprint(self, blueprint: dict, parent_page_id: str) -> dict[str, Any]:
        """Blueprint 논스트리밍 실행 — execute_streaming을 소비하여 최종 결과만 반환."""
        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}
        async for event in self.execute_streaming(blueprint, parent_page_id):
            if event.get("type") == "result":
                result = event["result"]
        return result

    # ── 롤백 (실패 시 정리) ─────────────────────────────────────

    async def rollback(self, result: dict[str, Any]) -> list[str]:
        """생성 실패 시 롤백 — 생성된 페이지들을 아카이브(삭제) 처리"""
        rolled_back: list[str] = []
        # 페이지를 역순으로 삭제 (하위 → 메인)
        for page in reversed(result.get("pages", [])):
            page_id = page.get("id")
            if not page_id:
                continue
            try:
                await self.client.archive_page(page_id)
                rolled_back.append(page.get("title", page_id))
            except Exception as e:
                logger.warning(f"[Rollback 실패] {page.get('title', '?')}: {str(e)[:80]}")
        return rolled_back
