"""CreationExecutor: Blueprint 실행 로직 (DB 생성, 블록 배치, 후처리, 검증, 롤백)

orchestrator.py에서 분리된 생성 실행 전담 클래스.
스트리밍/논스트리밍 두 인터페이스를 제공:
- execute_streaming(): AsyncGenerator — 진행 이벤트를 yield, 최종 결과는 "result" 이벤트로 반환
- execute_blueprint(): 논스트리밍 편의 래퍼 — 결과 dict만 반환
"""

import asyncio
import logging
from typing import Any, AsyncGenerator

from app.agent.tools.add_blocks import spec_to_block
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.agent.view_builder import build_view_configuration
from app.notion.block_builder import build_database_properties
from app.notion.client import NotionClient

logger = logging.getLogger("notionforge.creation_executor")

NOTION_RETRY_MAX = 2
NOTION_RETRY_BACKOFF = 0.5


def _is_notion_retryable(error: Exception) -> bool:
    msg = str(error).lower()
    retryable = ("rate_limit", "429", "502", "503", "504", "timeout", "connection")
    return any(kw in msg for kw in retryable)


async def _retry_notion(coro_fn, *args, max_retries: int = NOTION_RETRY_MAX, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return await coro_fn(*args, **kwargs)
        except Exception as e:
            if not _is_notion_retryable(e) or attempt == max_retries:
                raise
            wait = NOTION_RETRY_BACKOFF * (2**attempt)
            logger.info(f"[Notion Retry] {attempt + 1}/{max_retries} — {wait}s 후 재시도: {str(e)[:60]}")
            await asyncio.sleep(wait)


def _subpage_title(sub: dict) -> str:
    """서브페이지 제목 통일 — recipe/golden은 'name', AI/스키마는 'title' 키 사용."""
    return sub.get("title") or sub.get("name") or "페이지"


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
        sample_items = db_spec.get("sample_items") or []
        if sample_items:
            clean_items = []
            for item in sample_items:
                if not isinstance(item, dict):
                    continue
                clean_item = {k: v for k, v in item.items() if k not in deferred_prop_names}
                clean_items.append(clean_item)

            if clean_items:
                try:
                    sample_result = await self.add_items_tool.execute(
                        database_id=db_id,
                        items=clean_items,
                        db_properties=filtered_props,
                    )
                    inserted = sample_result.get("item_count", 0)
                    total = len(clean_items)
                    if inserted == 0:
                        logger.warning(
                            f"[샘플 데이터] {db_spec.get('title', 'DB')} — 0/{total}개 성공. "
                            f"blueprint 속성: {list(filtered_props.keys())}, "
                            f"샘플 키: {list(clean_items[0].keys()) if clean_items else []}"
                        )
                    elif inserted < total:
                        logger.info(f"[샘플 데이터] {inserted}/{total}개만 성공")
                    else:
                        logger.info(f"[샘플 데이터] {inserted}개 전부 성공")
                except Exception as e:
                    logger.warning(f"[샘플 데이터 실패] {db_spec.get('title', 'DB')}: {str(e)[:200]}")

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
        view_specs = []
        for view in views:
            vs = view if isinstance(view, dict) else {"type": view}
            for key in ("date_property", "date_property_id"):
                dp = vs.get(key)
                if dp and dp in prop_name_to_id:
                    vs[key] = prop_name_to_id[dp]
            view_specs.append(vs)

        async def _create_single_view(vs: dict) -> None:
            configuration = build_view_configuration(vs)
            await self.client.create_view(
                database_id=db_id,
                view_type=vs.get("type", "table"),
                title=vs.get("title", ""),
                filters=vs.get("filters"),
                sorts=vs.get("sorts"),
                group_by=vs.get("group_by"),
                sub_group_by=vs.get("sub_group_by"),
                quick_filters=vs.get("quick_filters"),
                properties=vs.get("properties"),
                configuration=configuration,
            )

        results = await asyncio.gather(
            *[_create_single_view(vs) for vs in view_specs],
            return_exceptions=True,
        )
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                vt = view_specs[i].get("type", "?") if i < len(view_specs) else "?"
                logger.info(f"[뷰 생성 스킵] {vt}: {str(r)[:80]}")

        return {"id": db_id, "title": db_spec["title"], "views": len(views)}

    # ── Status 속성 한국어화 ────────────────────────────────────

    async def _localize_status_options(self, db_id: str, properties: dict) -> None:
        """status 속성의 기본 영어 옵션을 한국어로 변경"""
        status_keys = [
            k for k, v in properties.items() if v == "status" or (isinstance(v, dict) and v.get("type") == "status")
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
                            new_options.append(
                                {
                                    "id": opt["id"],
                                    "name": rename_map[old_name],
                                    "color": opt.get("color", "default"),
                                }
                            )

                if new_options:
                    await self.client.update_database(
                        db_id,
                        {
                            "properties": {
                                key: {
                                    "status": {
                                        "options": new_options,
                                    }
                                }
                            }
                        },
                    )
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
        """하위 페이지에 블록 내용 병렬 채우기"""
        from app.notion import block_builder as bb

        async def _fill_single(sub: dict) -> None:
            sub_title = _subpage_title(sub)
            sub_id = sub_page_map.get(sub_title)
            if not sub_id:
                return
            sub_blocks = sub.get("blocks", [])
            if sub_blocks:
                notion_blocks = [
                    spec_to_block(b) for b in sub_blocks if isinstance(b, dict) and b.get("type") != "database_ref"
                ]
                if notion_blocks:
                    await self.client.add_blocks(sub_id, notion_blocks)
            else:
                color = blueprint.get("metadata", {}).get("color_theme", "blue")
                bg = f"{color}_background" if color != "default" else "default"
                desc = sub.get("description", f"{sub_title} 페이지입니다.")
                default_blocks = [
                    bb.callout(desc, icon=sub.get("icon", "📄"), color=bg),
                    bb.divider(),
                    bb.heading(f"📋 {sub_title} 개요", level=2, color=color),
                    bb.paragraph("이 페이지의 내용을 자유롭게 작성해보세요."),
                    bb.paragraph(""),
                    bb.toggle(
                        "📖 활용 팁",
                        children=[
                            bb.paragraph(f"• {sub_title}에 관련된 정보를 정리해보세요"),
                            bb.paragraph("• 필요한 내용을 자유롭게 추가하고 수정하세요"),
                        ],
                    ),
                ]
                await self.client.add_blocks(sub_id, default_blocks)

        subs = blueprint.get("sub_pages", [])
        fill_results = await asyncio.gather(*[_fill_single(s) for s in subs], return_exceptions=True)
        for i, r in enumerate(fill_results):
            if isinstance(r, Exception):
                logger.info(f"[하위 페이지 블록 스킵] {subs[i].get('title', '?')}: {str(r)[:80]}")

    # ── Relation / Rollup / Formula 후처리 ──────────────────────

    async def post_process_relations(self, blueprint: dict, result: dict) -> None:
        """DB 생성 후 relation/rollup/formula 속성 후처리 — target_db_index → 실제 DB ID 매핑.

        relation/rollup은 다중 DB가 필요하지만 formula는 단일 DB에서도 유효하므로,
        DB가 1개여도 formula는 반드시 생성한다(과거 <2 조기반환으로 단일 DB formula가 누락되던 버그).
        """
        created_dbs = result.get("databases", [])
        if not created_dbs:
            return

        databases = blueprint.get("databases", [])

        def _props_of(db_spec: dict) -> dict:
            return db_spec.get("properties", db_spec.get("db_properties", {}))

        # 선언된 relation 수집: db_index -> {prop_name: target_idx}
        rel_decls: dict[int, dict[str, int]] = {}
        for i, db_spec in enumerate(databases):
            if i >= len(created_dbs):
                continue
            for name, spec in _props_of(db_spec).items():
                if isinstance(spec, dict) and spec.get("type") == "relation" and "target_db_index" in spec:
                    ti = spec["target_db_index"]
                    if 0 <= ti < len(created_dbs):
                        rel_decls.setdefault(i, {})[name] = ti

        # 양방향 쌍 탐지 (DATA-1): i.name_i→j 와 j.name_j→i 가 모두 선언되면
        # dual_property 로 1개만 생성(반대쪽은 Notion이 synced 속성으로 자동 생성) → rollup 집계 가능
        dual_make: set[tuple[int, str]] = set()
        dual_skip: set[tuple[int, str]] = set()
        for i, props_i in rel_decls.items():
            for name_i, j in props_i.items():
                if i == j or (i, name_i) in dual_skip or (i, name_i) in dual_make:
                    continue
                back = next(
                    (nj for nj, tj in rel_decls.get(j, {}).items() if tj == i and (j, nj) not in dual_skip),
                    None,
                )
                if back is not None:
                    dual_make.add((i, name_i))
                    dual_skip.add((j, back))

        # ── Pass 1: relation 생성 (rollup이 참조할 relation이 존재하도록) ──
        for i, db_spec in enumerate(databases):
            if i >= len(created_dbs):
                break
            relation_props: dict[str, Any] = {}
            for prop_name, prop_spec in _props_of(db_spec).items():
                if not isinstance(prop_spec, dict):
                    continue
                if prop_spec.get("type") == "relation" and "target_db_index" in prop_spec:
                    target_idx = prop_spec["target_db_index"]
                    if not (0 <= target_idx < len(created_dbs)):
                        continue
                    if (i, prop_name) in dual_skip:
                        continue  # 양방향 쌍의 synced 측 — dual 생성 시 자동 생성됨
                    cfg: dict[str, Any] = {"database_id": created_dbs[target_idx]["id"]}
                    if (i, prop_name) in dual_make:
                        cfg["type"] = "dual_property"
                        cfg["dual_property"] = {}
                    else:
                        cfg["single_property"] = {}
                    relation_props[prop_name] = {"relation": cfg}
            if relation_props:
                try:
                    await self.client.update_database(created_dbs[i]["id"], {"properties": relation_props})
                    logger.info(f"[Relation 후처리] {created_dbs[i]['title']}: {list(relation_props.keys())}")
                except Exception as e:
                    logger.info(f"[Relation 후처리 실패] {created_dbs[i]['title']}: {str(e)[:100]}")

        # ── Pass 2: rollup / formula (relation이 존재한 뒤에 추가) ──
        for i, db_spec in enumerate(databases):
            if i >= len(created_dbs):
                break
            derived_props: dict[str, Any] = {}
            for prop_name, prop_spec in _props_of(db_spec).items():
                if not isinstance(prop_spec, dict):
                    continue
                prop_type = prop_spec.get("type", "")
                if prop_type == "formula" and "expression" in prop_spec:
                    derived_props[prop_name] = {"formula": {"expression": prop_spec["expression"]}}
                elif prop_type == "rollup" and "relation_property" in prop_spec:
                    derived_props[prop_name] = {
                        "rollup": {
                            "relation_property_name": prop_spec["relation_property"],
                            "rollup_property_name": prop_spec.get("target_property", "이름"),
                            "function": prop_spec.get("function", "count"),
                        }
                    }
            if derived_props:
                try:
                    await self.client.update_database(created_dbs[i]["id"], {"properties": derived_props})
                    logger.info(f"[Rollup/Formula 후처리] {created_dbs[i]['title']}: {list(derived_props.keys())}")
                except Exception as e:
                    logger.info(f"[Rollup/Formula 후처리 실패] {created_dbs[i]['title']}: {str(e)[:100]}")

    @staticmethod
    def _title_key(props: dict) -> str:
        for name, spec in props.items():
            if spec == "title" or (isinstance(spec, dict) and spec.get("type") == "title"):
                return name
        return ""

    @staticmethod
    def _row_title(row: dict) -> str:
        for prop in row.get("properties", {}).values():
            if prop.get("type") == "title":
                return "".join(rt.get("plain_text", "") for rt in prop.get("title", []))
        return ""

    async def post_process_sample_links(self, blueprint: dict, result: dict) -> None:
        """샘플 아이템 간 relation 연결 — rollup이 실제 값을 집계하도록 시연용 링크.

        db_spec의 sample_item에 relation 속성값(대상 DB 아이템 제목 또는 제목 리스트)이 있으면
        생성된 해당 페이지에 relation을 설정한다. dual_property로 생성된 측 속성에 설정하면
        양방향 동기화되어 rollup이 집계된다.
        """
        created_dbs = result.get("databases", [])
        if len(created_dbs) < 2:
            return
        databases = blueprint.get("databases", [])

        def _props_of(db_spec: dict) -> dict:
            return db_spec.get("properties", db_spec.get("db_properties", {}))

        # 각 DB의 title → page_id 맵 (생성된 샘플 조회 — 순서/실패 무관하게 안정적)
        item_maps: list[dict[str, str]] = []
        for db in created_dbs:
            m: dict[str, str] = {}
            try:
                for row in await self.client.query_database(db["id"]):
                    t = self._row_title(row)
                    if t:
                        m[t] = row["id"]
            except Exception:
                pass
            item_maps.append(m)

        for i, db_spec in enumerate(databases):
            if i >= len(created_dbs):
                break
            props = _props_of(db_spec)
            rel_props = {
                n: s
                for n, s in props.items()
                if isinstance(s, dict) and s.get("type") == "relation" and "target_db_index" in s
            }
            if not rel_props:
                continue
            title_key = self._title_key(props)
            if not title_key:
                continue
            for item in db_spec.get("sample_items", []):
                if not isinstance(item, dict):
                    continue
                src_id = item_maps[i].get(str(item.get(title_key, "")))
                if not src_id:
                    continue
                update_props: dict[str, Any] = {}
                for rel_name, rel_spec in rel_props.items():
                    if rel_name not in item:
                        continue
                    tgt_idx = rel_spec["target_db_index"]
                    if not (0 <= tgt_idx < len(item_maps)):
                        continue
                    vals = item[rel_name] if isinstance(item[rel_name], list) else [item[rel_name]]
                    rel_ids = [{"id": item_maps[tgt_idx][str(v)]} for v in vals if str(v) in item_maps[tgt_idx]]
                    if rel_ids:
                        update_props[rel_name] = {"relation": rel_ids}
                if update_props:
                    try:
                        await self.client.update_page(src_id, properties=update_props)
                    except Exception as e:
                        logger.info(f"[샘플 링크 실패] {str(e)[:80]}")

    # ── Pre-creation 검증 (API 호출 전) ──────────────────────────

    @staticmethod
    def validate_blueprint_integrity(blueprint: dict) -> list[str]:
        """Blueprint 무결성 사전 검증 — Notion API 호출 전 구조적 문제를 조기 발견"""
        issues: list[str] = []
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        sub_pages = blueprint.get("sub_pages", [])
        db_count = len(databases)

        if not blueprint.get("main_page", {}).get("title"):
            issues.append("main_page.title이 비어있습니다.")

        # db_index 범위 검증
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "database_ref":
                idx = block.get("db_index", 0)
                if idx >= db_count:
                    issues.append(f"blocks[{i}]: db_index={idx}가 databases({db_count}개) 범위 밖입니다.")
            if block.get("type") == "linked_view":
                idx = block.get("db_index", 0)
                if idx >= db_count:
                    issues.append(f"blocks[{i}]: linked_view db_index={idx}가 범위 밖입니다.")

        # Relation 그래프 검증
        for di, db in enumerate(databases):
            props = db.get("properties", db.get("db_properties", {}))
            for pname, pspec in props.items():
                if not isinstance(pspec, dict):
                    continue
                if pspec.get("type") == "relation":
                    target = pspec.get("target_db_index")
                    if target is not None:
                        if not isinstance(target, int) or target < 0 or target >= db_count:
                            issues.append(f"DB[{di}].{pname}: relation target_db_index={target} 범위 밖")
                        elif target == di:
                            issues.append(f"DB[{di}].{pname}: 자기참조 relation")
                if pspec.get("type") == "rollup":
                    rel_prop = pspec.get("relation_property", "")
                    if rel_prop and rel_prop not in props:
                        issues.append(f"DB[{di}].{pname}: rollup의 relation_property '{rel_prop}'가 DB에 없음")

        # DB 속성에 title 타입 존재 확인
        for di, db in enumerate(databases):
            props = db.get("properties", db.get("db_properties", {}))
            has_title = any(v == "title" or (isinstance(v, dict) and v.get("type") == "title") for v in props.values())
            if not has_title and props:
                issues.append(f"DB[{di}]: title 타입 속성이 없습니다.")

        # db_parent 참조 검증
        sub_page_titles = {_subpage_title(s) for s in sub_pages}
        for di, db in enumerate(databases):
            db_parent = db.get("db_parent", "")
            if db_parent and db_parent not in sub_page_titles:
                issues.append(f"DB[{di}]: db_parent '{db_parent}'가 sub_pages에 없습니다.")

        return issues

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

    # ── Blueprint 자동 교정 ──────────────────────────────────────

    @staticmethod
    def _auto_fix_blueprint(blueprint: dict, issues: list[str]) -> dict:
        """Pre-creation 검증에서 발견된 문제를 자동 교정"""
        databases = blueprint.get("databases", [])
        blocks = blueprint.get("blocks", [])
        db_count = len(databases)

        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") in ("database_ref", "linked_view"):
                idx = block.get("db_index", 0)
                if idx >= db_count and db_count > 0:
                    block["db_index"] = 0

        for di, db in enumerate(databases):
            props = db.get("properties", db.get("db_properties", {}))
            keys_to_remove = []
            for pname, pspec in props.items():
                if not isinstance(pspec, dict):
                    continue
                if pspec.get("type") == "relation":
                    target = pspec.get("target_db_index")
                    if target is not None and (
                        not isinstance(target, int) or target < 0 or target >= db_count or target == di
                    ):
                        keys_to_remove.append(pname)
                if pspec.get("type") == "rollup":
                    rel_prop = pspec.get("relation_property", "")
                    if rel_prop and rel_prop not in props:
                        keys_to_remove.append(pname)
            for k in keys_to_remove:
                props.pop(k, None)

        return blueprint

    # ── Blueprint 전체 실행 (스트리밍) ──────────────────────────

    async def execute_streaming(
        self,
        blueprint: dict,
        parent_page_id: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Blueprint 스트리밍 실행 — 진행 이벤트를 yield, 최종 "result" 이벤트로 결과 반환.

        yield 되는 이벤트 타입:
        - {"type": "progress", ...}: 진행 상황
        - {"type": "error", ...}: 에러 (조기 종료 시)
        - {"type": "result", "result": dict}: 최종 결과 (항상 마지막에 yield)
        """
        yield {"type": "progress", "step": "creating", "message": "🏗️ 노션에 생성을 시작합니다..."}

        # 0. Pre-creation 무결성 검증
        integrity_issues = self.validate_blueprint_integrity(blueprint)
        if integrity_issues:
            logger.info(f"[Pre-creation 검증] {len(integrity_issues)}개 문제 발견, 자동 교정 시도")
            blueprint = self._auto_fix_blueprint(blueprint, integrity_issues)
            yield {
                "type": "progress",
                "step": "pre_validation",
                "message": f"🔍 사전 검증: {len(integrity_issues)}개 항목 자동 교정 완료",
            }

        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}
        main = blueprint["main_page"]

        # 1. 메인 페이지 생성
        yield {
            "type": "progress",
            "step": "page",
            "message": f"📄 페이지 생성 중: {main.get('icon', '')} {main['title']}",
        }
        try:
            page = await _retry_notion(
                self.client.create_page,
                parent_id=parent_page_id,
                title=main["title"],
                icon=main.get("icon"),
                cover_url=main.get("cover_url"),
            )
            main_page_id = page["id"]
            result["pages"].append({"id": main_page_id, "title": main["title"], "url": page.get("url", "")})
            result["main_url"] = page.get("url", "")
            yield {
                "type": "progress",
                "step": "page_done",
                "message": f"✅ 페이지 생성됨: {main.get('icon', '')} {main['title']}",
            }
        except Exception as e:
            yield {"type": "error", "content": f"메인 페이지 생성 실패: {str(e)[:200]}"}
            yield {"type": "result", "result": result}
            return

        # 2. 하위 페이지 병렬 생성
        sub_page_map: dict[str, str] = {}
        sub_pages = blueprint.get("sub_pages", [])
        if sub_pages:
            yield {
                "type": "progress",
                "step": "sub_page",
                "message": f"📁 하위 페이지 {len(sub_pages)}개 생성 중...",
            }

            async def _create_sub(sub: dict) -> tuple[str, dict | None, str]:
                sub_title = _subpage_title(sub)
                try:
                    page = await _retry_notion(
                        self.client.create_page,
                        parent_id=main_page_id,
                        title=sub_title,
                        icon=sub.get("icon"),
                        cover_url=sub.get("cover_url") or main.get("cover_url"),
                        position="page_end",
                    )
                    return sub_title, page, ""
                except Exception as e:
                    return sub_title, None, str(e)[:50]

            sub_results = await asyncio.gather(*[_create_sub(s) for s in sub_pages])
            for title, page, error in sub_results:
                if page:
                    sub_page_map[title] = page["id"]
                    result["pages"].append({"id": page["id"], "title": title})
                else:
                    yield {"type": "progress", "step": "warning", "message": f"⚠️ {title} 스킵: {error}"}

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
                        db_parent_id = (
                            sub_page_map.get(db_parent_name, main_page_id) if db_parent_name else main_page_id
                        )
                        yield {
                            "type": "progress",
                            "step": "database",
                            "message": f"📊 데이터베이스 생성 중: {db_title}",
                        }
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
                                db_result = await self.create_database_with_data(
                                    parent_id=main_page_id, db_spec=db_spec
                                )
                                result["databases"].append(db_result)
                            except Exception as e:
                                yield {
                                    "type": "progress",
                                    "step": "warning",
                                    "message": f"⚠️ DB 생성 스킵: {str(e)[:80]}",
                                }
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
                                    source_database_id=db_id,
                                    target_page_id=main_page_id,
                                    view_type=block.get("view_type", "table"),
                                    title=block.get("title", ""),
                                    filters=block.get("filter"),
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

        # 5.5 샘플 아이템 간 relation 링크 (rollup 실집계 시연)
        await self.post_process_sample_links(blueprint, result)
        relation_count = sum(
            1
            for db in databases
            for _, v in db.get("properties", db.get("db_properties", {})).items()
            if isinstance(v, dict) and (v.get("type") in ("relation", "rollup", "formula") or "target_db_index" in v)
        )
        if relation_count > 0:
            yield {"type": "progress", "step": "relations", "message": f"🔗 DB 간 연결 완료 ({relation_count}개)"}

        # 6. 검증
        validation_issues = await self.validate_creation(main_page_id, blueprint, result)
        if validation_issues:
            yield {
                "type": "progress",
                "step": "validation",
                "message": f"🔍 검증: {len(validation_issues)}개 항목 확인",
            }
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

    @staticmethod
    def summarize_partial_result(blueprint: dict, result: dict) -> dict[str, Any]:
        expected_dbs = len(blueprint.get("databases", []))
        expected_blocks = len(blueprint.get("blocks", []))
        expected_subs = len(blueprint.get("sub_pages", []))

        actual_dbs = len(result.get("databases", []))
        actual_blocks = result.get("blocks", 0)
        actual_pages = len(result.get("pages", []))
        actual_subs = max(0, actual_pages - 1)

        completion = 0.0
        total_expected = expected_dbs + expected_blocks + expected_subs
        total_actual = actual_dbs + actual_blocks + actual_subs
        if total_expected > 0:
            completion = round(total_actual / total_expected * 100, 1)

        return {
            "completion_pct": min(100.0, completion),
            "databases": {"expected": expected_dbs, "created": actual_dbs},
            "blocks": {"expected": expected_blocks, "created": actual_blocks},
            "sub_pages": {"expected": expected_subs, "created": actual_subs},
            "is_partial": completion < 100.0 and completion > 0.0,
        }
