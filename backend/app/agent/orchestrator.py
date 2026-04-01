"""Agent Orchestrator: 사용자 요청 → 의도 분석 → Blueprint → Tool 실행 → 결과

고도화 항목:
1. 생성 완료 후 안내 메시지 (전체 너비, 뷰 변경 등)
2. 대화 맥락 유지 (후속 수정 지원)
3. 스킬 동적 로딩 (AI가 .md 읽고 Blueprint 생성)
"""

from typing import Any, AsyncGenerator

from app.agent.intent_analyzer import analyze_intent
from app.agent.blueprint_generator import generate_blueprint  # now async, takes message string
from app.agent.tools.add_blocks import AddBlocksTool, spec_to_block
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.notion.client import NotionClient
from app.notion.block_builder import build_database_properties
from app.schemas.blueprint import IntentResult


class AgentOrchestrator:
    def __init__(self, notion_token: str = "", parent_page_id: str = "", ai_key: str = "", ai_model: str = ""):
        from app.config import settings

        self.client = NotionClient(
            token=notion_token or settings.notion_api_key,
            parent_page_id=parent_page_id or settings.notion_parent_page_id,
        )
        self.parent_page_id = parent_page_id or settings.notion_parent_page_id
        self.add_blocks_tool = AddBlocksTool(self.client)
        self.add_items_tool = AddDatabaseItemsTool(self.client)
        self.ai_key = ai_key
        self.ai_model = ai_model

        # 대화 맥락 유지
        self._conversation: list[dict[str, str]] = []
        self._last_intent: IntentResult | None = None
        self._last_result: dict[str, Any] | None = None

    async def process(self, message: str) -> AsyncGenerator[dict[str, Any], None]:
        """메인 처리 파이프라인 — 실시간 스트리밍"""

        self._conversation.append({"role": "user", "content": message})

        # ① 의도 분석
        yield {"type": "progress", "step": "intent_analysis", "message": "🔍 요청을 분석하고 있어요..."}
        intent = await analyze_intent(message)
        yield {"type": "progress", "step": "intent_done", "message": f"✅ 의도 파악: {intent.intent} ({intent.template_type})"}

        if intent.intent == "MODIFY" and self._last_result:
            async for event in self._handle_modify(message, intent):
                yield event
            return

        if intent.intent == "QUESTION":
            yield {"type": "ai_response", "content": self._answer_question(message)}
            return

        if intent.confidence < 0.5 and intent.missing_info:
            yield {"type": "question", "content": self._build_question(intent), "intent": intent.model_dump()}
            return

        # ② AI 설계
        yield {"type": "progress", "step": "designing", "message": "🎨 AI가 템플릿을 설계하고 있어요..."}
        blueprint = await generate_blueprint(message, ai_key=self.ai_key, ai_model=self.ai_model)

        method = blueprint.get("metadata", {}).get("generation_method", "?")
        skill = blueprint.get("metadata", {}).get("skill_used", "?")
        num_blocks = len(blueprint.get("blocks", []))
        num_dbs = len(blueprint.get("databases", []))
        yield {"type": "progress", "step": "design_done", "message": f"✅ 설계 완료: {skill} 스킬, 블록 {num_blocks}개, DB {num_dbs}개 ({method})"}

        yield {"type": "blueprint_preview", "content": self._format_preview(blueprint), "blueprint": blueprint}

        # ③ Notion 생성 (실시간 스트리밍)
        yield {"type": "progress", "step": "creating", "message": "🏗️ 노션에 생성을 시작합니다..."}

        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}
        main = blueprint["main_page"]

        # 페이지 생성
        yield {"type": "progress", "step": "page", "message": f"📄 페이지 생성 중: {main.get('icon','')} {main['title']}"}
        try:
            page = await self.client.create_page(
                parent_id=self.parent_page_id,
                title=main["title"],
                icon=main.get("icon"),
                cover_url=main.get("cover_url"),
            )
            main_page_id = page["id"]
            result["pages"].append({"id": main_page_id, "title": main["title"], "url": page.get("url", "")})
            result["main_url"] = page.get("url", "")

            # 페이지 전체 너비 자동 설정 (token_v2가 있을 때만)
            full_width_ok = await self.client.set_page_full_width(main_page_id)
            if full_width_ok:
                yield {"type": "progress", "step": "page_done", "message": f"✅ 페이지 생성됨 (전체 너비): {main.get('icon','')} {main['title']}"}
            else:
                yield {"type": "progress", "step": "page_done", "message": f"✅ 페이지 생성됨: {main.get('icon','')} {main['title']}"}
        except Exception as e:
            yield {"type": "progress", "step": "error", "message": f"❌ 페이지 생성 실패: {str(e)[:50]}"}
            raise RuntimeError(f"메인 페이지 생성 실패: {e}") from e

        # 하위 페이지
        sub_page_map: dict[str, str] = {}
        for sub in blueprint.get("sub_pages", []):
            yield {"type": "progress", "step": "sub_page", "message": f"📁 하위 페이지: {sub.get('icon','')} {sub['title']}"}
            try:
                sub_page = await self.client.create_page(parent_id=main_page_id, title=sub["title"], icon=sub.get("icon"))
                sub_page_map[sub["title"]] = sub_page["id"]
                result["pages"].append({"id": sub_page["id"], "title": sub["title"]})
                yield {"type": "progress", "step": "sub_page_done", "message": f"✅ {sub.get('icon','')} {sub['title']} 생성됨"}
            except Exception as e:
                yield {"type": "progress", "step": "warning", "message": f"⚠️ {sub['title']} 스킵됨"}

        # 블록 + DB 삽입
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        for i, block in enumerate(blocks):
            block_type = block.get("type", "?")
            try:
                if block_type == "database_ref":
                    if db_index < len(databases):
                        db_spec = databases[db_index]
                        db_title = db_spec.get("title", db_spec.get("db_name", "DB"))
                        yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title}"}

                        try:
                            db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=db_spec)
                            result["databases"].append(db_result)

                            # 속성 수
                            num_props = len(db_spec.get("db_properties", db_spec.get("properties", {})))
                            yield {"type": "progress", "step": "db_created", "message": f"✅ {db_title} DB 생성됨 (속성 {num_props}개)"}

                            # 샘플 데이터
                            samples = db_spec.get("sample_items", [])
                            if samples:
                                yield {"type": "progress", "step": "samples", "message": f"📝 샘플 데이터 {len(samples)}개 추가 중..."}
                                for j, item in enumerate(samples[:3]):
                                    icon = item.get("icon", "")
                                    title_val = next((v for k, v in item.items() if k != "icon" and isinstance(v, str)), f"항목 {j+1}")
                                    yield {"type": "progress", "step": "sample_item", "message": f"  {icon} {title_val}"}

                            # 뷰
                            views = db_spec.get("views", [])
                            for view in views:
                                view_type = view if isinstance(view, str) else view.get("type", "?")
                                view_icons = {"table": "📋", "gallery": "🖼️", "board": "📊", "calendar": "📅", "timeline": "📈", "list": "📝"}
                                yield {"type": "progress", "step": "view", "message": f"  {view_icons.get(view_type, '📋')} {view_type} 뷰 추가됨"}

                        except Exception as e:
                            yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:50]}"}
                        db_index += 1

                elif block_type == "column_list":
                    yield {"type": "progress", "step": "block", "message": "🔲 칼럼 레이아웃 생성 중..."}
                    db_refs_in_col = self._collect_db_refs_in_columns(block)
                    for _ in db_refs_in_col:
                        if db_index < len(databases):
                            try:
                                db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=databases[db_index])
                                result["databases"].append(db_result)
                            except Exception:
                                pass
                            db_index += 1
                    column_block = await self._build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception:
                            pass
                    yield {"type": "progress", "step": "block_done", "message": "✅ 칼럼 레이아웃 생성됨"}

                else:
                    # 일반 블록 (주요 블록만 로그)
                    if block_type in ("callout", "heading_1", "heading_2"):
                        text = block.get("text", "")[:30]
                        yield {"type": "progress", "step": "block", "message": f"🧱 {block_type}: {text}"}

                    notion_block = spec_to_block(block)
                    try:
                        await self.client.add_blocks(main_page_id, [notion_block])
                        result["blocks"] += 1
                    except Exception as e:
                        print(f"[블록 스킵] {block_type}: {str(e)[:80]}")

            except Exception as e:
                print(f"[블록 처리 오류] {block_type}: {str(e)[:80]}")

        # 남은 DB
        while db_index < len(databases):
            try:
                db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=databases[db_index])
                result["databases"].append(db_result)
            except Exception:
                pass
            db_index += 1

        # 하위 페이지 블록
        for sub in blueprint.get("sub_pages", []):
            sub_id = sub_page_map.get(sub["title"])
            if sub_id and sub.get("blocks"):
                try:
                    notion_blocks = [spec_to_block(b) for b in sub["blocks"] if b.get("type") != "database_ref"]
                    if notion_blocks:
                        await self.client.add_blocks(sub_id, notion_blocks)
                except Exception:
                    pass

        # 결과 저장
        self._last_intent = intent
        self._last_result = result

        # ④ 완료
        yield {"type": "complete", "content": self._format_complete(result), "result": result}

    async def _handle_modify(self, message: str, intent: IntentResult) -> AsyncGenerator[dict[str, Any], None]:
        """후속 수정 처리 — 기존 생성 결과에 추가/변경"""
        msg = message.lower()
        result = self._last_result

        if not result or not result.get("databases"):
            yield {"type": "ai_response", "content": "수정할 템플릿이 없습니다. 먼저 템플릿을 생성해주세요."}
            return

        # DB 속성 추가 요청
        if "속성" in msg and ("추가" in msg or "넣어" in msg):
            yield {"type": "progress", "step": "modifying", "message": "데이터베이스를 수정 중..."}

            db_id = result["databases"][0]["id"]
            new_props = self._parse_property_request(message)

            if new_props:
                try:
                    props = build_database_properties(new_props)
                    await self.client.update_database(db_id, {"properties": props})
                    prop_names = ", ".join(new_props.keys())
                    yield {
                        "type": "complete",
                        "content": f"✅ 속성 추가 완료!\n📊 추가된 속성: {prop_names}\n\n기존 데이터베이스에 새 속성이 추가되었습니다.",
                    }
                except Exception as e:
                    yield {"type": "error", "content": f"속성 추가 중 오류: {str(e)[:100]}"}
            else:
                yield {
                    "type": "question",
                    "content": "어떤 속성을 추가할까요?\n\n예시:\n- \"우선순위 select 속성 추가해줘 (높음/중간/낮음)\"\n- \"메모 텍스트 속성 추가해줘\"\n- \"마감일 날짜 속성 추가해줘\"",
                }
            return

        # 블록 추가 요청
        if any(w in msg for w in ["블록", "섹션", "내용", "텍스트"]) and "추가" in msg:
            yield {"type": "progress", "step": "modifying", "message": "블록을 추가 중..."}
            main_page_id = result["pages"][0]["id"]

            blocks_to_add = self._parse_block_request(message)
            try:
                notion_blocks = [spec_to_block(b) for b in blocks_to_add]
                await self.client.add_blocks(main_page_id, notion_blocks)
                yield {"type": "complete", "content": f"✅ 블록 {len(blocks_to_add)}개 추가 완료!"}
            except Exception as e:
                yield {"type": "error", "content": f"블록 추가 중 오류: {str(e)[:100]}"}
            return

        # 기타 수정
        yield {
            "type": "question",
            "content": "어떤 수정을 원하시나요?\n\n가능한 수정:\n- \"DB에 우선순위 속성 추가해줘\"\n- \"FAQ 섹션 추가해줘\"\n- \"새 하위 페이지 추가해줘\"",
        }

    def _parse_property_request(self, message: str) -> dict[str, Any]:
        """유저 메시지에서 속성 추가 요청 파싱"""
        msg = message.lower()
        props: dict[str, Any] = {}

        # "우선순위 select 속성 (높음/중간/낮음)"
        if "select" in msg or "셀렉트" in msg:
            # 속성 이름 추출 (첫 번째 한글 단어)
            import re
            name_match = re.search(r"[가-힣a-zA-Z]+", message)
            name = name_match.group() if name_match else "카테고리"

            # 옵션 추출 (괄호 안 또는 / 구분)
            options_match = re.search(r"[(\(]([^)]+)[)\)]", message)
            if options_match:
                options = [o.strip() for o in options_match.group(1).split("/")]
            else:
                options = ["옵션1", "옵션2", "옵션3"]

            colors = ["blue", "orange", "green", "red", "purple", "yellow"]
            props[name] = {
                "type": "select",
                "options": [{"name": o, "color": colors[i % len(colors)]} for i, o in enumerate(options)],
            }

        elif "날짜" in msg or "date" in msg or "마감" in msg:
            props["마감일" if "마감" in msg else "날짜"] = "date"

        elif "체크" in msg or "checkbox" in msg:
            props["완료"] = "checkbox"

        elif "숫자" in msg or "number" in msg or "점수" in msg:
            props["점수" if "점수" in msg else "숫자"] = "number"

        elif "텍스트" in msg or "메모" in msg or "text" in msg:
            props["메모" if "메모" in msg else "비고"] = "rich_text"

        elif "url" in msg or "링크" in msg:
            props["URL"] = "url"

        elif "이메일" in msg or "email" in msg:
            props["이메일"] = "email"

        return props

    def _parse_block_request(self, message: str) -> list[dict]:
        """유저 메시지에서 블록 추가 요청 파싱"""
        msg = message.lower()
        blocks: list[dict] = []

        if "faq" in msg or "자주" in msg:
            blocks.extend([
                {"type": "divider"},
                {"type": "heading_2", "text": "💡 자주 묻는 질문"},
                {"type": "toggle", "text": "질문 1", "children_text": "답변을 입력하세요."},
                {"type": "toggle", "text": "질문 2", "children_text": "답변을 입력하세요."},
                {"type": "toggle", "text": "질문 3", "children_text": "답변을 입력하세요."},
            ])
        elif "구분" in msg or "divider" in msg:
            blocks.append({"type": "divider"})
        elif "제목" in msg or "헤딩" in msg:
            blocks.append({"type": "heading_2", "text": "새 섹션"})
        else:
            blocks.extend([
                {"type": "divider"},
                {"type": "heading_2", "text": "📌 추가 내용"},
                {"type": "paragraph", "text": "여기에 내용을 입력하세요."},
            ])

        return blocks

    def _answer_question(self, message: str) -> str:
        """QUESTION 의도 응답"""
        msg = message.lower()

        if "버튼" in msg:
            return "Notion API에서는 버튼 블록 생성이 불가능합니다.\n\n대안으로 콜아웃 블록에 아이콘을 넣어 버튼처럼 보이게 만들어드립니다."

        if "갤러리" in msg or "캘린더" in msg or "칸반" in msg or "뷰" in msg:
            return "Views API (2026-03-19)로 갤러리, 캘린더, 칸반 뷰를 자동 생성할 수 있습니다!\n\n템플릿 생성 시 원하는 뷰를 말씀해주시면 자동으로 추가해드립니다.\n예: \"프로젝트 보드 만들어줘, 칸반 뷰로\""

        if "전체 너비" in msg or "풀 너비" in msg or "full width" in msg:
            return "Notion API에서는 페이지 전체 너비 설정이 불가능합니다.\n\n생성 후 직접 변경 방법:\n페이지 우측 상단 ··· → 전체 너비 활성화 (3초)"

        if any(w in msg for w in ["가능", "할 수", "뭐야", "뭘 할"]):
            return (
                "NotionForge가 할 수 있는 것:\n\n"
                "✅ 페이지 생성 (커버, 아이콘, 제목)\n"
                "✅ 데이터베이스 생성 + 모든 속성 타입\n"
                "✅ 블록 배치 (heading, callout, toggle, 체크리스트 등)\n"
                "✅ 2단/3단 칼럼 레이아웃\n"
                "✅ 색상 테마 (8가지)\n"
                "✅ 하위 페이지 구조\n"
                "✅ 샘플 데이터 자동 입력\n\n"
                "✅ DB 뷰 자동 생성 (갤러리, 캘린더, 칸반, 타임라인)\n"
                "✅ Tab 블록 (콘텐츠 탭 구분)\n\n"
                "❌ 불가: 버튼 블록, 전체 너비 설정"
            )

        return "궁금한 점이 있으시면 편하게 물어보세요! 또는 원하는 템플릿을 설명해주시면 바로 만들어드립니다."

    async def _execute_blueprint(self, blueprint: dict) -> dict[str, Any]:
        """Blueprint 실행 — 올바른 순서로 생성"""
        main = blueprint["main_page"]
        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}

        # 1. 메인 페이지 생성
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
        result["pages"].append({"id": main_page_id, "title": main["title"], "url": page.get("url", "")})
        result["main_url"] = page.get("url", "")

        # 2. 하위 페이지 먼저 생성
        sub_page_map: dict[str, str] = {}
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

        # 3. 블록 + DB를 순서대로 삽입
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        for block in blocks:
            try:
                if block.get("type") == "database_ref":
                    if db_index < len(databases):
                        try:
                            db_result = await self._create_database_with_data(
                                parent_id=main_page_id,
                                db_spec=databases[db_index],
                            )
                            result["databases"].append(db_result)
                        except Exception as e:
                            print(f"[DB 생성 스킵] {str(e)[:100]}")
                        db_index += 1

                elif block.get("type") == "column_list":
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

                    column_block = await self._build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            print(f"[칼럼 블록 스킵] {str(e)[:100]}")

                else:
                    notion_block = spec_to_block(block)
                    try:
                        await self.client.add_blocks(main_page_id, [notion_block])
                        result["blocks"] += 1
                    except Exception as e:
                        print(f"[블록 스킵] {block.get('type', '?')}: {str(e)[:100]}")

            except Exception as e:
                print(f"[블록 처리 오류] {block.get('type', '?')}: {str(e)[:100]}")

        # 남은 DB 추가
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

        # 4. 하위 페이지에 블록 추가
        for sub in blueprint.get("sub_pages", []):
            sub_id = sub_page_map.get(sub["title"])
            if sub_id and sub.get("blocks"):
                try:
                    notion_blocks = [spec_to_block(b) for b in sub["blocks"] if b.get("type") != "database_ref"]
                    if notion_blocks:
                        await self.client.add_blocks(sub_id, notion_blocks)
                except Exception as e:
                    print(f"[하위 페이지 블록 스킵] {sub['title']}: {str(e)[:80]}")

        return result

    async def _create_database_with_data(self, parent_id: str, db_spec: dict) -> dict[str, Any]:
        """DB 생성 + 샘플 데이터 + 뷰 자동 생성"""
        properties = build_database_properties(db_spec["properties"])
        db = await self.client.create_database(
            parent_id=parent_id,
            title=db_spec["title"],
            properties=properties,
            is_inline=db_spec.get("is_inline", True),
        )

        db_id = db["id"]

        # 샘플 데이터 추가
        if "sample_items" in db_spec:
            try:
                await self.add_items_tool.execute(
                    database_id=db_id,
                    items=db_spec["sample_items"],
                    db_properties=db_spec["properties"],
                )
            except Exception as e:
                print(f"[샘플 데이터 스킵] {str(e)[:80]}")

        # 뷰 자동 생성 (Views API 2026-03-19)
        views = db_spec.get("views", [])
        for view in views:
            try:
                await self.client.create_view(
                    database_id=db_id,
                    view_type=view.get("type", "table"),
                    title=view.get("title", ""),
                    filters=view.get("filters"),
                    sorts=view.get("sorts"),
                )
            except Exception as e:
                print(f"[뷰 생성 스킵] {view.get('type', '?')}: {str(e)[:80]}")

        return {"id": db_id, "title": db_spec["title"], "views": len(views)}

    async def _build_column_with_db(self, block: dict, page_id: str, sub_page_map: dict, result: dict) -> dict | None:
        """칼럼 블록 생성"""
        from app.notion import block_builder as bb

        columns_data = block.get("columns", [])
        col_blocks = []

        for col in columns_data:
            col_children = []
            for b in col.get("blocks", []):
                if b.get("type") == "database_ref":
                    col_children.append(bb.callout("위 데이터베이스를 확인하세요", icon="📊"))
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

    def _collect_db_refs_in_columns(self, block: dict) -> list[int]:
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
        if meta.get("skill_loaded"):
            lines.append("🔧 스킬: 로딩됨")
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

        # 사용 안내 (고도화 #1)
        lines.append("")
        lines.append("💡 **추가 설정 안내**")
        lines.append("• 전체 너비: 페이지 우측 상단 ··· → 전체 너비 활성화")
        if result.get("databases"):
            lines.append("• DB 뷰 변경: DB 상단 + 버튼 → 갤러리/캘린더/보드 선택")
            lines.append("• 필터/정렬: DB 상단 필터 아이콘 클릭")
        lines.append("")
        lines.append("💬 수정이 필요하면 말씀해주세요! (예: \"DB에 우선순위 속성 추가해줘\")")

        return "\n".join(lines)
