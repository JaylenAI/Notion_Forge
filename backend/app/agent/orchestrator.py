"""Agent Orchestrator: 사용자 요청 -> 의도 분석 -> Blueprint -> Tool 실행 -> 결과"""

from typing import Any, AsyncGenerator

from app.agent.intent_analyzer import analyze_intent
from app.agent.blueprint_generator import generate_blueprint
from app.agent.tools.add_blocks import AddBlocksTool, spec_to_block
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.notion.client import NotionClient
from app.notion.block_builder import build_database_properties
from app.schemas.blueprint import IntentResult


class AgentOrchestrator:
    def __init__(self, notion_token: str = "", parent_page_id: str = ""):
        from app.config import settings

        self.client = NotionClient(
            token=notion_token or settings.notion_api_key,
            parent_page_id=parent_page_id or settings.notion_parent_page_id,
        )
        self.parent_page_id = parent_page_id or settings.notion_parent_page_id
        self.add_blocks_tool = AddBlocksTool(self.client)
        self.add_items_tool = AddDatabaseItemsTool(self.client)

    async def process(self, message: str) -> AsyncGenerator[dict[str, Any], None]:
        """메인 처리 파이프라인"""

        yield {"type": "progress", "step": "intent_analysis", "message": "요청을 분석하고 있어요..."}
        intent = await analyze_intent(message)

        if intent.confidence < 0.7 and intent.missing_info:
            yield {"type": "question", "content": self._build_question(intent), "intent": intent.model_dump()}
            return

        yield {"type": "progress", "step": "blueprint", "message": "템플릿 구조를 설계하고 있어요..."}
        blueprint = generate_blueprint(intent)

        yield {"type": "blueprint_preview", "content": self._format_preview(blueprint), "blueprint": blueprint}

        yield {"type": "progress", "step": "generating", "message": "노션에 생성 중..."}
        result = await self._execute_blueprint(blueprint)

        yield {"type": "complete", "content": self._format_complete(result), "result": result}

    async def _execute_blueprint(self, blueprint: dict) -> dict[str, Any]:
        """Blueprint 실행 -- 올바른 순서로 생성

        순서:
        1. 메인 페이지 (빈 페이지)
        2. 하위 페이지 (link_to_page에 필요)
        3. 블록을 순서대로 추가 -- database_ref를 만나면 해당 위치에 인라인 DB 생성
        4. 하위 페이지에 블록 추가
        """
        main = blueprint["main_page"]
        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}

        # ==============================
        # 1. 메인 페이지 생성 (빈 페이지)
        # ==============================
        try:
            page = await self.client.create_page(
                parent_id=self.parent_page_id,
                title=main["title"],
                icon=main.get("icon"),
                cover_url=main.get("cover_url"),
            )
        except Exception as e:
            raise RuntimeError(f"메인 페이지 생성 실패: {e}") from e

        main_page_id = page["id"]
        result["pages"].append({
            "id": main_page_id,
            "title": main["title"],
            "url": page.get("url", ""),
        })
        result["main_url"] = page.get("url", "")

        # ==============================
        # 2. 하위 페이지 먼저 생성 (link_to_page에 필요)
        # ==============================
        sub_page_map: dict[str, str] = {}  # title -> page_id
        for sub in blueprint.get("sub_pages", []):
            try:
                sub_page = await self.client.create_page(
                    parent_id=main_page_id,
                    title=sub["title"],
                    icon=sub.get("icon"),
                )
                sub_page_map[sub["title"]] = sub_page["id"]
                result["pages"].append({"id": sub_page["id"], "title": sub["title"]})
            except Exception as e:
                print(f"[하위 페이지 생성 스킵] {sub.get('title', '?')}: {str(e)[:100]}")

        # ==============================
        # 3. 블록 + DB를 순서대로 메인 페이지에 삽입
        # ==============================
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        for block in blocks:
            try:
                if block.get("type") == "database_ref":
                    # DB를 이 위치에 인라인으로 생성
                    if db_index < len(databases):
                        db_result = await self._create_database_with_data(
                            parent_id=main_page_id,
                            db_spec=databases[db_index],
                        )
                        result["databases"].append(db_result)
                        db_index += 1

                elif block.get("type") == "column_list":
                    # 칼럼 처리 -- 내부에 database_ref가 있으면 칼럼 앞에 DB 생성
                    db_refs_in_col = self._collect_db_refs_in_columns(block)
                    for _ in db_refs_in_col:
                        if db_index < len(databases):
                            try:
                                db_result = await self._create_database_with_data(
                                    parent_id=main_page_id,
                                    db_spec=databases[db_index],
                                )
                                result["databases"].append(db_result)
                            except Exception as e:
                                print(f"[칼럼 내 DB 스킵] {str(e)[:100]}")
                            db_index += 1

                    # 칼럼 블록 자체를 생성 (database_ref는 제거)
                    column_block = await self._build_column_with_db(
                        block, main_page_id, sub_page_map, result
                    )
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            print(f"[칼럼 블록 스킵] {str(e)[:100]}")

                elif block.get("type") == "link_to_page":
                    # link_to_page -- 하위 페이지 이름으로 실제 ID 매핑
                    page_title = block.get("page_title", "")
                    target_id = sub_page_map.get(page_title)
                    if target_id:
                        from app.notion import block_builder as bb
                        ltp = bb.link_to_page(target_id)
                        try:
                            await self.client.add_blocks(main_page_id, [ltp])
                            result["blocks"] += 1
                        except Exception as e:
                            print(f"[link_to_page 스킵] {str(e)[:100]}")
                    else:
                        # fallback: 일반 블록으로 처리
                        notion_block = spec_to_block(block)
                        try:
                            await self.client.add_blocks(main_page_id, [notion_block])
                            result["blocks"] += 1
                        except Exception as e:
                            print(f"[블록 스킵] {block.get('type', '?')}: {str(e)[:100]}")

                else:
                    # 일반 블록
                    notion_block = spec_to_block(block)
                    try:
                        await self.client.add_blocks(main_page_id, [notion_block])
                        result["blocks"] += 1
                    except Exception as e:
                        print(f"[블록 스킵] {block.get('type', '?')}: {str(e)[:100]}")

            except Exception as e:
                print(f"[블록 처리 오류] {block.get('type', '?')}: {str(e)[:100]}")

        # 아직 삽입 안 된 DB가 있으면 마지막에 추가
        while db_index < len(databases):
            try:
                db_result = await self._create_database_with_data(
                    parent_id=main_page_id,
                    db_spec=databases[db_index],
                )
                result["databases"].append(db_result)
            except Exception as e:
                print(f"[DB 생성 스킵] {str(e)[:100]}")
            db_index += 1

        # ==============================
        # 4. 하위 페이지에 블록 추가
        # ==============================
        for sub in blueprint.get("sub_pages", []):
            sub_id = sub_page_map.get(sub["title"])
            if sub_id and sub.get("blocks"):
                try:
                    notion_blocks = [
                        spec_to_block(b)
                        for b in sub["blocks"]
                        if b.get("type") != "database_ref"
                    ]
                    if notion_blocks:
                        await self.client.add_blocks(sub_id, notion_blocks)
                except Exception as e:
                    print(f"[하위 페이지 블록 스킵] {sub['title']}: {str(e)[:80]}")

        return result

    async def _create_database_with_data(self, parent_id: str, db_spec: dict) -> dict[str, Any]:
        """DB 생성 + 샘플 데이터 추가"""
        try:
            properties = build_database_properties(db_spec["properties"])
        except Exception as e:
            raise RuntimeError(f"DB 속성 빌드 실패 ({db_spec.get('title', '?')}): {e}") from e

        try:
            db = await self.client.create_database(
                parent_id=parent_id,
                title=db_spec["title"],
                properties=properties,
                is_inline=db_spec.get("is_inline", True),
            )
        except Exception as e:
            raise RuntimeError(f"DB 생성 API 실패 ({db_spec.get('title', '?')}): {e}") from e

        # 샘플 데이터 추가
        if "sample_items" in db_spec:
            try:
                await self.add_items_tool.execute(
                    database_id=db["id"],
                    items=db_spec["sample_items"],
                    db_properties=db_spec["properties"],
                )
            except Exception as e:
                print(f"[샘플 데이터 스킵] {str(e)[:80]}")

        return {"id": db["id"], "title": db_spec["title"]}

    async def _build_column_with_db(
        self, block: dict, page_id: str,
        sub_page_map: dict, result: dict,
    ) -> dict | None:
        """칼럼 블록 생성 -- database_ref는 제거하고, link_to_page는 실제 ID로 변환"""
        from app.notion import block_builder as bb

        columns_data = block.get("columns", [])
        col_blocks = []

        for col in columns_data:
            col_children = []
            for b in col.get("blocks", []):
                if b.get("type") == "database_ref":
                    # 칼럼 안에서는 DB를 직접 넣을 수 없음 -- 이미 앞에서 생성함
                    col_children.append(
                        bb.callout("위 데이터베이스를 확인하세요", icon="📊")
                    )
                elif b.get("type") == "bulleted_list" and any(
                    name in b.get("text", "") for name in sub_page_map
                ):
                    # 하위 페이지 이름이 포함된 bulleted_list -> link_to_page로 변환
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
                    except Exception as e:
                        print(f"[칼럼 내 블록 스킵] {b.get('type', '?')}: {str(e)[:80]}")
            col_blocks.append(col_children)

        if col_blocks:
            return bb.column_list(col_blocks)
        return None

    def _collect_db_refs_in_columns(self, block: dict) -> list[int]:
        """칼럼 내부의 database_ref 인덱스 목록 수집"""
        refs = []
        for col in block.get("columns", []):
            for b in col.get("blocks", []):
                if b.get("type") == "database_ref":
                    refs.append(len(refs))
        return refs

    def _build_question(self, intent: IntentResult) -> str:
        lines = intent.missing_info or ["어떤 용도의 노션 템플릿을 만들어드릴까요?"]
        categories = [
            "📊 프로젝트 관리 (대시보드, 칸반)",
            "✅ 습관/목표 트래커",
            "📚 학습/독서 기록",
            "🏢 업무용 (CRM, 회의록, 인수인계)",
            "🔖 북마크/자료 정리",
            "📝 일기/기록 노트",
        ]
        return "\n".join(f"- {q}" for q in lines) + "\n\n인기 카테고리:\n" + "\n".join(f"  {c}" for c in categories)

    def _format_preview(self, blueprint: dict) -> str:
        meta = blueprint["metadata"]
        lines = [f"📄 **{meta['title']}** ({meta['template_type']})", f"🎨 색상: {meta['color_theme']}"]
        for db in blueprint.get("databases", []):
            lines.append(f"📊 DB: {db['title']} ({', '.join(db['properties'].keys())})")
        for sub in blueprint.get("sub_pages", []):
            lines.append(f"📁 하위: {sub['title']}")
        return "\n".join(lines)

    def _format_complete(self, result: dict) -> str:
        lines = [
            "✅ 템플릿 생성 완료!",
            f"📄 페이지 {len(result['pages'])}개",
            f"📊 데이터베이스 {len(result['databases'])}개",
            f"🧱 블록 {result['blocks']}개",
        ]
        if result.get("main_url"):
            lines.append(f"🔗 {result['main_url']}")
        return "\n".join(lines)
