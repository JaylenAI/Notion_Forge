"""Modify Handler: 후속 수정 처리 모듈

orchestrator.py에서 추출된 수정 전담 핸들러.
생성된 템플릿에 대한 속성/뷰/DB/블록 추가·삭제·변경 등 10가지 수정 유형을 처리한다.
"""

import logging
import re
from typing import Any, AsyncGenerator

from app.agent.tools.add_blocks import spec_to_block
from app.agent.view_builder import build_view_configuration
from app.notion.block_builder import build_database_properties
from app.notion.client import NotionClient
from app.schemas.blueprint import IntentResult

logger = logging.getLogger("notionforge.modify_handler")


class ModifyHandler:
    """후속 수정 처리 — AI 기반 멀티턴 대화형 수정

    지원하는 수정 유형 (10가지):
    1. 속성 삭제/제거
    2. 속성 추가
    3. 뷰 추가/변경
    4. DB 추가 (새 데이터베이스)
    5. Relation 연결
    6. Formula 추가
    7. 서브페이지 추가
    8. 블록 추가
    9. 뷰 삭제
    10. 블록 삭제
    """

    # ── 디스패치 테이블: 수정 유형 → 핸들러 메서드 이름 ──────────
    _HANDLERS: dict[str, str] = {
        "recolor": "_handle_recolor",
        "delete_property": "_handle_delete_property",
        "add_property": "_handle_add_property",
        "add_view": "_handle_add_view",
        "add_formula": "_handle_add_formula",
        "add_relation": "_handle_add_relation",
        "add_database": "_handle_add_database",
        "delete_item": "_handle_delete_item",
        "add_block": "_handle_add_block",
        "add_sub_page": "_handle_add_sub_page",
        "modify_default": "_handle_modify_default",
    }

    def __init__(self, client: NotionClient, ai_key: str = "", ai_model: str = ""):
        self.client = client
        self.ai_key = ai_key
        self.ai_model = ai_model

    # ── 메인 디스패처 ──────────────────────────────────────────────

    async def handle_modify(
        self,
        message: str,
        intent: IntentResult,
        last_result: dict[str, Any] | None,
        last_blueprint: dict[str, Any] | None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """후속 수정 처리 — 수정 유형을 분류한 뒤 해당 핸들러에 위임.

        Args:
            message: 사용자 메시지 원문
            intent: 의도 분석 결과
            last_result: 이전 생성 결과 (pages, databases, blocks 등)
            last_blueprint: 이전 블루프린트
        """
        result = last_result

        if not result or not result.get("pages"):
            yield {"type": "ai_response", "content": "수정할 템플릿이 없습니다. 먼저 템플릿을 생성해주세요."}
            return

        # LLM 분류 우선 (자유 발화·recolor 등 지원), 실패/미설정 시 regex 폴백 (robustness)
        from app.agent.modify_classifier import classify_modification

        modify_type = await classify_modification(message, result, last_blueprint, self.ai_key, self.ai_model)
        if not modify_type:
            modify_type = self._classify_modify_type(message, result)
        handler_name = self._HANDLERS.get(modify_type, "_handle_modify_default")
        handler = getattr(self, handler_name)

        async for event in handler(message, result):
            yield event

    # ── 수정 유형 분류 ─────────────────────────────────────────────

    @staticmethod
    def _classify_modify_type(message: str, result: dict[str, Any]) -> str:
        """메시지 키워드 분석으로 수정 유형을 반환한다."""
        msg = message.lower()
        has_dbs = bool(result.get("databases"))
        delete_words = ("삭제", "없애", "제거", "빼")
        add_words = ("추가", "넣어", "만들어")

        # 뷰 삭제 (뷰 키워드 + 삭제 — 속성 삭제보다 먼저 체크)
        if (
            has_dbs
            and any(w in msg for w in ["뷰", "보드", "캘린더", "갤러리", "타임라인"])
            and any(w in msg for w in delete_words)
        ):
            return "delete_item"

        # 속성 삭제
        if has_dbs and any(w in msg for w in delete_words) and "속성" in msg:
            return "delete_property"

        # 속성 추가
        if has_dbs and "속성" in msg and any(w in msg for w in add_words):
            return "add_property"

        # 뷰 추가/변경
        if has_dbs and any(w in msg for w in ["뷰", "보드", "캘린더", "갤러리", "타임라인", "테이블", "칸반"]):
            return "add_view"

        # Formula 추가
        if has_dbs and any(w in msg for w in ["수식", "formula", "포뮬라", "계산", "d-day", "디데이"]):
            return "add_formula"

        # Relation 연결
        if has_dbs and any(w in msg for w in ["연결", "relation", "릴레이션", "관계"]):
            return "add_relation"

        # DB 추가
        if any(w in msg for w in ["db ", "데이터베이스", "디비"]) and any(w in msg for w in ["추가", "만들어", "생성"]):
            return "add_database"

        # 블록 삭제
        if any(w in msg for w in ["블록", "섹션", "내용"]) and any(w in msg for w in delete_words):
            return "delete_item"

        # 서브페이지 추가
        if any(w in msg for w in ["하위 페이지", "서브페이지", "페이지 추가", "새 페이지"]):
            return "add_sub_page"

        # 블록 추가
        if any(w in msg for w in ["블록", "섹션", "내용", "텍스트", "faq", "가이드"]) and any(
            w in msg for w in ["추가", "넣어"]
        ):
            return "add_block"

        return "modify_default"

    # ── 개별 핸들러 ────────────────────────────────────────────────

    async def _handle_recolor(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """라이브 페이지 블록 색상을 테마 색으로 변경 (B1 — '색 바꿔줘')."""
        from app.agent.intent_analyzer import COLOR_MAP

        msg = message.lower()
        new_color = next((en for kr, en in COLOR_MAP.items() if kr in msg), None)
        if not new_color:
            yield {"type": "ai_response", "content": "어떤 색으로 바꿀까요? (예: 파란색, 초록색, 보라색)"}
            return

        main_page_id = result["pages"][0]["id"]
        yield {"type": "progress", "step": "modifying", "message": f"🎨 {new_color} 테마로 색상을 바꾸고 있어요..."}
        bg = f"{new_color}_background"
        themed = {"callout", "quote", "toggle"}
        headings = {"heading_1", "heading_2", "heading_3"}
        changed = 0
        try:
            children = await self.client.get_block_children(main_page_id)
            for ch in children:
                t = ch.get("type")
                if t not in themed and t not in headings:
                    continue
                payload = ch.get(t, {}) or {}
                # Notion 블록 update는 rich_text가 필수 → 기존 내용 보존하고 color만 교체.
                upd: dict[str, Any] = {"color": bg if t in themed else new_color}
                if payload.get("rich_text") is not None:
                    upd["rich_text"] = payload["rich_text"]
                if t == "callout" and payload.get("icon"):
                    upd["icon"] = payload["icon"]
                res = await self.client.update_block(ch["id"], {t: upd})
                if not (isinstance(res, dict) and res.get("fallback")):
                    changed += 1
            if changed:
                yield {"type": "complete", "content": f"✅ {changed}개 블록을 {new_color} 테마로 바꿨어요!"}
            else:
                yield {"type": "ai_response", "content": "색을 적용할 블록을 찾지 못했어요(콜아웃/헤딩 없음)."}
        except Exception as e:
            yield {"type": "error", "content": f"색상 변경 실패: {str(e)[:100]}"}

    async def _handle_delete_property(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """속성 삭제"""
        msg = message.lower()
        yield {"type": "progress", "step": "modifying", "message": "🗑️ 속성을 삭제하고 있어요..."}
        db_id = self._pick_target_db(msg, result)
        prop_name = self._extract_property_name(message)
        if prop_name:
            try:
                await self.client.update_database(db_id, {"properties": {prop_name: None}})
                yield {"type": "complete", "content": f'✅ "{prop_name}" 속성 삭제 완료!'}
            except Exception as e:
                yield {"type": "error", "content": f"속성 삭제 실패: {str(e)[:100]}"}
        else:
            yield {"type": "question", "content": "어떤 속성을 삭제할까요? 속성 이름을 정확히 알려주세요."}

    async def _handle_add_property(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """속성 추가"""
        msg = message.lower()
        yield {"type": "progress", "step": "modifying", "message": "📊 속성을 추가하고 있어요..."}
        db_id = self._pick_target_db(msg, result)
        new_props = self._parse_property_request(message)
        if new_props:
            try:
                props = build_database_properties(new_props)
                await self.client.update_database(db_id, {"properties": props})
                prop_names = ", ".join(new_props.keys())
                yield {"type": "complete", "content": f"✅ 속성 추가 완료!\n📊 추가된 속성: {prop_names}"}
            except Exception as e:
                yield {"type": "error", "content": f"속성 추가 실패: {str(e)[:100]}"}
        else:
            yield {
                "type": "question",
                "content": '어떤 속성을 추가할까요?\n\n예시:\n- "우선순위 select 속성 추가해줘 (높음/중간/낮음)"\n- "마감일 날짜 속성 추가해줘"\n- "메모 텍스트 속성 추가해줘"',
            }

    async def _handle_add_view(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """뷰 추가/변경"""
        msg = message.lower()
        yield {"type": "progress", "step": "modifying", "message": "📋 뷰를 추가하고 있어요..."}
        db_id = self._pick_target_db(msg, result)
        view_type = self._detect_view_type(msg)
        view_title = {
            "board": "칸반 보드",
            "calendar": "캘린더",
            "gallery": "갤러리",
            "timeline": "타임라인",
            "table": "테이블",
            "list": "리스트",
        }.get(view_type, view_type)

        group_by = None
        view_config_spec: dict[str, Any] = {"type": view_type}
        if view_type == "board":
            group_by = {"property": "상태"}
            view_config_spec["cover"] = {"type": "page_cover"}
            view_config_spec["cover_size"] = "medium"
        elif view_type == "gallery":
            view_config_spec["cover"] = {"type": "page_cover"}
            view_config_spec["cover_size"] = "medium"

        configuration = build_view_configuration(view_config_spec)

        try:
            await self.client.create_view(
                database_id=db_id,
                view_type=view_type,
                title=view_title,
                group_by=group_by,
                configuration=configuration,
            )
            yield {"type": "complete", "content": f"✅ {view_title} 뷰 추가 완료!"}
        except Exception as e:
            yield {"type": "error", "content": f"뷰 추가 실패: {str(e)[:100]}"}

    async def _handle_add_database(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """새 데이터베이스 추가"""
        main_page_id = result["pages"][0]["id"]
        yield {"type": "progress", "step": "modifying", "message": "📊 새 데이터베이스를 생성 중..."}
        try:
            from app.agent.blueprint_generator import generate_blueprint

            bp = await generate_blueprint(
                f"단일 데이터베이스만 만들어줘: {message}",
                ai_key=self.ai_key,
                ai_model=self.ai_model,
            )
            if bp.get("databases"):
                db_spec = bp["databases"][0]
                from app.agent.tools.add_database_items import AddDatabaseItemsTool

                db_props = build_database_properties(db_spec.get("properties", db_spec.get("db_properties", {})))
                db = await self.client.create_database(
                    parent_id=main_page_id,
                    title=db_spec.get("title", db_spec.get("db_name", "DB")),
                    properties=db_props,
                    icon=db_spec.get("icon"),
                )
                db_result = {
                    "id": db["id"],
                    "title": db_spec.get("title", db_spec.get("db_name", "DB")),
                }

                # 샘플 데이터 추가
                samples = db_spec.get("sample_items", [])
                if samples:
                    items_tool = AddDatabaseItemsTool(self.client)
                    try:
                        await items_tool.run(db["id"], samples)
                    except Exception as e:
                        logger.info(f"[샘플 데이터 추가 실패] {str(e)[:80]}")

                # 뷰 생성
                for view_spec in db_spec.get("views", []):
                    if isinstance(view_spec, str):
                        view_spec = {"type": view_spec}
                    try:
                        config = build_view_configuration(view_spec)
                        await self.client.create_view(
                            database_id=db["id"],
                            view_type=view_spec.get("type", "table"),
                            title=view_spec.get("title", view_spec.get("type", "table")),
                            configuration=config,
                        )
                    except Exception as e:
                        logger.info(f"[뷰 생성 스킵] {str(e)[:80]}")

                result["databases"].append(db_result)
                yield {
                    "type": "complete",
                    "content": (
                        f'✅ "{db_spec.get("title", "DB")}" 데이터베이스 추가 완료!\n'
                        f"📊 속성 {len(db_spec.get('properties', db_spec.get('db_properties', {})))}개, 샘플 데이터 포함"
                    ),
                }
            else:
                yield {"type": "error", "content": "DB 설계 실패. 다시 시도해주세요."}
        except Exception as e:
            yield {"type": "error", "content": f"DB 추가 실패: {str(e)[:100]}"}

    async def _handle_add_relation(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Relation 연결"""
        msg = message.lower()
        yield {"type": "progress", "step": "modifying", "message": "🔗 DB를 연결하고 있어요..."}
        if len(result["databases"]) < 2:
            yield {
                "type": "question",
                "content": 'Relation 연결은 2개 이상의 DB가 필요합니다.\n먼저 DB를 추가해주세요! (예: "태스크 DB 추가해줘")',
            }
            return

        source_db = result["databases"][0]
        target_db = result["databases"][1]

        for i, db in enumerate(result["databases"]):
            db_title = db.get("title", "").lower()
            if db_title and db_title in msg:
                if i == 0:
                    target_db = result["databases"][1] if len(result["databases"]) > 1 else result["databases"][0]
                else:
                    source_db = result["databases"][0]
                    target_db = db

        relation_name = f"관련 {target_db['title']}"
        try:
            await self.client.update_database(
                source_db["id"],
                {
                    "properties": {
                        relation_name: {
                            "relation": {
                                "database_id": target_db["id"],
                                "single_property": {},
                            }
                        }
                    }
                },
            )
            yield {
                "type": "complete",
                "content": (
                    f"✅ Relation 연결 완료!\n"
                    f"🔗 {source_db['title']} → {target_db['title']}\n"
                    f'📊 "{relation_name}" 속성 추가됨'
                ),
            }
        except Exception as e:
            yield {"type": "error", "content": f"Relation 연결 실패: {str(e)[:100]}"}

    async def _handle_add_formula(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Formula 추가"""
        msg = message.lower()
        yield {"type": "progress", "step": "modifying", "message": "🔢 수식 속성을 추가하고 있어요..."}
        db_id = self._pick_target_db(msg, result)
        formula = self._detect_formula(msg)
        if formula:
            try:
                await self.client.update_database(
                    db_id, {"properties": {formula["name"]: {"formula": {"expression": formula["expression"]}}}}
                )
                yield {
                    "type": "complete",
                    "content": f'✅ 수식 속성 추가 완료!\n🔢 "{formula["name"]}" = {formula["expression"][:50]}',
                }
            except Exception as e:
                yield {"type": "error", "content": f"수식 추가 실패: {str(e)[:100]}"}
        else:
            yield {
                "type": "question",
                "content": (
                    "어떤 수식을 추가할까요?\n\n예시:\n"
                    '- "D-Day 수식 추가해줘" (마감일까지 남은 일수)\n'
                    '- "진행률 수식 추가해줘" (상태 기반 %)\n'
                    '- "총액 수식 추가해줘" (단가 × 수량)'
                ),
            }

    async def _handle_add_sub_page(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """서브페이지 추가"""
        main_page_id = result["pages"][0]["id"]
        yield {"type": "progress", "step": "modifying", "message": "📁 하위 페이지를 추가하고 있어요..."}
        title_match = re.search(r"[\"']([^\"']+)[\"']", message)
        page_title = (
            title_match.group(1)
            if title_match
            else message.replace("하위 페이지", "")
            .replace("서브페이지", "")
            .replace("추가해줘", "")
            .replace("만들어줘", "")
            .strip()
        )
        if not page_title or len(page_title) > 50:
            page_title = "새 페이지"

        try:
            from app.notion import block_builder as bb

            sub_page = await self.client.create_page(
                parent_id=main_page_id,
                title=page_title,
                icon="📄",
                position="page_end",
            )
            default_blocks = [
                bb.callout(f"{page_title} 페이지입니다.", icon="📄", color="blue_background"),
                bb.divider(),
                bb.heading(f"📋 {page_title} 개요", level=2),
                bb.paragraph("이 페이지의 내용을 자유롭게 작성해보세요."),
            ]
            await self.client.add_blocks(sub_page["id"], default_blocks)
            result["pages"].append({"id": sub_page["id"], "title": page_title})
            yield {"type": "complete", "content": f'✅ "{page_title}" 하위 페이지 추가 완료!'}
        except Exception as e:
            yield {"type": "error", "content": f"페이지 추가 실패: {str(e)[:100]}"}

    async def _handle_add_block(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """블록 추가"""
        main_page_id = result["pages"][0]["id"]
        yield {"type": "progress", "step": "modifying", "message": "🧱 블록을 추가하고 있어요..."}
        blocks_to_add = self._parse_block_request(message)
        try:
            notion_blocks = [spec_to_block(b) for b in blocks_to_add]
            await self.client.add_blocks(main_page_id, notion_blocks)
            yield {"type": "complete", "content": f"✅ 블록 {len(blocks_to_add)}개 추가 완료!"}
        except Exception as e:
            yield {"type": "error", "content": f"블록 추가 실패: {str(e)[:100]}"}

    async def _handle_delete_item(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """뷰 삭제 또는 블록 삭제 (delete_item으로 통합)"""
        msg = message.lower()
        main_page_id = result["pages"][0]["id"]
        has_dbs = bool(result.get("databases"))

        # 뷰 삭제 판별: 뷰 관련 키워드가 있고 DB가 있으면 뷰 삭제
        view_keywords = ("뷰", "보드", "캘린더", "갤러리", "타임라인")
        if has_dbs and any(w in msg for w in view_keywords):
            yield {"type": "progress", "step": "modifying", "message": "🗑️ 뷰를 삭제하고 있어요..."}
            db_id = self._pick_target_db(msg, result)
            target_view_type = self._detect_view_type(msg)
            try:
                views = await self.client.list_views(db_id)
                deleted = False
                for view in views:
                    if view.get("type") == target_view_type:
                        await self.client.delete_view(view["id"])
                        deleted = True
                        break
                if deleted:
                    view_name = {
                        "board": "칸반 보드",
                        "calendar": "캘린더",
                        "gallery": "갤러리",
                        "timeline": "타임라인",
                        "table": "테이블",
                    }.get(target_view_type, target_view_type)
                    yield {"type": "complete", "content": f"✅ {view_name} 뷰 삭제 완료!"}
                else:
                    yield {"type": "error", "content": "해당 타입의 뷰를 찾을 수 없습니다."}
            except Exception as e:
                yield {"type": "error", "content": f"뷰 삭제 실패: {str(e)[:100]}"}
            return

        # 블록 삭제
        yield {"type": "progress", "step": "modifying", "message": "🗑️ 블록을 삭제하고 있어요..."}
        target_text = ""
        text_match = re.search(r"[\"']([^\"']+)[\"']", message)
        if text_match:
            target_text = text_match.group(1)

        if target_text:
            try:
                children = await self.client.get_block_children(main_page_id)
                deleted = False
                for child in children:
                    block_text = self._extract_block_text(child)
                    if target_text.lower() in block_text.lower():
                        await self.client.delete_block(child["id"])
                        deleted = True
                        break
                if deleted:
                    yield {"type": "complete", "content": f'✅ "{target_text}" 포함 블록 삭제 완료!'}
                else:
                    yield {"type": "error", "content": f'"{target_text}"을 포함하는 블록을 찾을 수 없습니다.'}
            except Exception as e:
                yield {"type": "error", "content": f"블록 삭제 실패: {str(e)[:100]}"}
        else:
            yield {
                "type": "question",
                "content": (
                    "어떤 블록을 삭제할까요?\n"
                    "삭제할 블록의 텍스트를 따옴표로 감싸서 알려주세요.\n"
                    '예: "FAQ" 블록 삭제해줘'
                ),
            }

    async def _handle_modify_default(
        self,
        message: str,
        result: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """폴백: 수정 유형을 인식하지 못한 경우 안내 메시지"""
        yield {
            "type": "question",
            "content": (
                "어떤 수정을 원하시나요?\n\n"
                "**속성 관련:**\n"
                '- "우선순위 select 속성 추가해줘 (높음/중간/낮음)"\n'
                '- "예산 속성 삭제해줘"\n\n'
                "**뷰 관련:**\n"
                '- "캘린더 뷰 추가해줘"\n'
                '- "칸반 보드 뷰 추가해줘"\n\n'
                "**DB 관련:**\n"
                '- "태스크 DB 추가해줘"\n'
                '- "프로젝트랑 태스크 연결해줘"\n\n'
                "**수식:**\n"
                '- "D-Day 수식 추가해줘"\n'
                '- "진행률 계산 추가해줘"\n\n'
                "**삭제:**\n"
                '- "캘린더 뷰 삭제해줘"\n'
                "- \"'FAQ' 블록 삭제해줘\"\n\n"
                "**구조:**\n"
                '- "새 하위 페이지 추가해줘"\n'
                '- "FAQ 섹션 추가해줘"'
            ),
        }

    # ── Helper methods ──────────────────────────────────────────────

    def _pick_target_db(self, msg: str, result: dict) -> str:
        """메시지에서 대상 DB 식별. 이름이 언급되지 않으면 첫 번째 DB."""
        for db in result.get("databases", []):
            title = db.get("title", "").lower()
            if title and title in msg:
                return db["id"]
        return result["databases"][0]["id"] if result.get("databases") else ""

    def _extract_property_name(self, message: str) -> str:
        """메시지에서 속성 이름 추출"""
        # "예산 속성 삭제해줘" → "예산"
        patterns = [
            r"[\"']([^\"']+)[\"']\s*속성",
            r"([가-힣a-zA-Z_]+)\s*속성\s*(삭제|없애|제거|빼)",
            r"(삭제|없애|제거|빼)\s*[\"']?([가-힣a-zA-Z_]+)[\"']?",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                for g in groups:
                    if g and g not in ("삭제", "없애", "제거", "빼", "속성"):
                        return g.strip()
        return ""

    def _detect_view_type(self, msg: str) -> str:
        """메시지에서 뷰 타입 감지"""
        view_map = {
            "보드": "board",
            "칸반": "board",
            "kanban": "board",
            "board": "board",
            "캘린더": "calendar",
            "달력": "calendar",
            "calendar": "calendar",
            "갤러리": "gallery",
            "gallery": "gallery",
            "타임라인": "timeline",
            "timeline": "timeline",
            "리스트": "list",
            "list": "list",
            "테이블": "table",
            "table": "table",
        }
        for keyword, view_type in view_map.items():
            if keyword in msg:
                return view_type
        return "table"

    def _detect_formula(self, msg: str) -> dict[str, str] | None:
        """메시지에서 수식 패턴 감지"""
        if any(w in msg for w in ["d-day", "디데이", "남은 일", "마감까지"]):
            return {"name": "D-Day", "expression": 'dateBetween(prop("마감일"), now(), "days")'}
        if any(w in msg for w in ["진행률", "진행율", "progress"]):
            return {
                "name": "진행률",
                "expression": 'if(prop("상태") == "완료", 100, if(prop("상태") == "진행 중", 50, 0))',
            }
        if any(w in msg for w in ["총액", "합계", "total", "총"]) and any(w in msg for w in ["단가", "수량", "가격"]):
            return {"name": "총액", "expression": 'prop("단가") * prop("수량")'}
        if any(w in msg for w in ["상태 이모지", "체크", "완료 표시"]):
            return {"name": "상태 표시", "expression": 'if(prop("완료"), "✅", "⬜")'}
        if any(w in msg for w in ["지연", "overdue", "초과"]):
            return {"name": "지연 여부", "expression": 'if(prop("마감일") < now(), "⚠️ 지연", "정상")'}
        # 사용자가 직접 수식을 지정한 경우
        expr_match = re.search(r"수식\s*[:=]\s*(.+)", msg)
        if expr_match:
            return {"name": "계산", "expression": expr_match.group(1).strip()}
        return None

    def _parse_property_request(self, message: str) -> dict[str, Any]:
        """유저 메시지에서 속성 추가 요청 파싱"""
        msg = message.lower()
        props: dict[str, Any] = {}

        # "우선순위 select 속성 (높음/중간/낮음)"
        if "select" in msg or "셀렉트" in msg:
            # 속성 이름 추출 (stop words 제외)
            stop_words = {"db에", "db", "디비", "에", "속성", "추가", "해줘", "넣어", "만들어", "select", "셀렉트"}
            name = "카테고리"
            for m in re.finditer(r"[가-힣a-zA-Z]+", message):
                word = m.group()
                if word.lower() not in stop_words and len(word) > 1:
                    name = word
                    break

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

    @staticmethod
    def _extract_block_text(block: dict) -> str:
        """블록에서 텍스트 내용 추출"""
        btype = block.get("type", "")
        block_data = block.get(btype, {})
        rich_texts = block_data.get("rich_text", [])
        return "".join(rt.get("plain_text", "") for rt in rich_texts)

    def _parse_block_request(self, message: str) -> list[dict]:
        """유저 메시지에서 블록 추가 요청 파싱"""
        msg = message.lower()
        blocks: list[dict] = []

        if "faq" in msg or "자주" in msg:
            blocks.extend(
                [
                    {"type": "divider"},
                    {"type": "heading_2", "text": "💡 자주 묻는 질문"},
                    {"type": "toggle", "text": "질문 1", "children_text": "답변을 입력하세요."},
                    {"type": "toggle", "text": "질문 2", "children_text": "답변을 입력하세요."},
                    {"type": "toggle", "text": "질문 3", "children_text": "답변을 입력하세요."},
                ]
            )
        elif "구분" in msg or "divider" in msg:
            blocks.append({"type": "divider"})
        elif "제목" in msg or "헤딩" in msg:
            blocks.append({"type": "heading_2", "text": "새 섹션"})
        else:
            blocks.extend(
                [
                    {"type": "divider"},
                    {"type": "heading_2", "text": "📌 추가 내용"},
                    {"type": "paragraph", "text": "여기에 내용을 입력하세요."},
                ]
            )

        return blocks
