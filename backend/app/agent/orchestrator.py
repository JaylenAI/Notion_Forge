"""Agent Orchestrator: 사용자 요청 → 의도 분석 → Blueprint → 생성 → 결과

핵심 파이프라인만 담당. 세부 로직은 분리된 모듈에 위임:
- creation_executor.py: Notion 생성 실행 (DB, 블록, 서브페이지, 뷰)
- modify_handler.py: 멀티턴 수정 처리 (속성/뷰/DB/수식 등)
- view_builder.py: Views API configuration 빌드
"""

import asyncio
import logging
import uuid
from typing import Any, AsyncGenerator

from app.agent.input_guardrail import validate_input
from app.agent.intent_analyzer import analyze_intent
from app.agent.blueprint_generator import generate_blueprint
from app.agent.tools.add_blocks import AddBlocksTool, spec_to_block
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.agent.creation_executor import CreationExecutor
from app.agent.modify_handler import ModifyHandler
from app.notion.client import NotionClient
from app.core.metrics import GenerationMetrics
from app.core.history import save_generation_record
from app.schemas.blueprint import IntentResult

logger = logging.getLogger("notionforge.orchestrator")


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

        # 분리된 모듈
        self._executor = CreationExecutor(self.client, self.add_items_tool)
        self._modifier = ModifyHandler(self.client, ai_key, ai_model)

        # 대화 맥락 유지
        self._conversation: list[dict[str, str]] = []
        self._last_intent: IntentResult | None = None
        self._last_result: dict[str, Any] | None = None
        self._last_blueprint: dict[str, Any] | None = None

        # 사용자 설정
        self.complexity: str = "standard"
        self.language: str = "ko"
        self.use_pipeline: bool = False

        # Approval Gate
        self._approval_event: asyncio.Event = asyncio.Event()
        self._approval_granted: bool = False

    async def process(self, message: str) -> AsyncGenerator[dict[str, Any], None]:
        """메인 처리 파이프라인 — 실시간 스트리밍"""

        # ⓪ Input Guardrail
        guard = validate_input(message)
        if not guard.is_valid:
            yield {"type": "error", "content": guard.error_message}
            return

        self._conversation.append({"role": "user", "content": message})

        metrics = GenerationMetrics(
            session_id=str(uuid.uuid4())[:8],
            user_input=message,
            complexity=self.complexity,
        )

        # ① 의도 분석
        metrics.start_stage("intent_analysis")
        yield {"type": "progress", "step": "intent_analysis", "message": "🔍 요청을 분석하고 있어요..."}
        intent = await analyze_intent(message)
        metrics.end_stage()
        yield {"type": "progress", "step": "intent_done", "message": f"✅ 의도 파악: {intent.intent} ({intent.template_type})"}

        # 수정 모드 전환
        if intent.intent == "MODIFY" and self._last_result:
            async for event in self._modifier.handle_modify(message, intent, self._last_result, self._last_blueprint):
                yield event
            return

        if self._last_result and intent.intent == "CREATE":
            if self._should_switch_to_modify(message):
                yield {"type": "progress", "step": "intent_override", "message": "🔄 수정 모드로 전환합니다..."}
                async for event in self._modifier.handle_modify(message, intent, self._last_result, self._last_blueprint):
                    yield event
                return

        if intent.intent == "QUESTION":
            yield {"type": "ai_response", "content": self._answer_question(message)}
            return

        if intent.confidence < 0.5 and intent.missing_info:
            yield {"type": "question", "content": self._build_question(intent), "intent": intent.model_dump()}
            return

        # ② AI 설계
        metrics.start_stage("blueprint_generation")
        blueprint = await self._generate_blueprint(message, metrics)
        metrics.end_stage()

        meta = blueprint.get("metadata", {})
        yield {"type": "progress", "step": "design_done", "message": self._format_design_msg(blueprint)}
        yield {"type": "blueprint_preview", "content": self._format_preview(blueprint), "blueprint": blueprint}

        # ── Approval Gate
        self._approval_event.clear()
        self._approval_granted = False
        yield {"type": "approval_request", "content": "템플릿 설계를 확인해주세요. 생성을 진행할까요?", "blueprint": blueprint}

        try:
            await asyncio.wait_for(self._approval_event.wait(), timeout=60.0)
        except asyncio.TimeoutError:
            yield {"type": "error", "content": "60초 동안 응답이 없어 생성을 취소했습니다."}
            return

        if not self._approval_granted:
            yield {"type": "system", "content": "생성이 취소되었습니다. 새로운 요청을 입력해주세요."}
            return

        # 메트릭에 블루프린트 정보 기록
        metrics.skill = meta.get("skill_used", "custom")
        metrics.layout = meta.get("layout", "")
        metrics.model = meta.get("model", self.ai_model)
        metrics.gen_eval_attempts = meta.get("gen_eval_attempts", 1)

        # ③ Notion 생성 (실시간 스트리밍)
        metrics.start_stage("notion_creation")
        async for event in self._execute_creation(blueprint):
            yield event

        result = self._current_result
        metrics.end_stage()

        # ── Rollback 판단
        expected_blocks = len(blueprint.get("blocks", []))
        expected_dbs = len(blueprint.get("databases", []))
        if result["blocks"] == 0 and len(result["databases"]) == 0 and (expected_blocks > 0 or expected_dbs > 0):
            yield {"type": "progress", "step": "rollback", "message": "⚠️ 생성 결과가 비어있어 롤백을 진행합니다..."}
            rolled = await self._executor.rollback(result)
            metrics.finish(success=False, error="empty_result_rollback")
            save_generation_record(metrics.to_dict(), blueprint)
            msg = f"생성 실패로 롤백 완료: {', '.join(rolled)} 삭제됨.\n다시 시도해주세요." if rolled else "생성 실패. 다시 시도해주세요."
            yield {"type": "error", "content": msg}
            return

        # 결과 저장
        self._last_intent = intent
        self._last_result = result
        self._last_blueprint = blueprint

        metrics.blocks_count = result["blocks"]
        metrics.databases_count = len(result["databases"])
        metrics.sub_pages_count = len(result.get("pages", [])) - 1
        metrics.finish(success=True)
        save_generation_record(metrics.to_dict(), blueprint)

        # ④ 완료
        yield {"type": "complete", "content": self._format_complete(result), "result": result}

    def approve_creation(self, approved: bool = True) -> None:
        """Approval Gate 응답"""
        self._approval_granted = approved
        self._approval_event.set()

    # ─── Private: Blueprint 생성 ───

    async def _generate_blueprint(self, message: str, metrics: GenerationMetrics) -> dict[str, Any]:
        """복잡도/언어 힌트 추가 → AI 설계"""
        complexity_label = {"simple": "간단한", "standard": "표준", "advanced": "고급"}.get(self.complexity, "표준")
        enhanced_msg = message
        if self.complexity != "standard":
            complexity_hint = {"simple": "\n[COMPLEXITY: simple — 10-15 blocks, 1 DB, minimal]",
                               "advanced": "\n[COMPLEXITY: advanced — 25-40 blocks, 3-4 DB, 5+ sub_pages, dashboard layout]"}.get(self.complexity, "")
            enhanced_msg = message + complexity_hint
        if self.language != "ko":
            lang_hint = {"en": "\n[LANGUAGE: English — all text content in English]",
                         "ja": "\n[LANGUAGE: Japanese — all text content in Japanese]"}.get(self.language, "")
            enhanced_msg += lang_hint

        use_pipeline = self.use_pipeline or self.complexity == "advanced"
        if use_pipeline:
            from app.agent.pipeline import multi_agent_pipeline
            from app.agent.blueprint_generator import _assemble_blueprint
            async for event in multi_agent_pipeline(enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model):
                if event.get("stage") == "complete":
                    blueprint = _assemble_blueprint(event.get("blueprint"))
                    blueprint["metadata"]["generation_method"] = "multi_agent_pipeline"
                    blueprint["metadata"]["skill_used"] = event.get("blueprint", {}).get("skill", "custom")
                    return blueprint

        return await generate_blueprint(
            enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model,
            conversation_history=self._conversation,
        )

    # ─── Private: Notion 생성 실행 ───

    async def _execute_creation(self, blueprint: dict) -> AsyncGenerator[dict[str, Any], None]:
        """Notion 생성 스트리밍 — CreationExecutor에 위임하면서 진행 상황 yield"""
        yield {"type": "progress", "step": "creating", "message": "🏗️ 노션에 생성을 시작합니다..."}

        result: dict[str, Any] = {"pages": [], "databases": [], "blocks": 0}
        main = blueprint["main_page"]

        # 메인 페이지 생성
        yield {"type": "progress", "step": "page", "message": f"📄 페이지 생성 중: {main.get('icon', '')} {main['title']}"}
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
            yield {"type": "progress", "step": "page_done", "message": f"✅ 페이지 생성됨: {main.get('icon', '')} {main['title']}"}
        except Exception as e:
            yield {"type": "error", "content": f"메인 페이지 생성 실패: {str(e)[:200]}"}
            self._current_result = result
            return

        # Pass 1: 서브페이지
        sub_page_map: dict[str, str] = {}
        for sub in blueprint.get("sub_pages", []):
            yield {"type": "progress", "step": "sub_page", "message": f"📁 하위 페이지: {sub.get('icon', '')} {sub['title']}"}
            try:
                sub_page = await self.client.create_page(parent_id=main_page_id, title=sub["title"], icon=sub.get("icon"), position="page_end")
                sub_page_map[sub["title"]] = sub_page["id"]
                result["pages"].append({"id": sub_page["id"], "title": sub["title"]})
            except Exception as e:
                yield {"type": "progress", "step": "warning", "message": f"⚠️ {sub['title']} 스킵: {str(e)[:50]}"}

        # Pass 1.5: sub_page_ref 치환
        CreationExecutor.resolve_sub_page_refs(blueprint.get("blocks", []), sub_page_map)
        for sub in blueprint.get("sub_pages", []):
            CreationExecutor.resolve_sub_page_refs(sub.get("blocks", []), sub_page_map)

        # Pass 2: 블록 + DB
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "?")
            try:
                if block_type == "database_ref":
                    if db_index < len(databases):
                        db_spec = databases[db_index]
                        db_title = db_spec.get("title", db_spec.get("db_name", "DB"))
                        db_parent_name = db_spec.get("db_parent", "")
                        db_parent_id = sub_page_map.get(db_parent_name, main_page_id) if db_parent_name else main_page_id
                        yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title}"}
                        try:
                            db_result = await self._executor.create_database_with_data(parent_id=db_parent_id, db_spec=db_spec)
                            result["databases"].append(db_result)
                            yield {"type": "progress", "step": "db_created", "message": f"✅ {db_title} DB 생성됨"}
                        except Exception as e:
                            yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:50]}"}
                        db_index += 1

                elif block_type == "column_list":
                    yield {"type": "progress", "step": "block", "message": "🔲 칼럼 레이아웃 생성 중..."}
                    for _ in self._executor.collect_db_refs_in_columns(block):
                        if db_index < len(databases):
                            db_spec = databases[db_index]
                            try:
                                db_result = await self._executor.create_database_with_data(parent_id=main_page_id, db_spec=db_spec)
                                result["databases"].append(db_result)
                            except Exception as e:
                                yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:80]}"}
                            db_index += 1
                    column_block = await self._executor.build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            logger.info(f"[칼럼 블록 추가 실패] {str(e)[:100]}")
                    yield {"type": "progress", "step": "block_done", "message": "✅ 칼럼 레이아웃 생성됨"}

                elif block_type == "linked_view":
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
                    notion_block = spec_to_block(block)
                    try:
                        await self.client.add_blocks(main_page_id, [notion_block])
                        result["blocks"] += 1
                    except Exception as e:
                        logger.info(f"[블록 스킵] {block_type}: {str(e)[:80]}")

            except Exception as e:
                logger.info(f"[블록 처리 오류] {block_type}: {str(e)[:80]}")

        # 남은 DB
        while db_index < len(databases):
            try:
                db_result = await self._executor.create_database_with_data(parent_id=main_page_id, db_spec=databases[db_index])
                result["databases"].append(db_result)
            except Exception:
                pass
            db_index += 1

        # Pass 3: 하위 페이지 블록
        await self._executor.fill_sub_pages(blueprint, sub_page_map, result)

        # Pass 4: Relation/Rollup/Formula 후처리
        await self._executor.post_process_relations(blueprint, result)
        relation_count = sum(1 for db in databases for _, v in db.get("properties", db.get("db_properties", {})).items()
                             if isinstance(v, dict) and (v.get("type") in ("relation", "rollup", "formula") or "target_db_index" in v))
        if relation_count > 0:
            yield {"type": "progress", "step": "relations", "message": f"🔗 DB 간 연결 완료 ({relation_count}개)"}

        # Pass 5: 검증
        validation_issues = await self._executor.validate_creation(main_page_id, blueprint, result)
        if validation_issues:
            yield {"type": "progress", "step": "validation", "message": f"🔍 검증: {len(validation_issues)}개 항목 확인"}
        else:
            yield {"type": "progress", "step": "validation", "message": "✅ 생성 결과 검증 완료 — 모든 항목 정상"}

        self._current_result = result

    # ─── Private: 헬퍼 ───

    @staticmethod
    def _should_switch_to_modify(message: str) -> bool:
        """CREATE 의도이지만 수정 키워드가 있으면 MODIFY로 전환"""
        msg_lower = message.lower()
        modify_keywords = ["추가", "넣어", "바꿔", "변경", "삭제", "없애", "제거", "연결", "빼"]
        context_keywords = ["속성", "뷰", "db", "디비", "데이터베이스", "칼럼", "페이지", "블록",
                            "수식", "formula", "d-day", "relation", "캘린더", "보드", "갤러리",
                            "타임라인", "테이블", "리스트", "칸반"]
        has_modify = any(kw in msg_lower for kw in modify_keywords)
        has_context = any(kw in msg_lower for kw in context_keywords)
        return has_modify and has_context

    def _answer_question(self, message: str) -> str:
        """QUESTION 의도 응답"""
        msg = message.lower()
        if "버튼" in msg:
            return "Notion API에서는 버튼 블록 생성이 불가능합니다.\n\n대안으로 콜아웃 블록에 아이콘을 넣어 버튼처럼 보이게 만들어드립니다."
        if any(w in msg for w in ["갤러리", "캘린더", "칸반", "뷰"]):
            return "Views API (2026-03-19)로 갤러리, 캘린더, 칸반 뷰를 자동 생성할 수 있습니다!\n\n예: \"프로젝트 보드 만들어줘, 칸반 뷰로\""
        if "전체 너비" in msg or "풀 너비" in msg:
            return "Notion API에서는 페이지 전체 너비 설정이 불가능합니다.\n\n페이지 우측 상단 ··· → 전체 너비 활성화 (3초)"
        if any(w in msg for w in ["가능", "할 수", "뭐야"]):
            return (
                "NotionForge가 할 수 있는 것:\n\n"
                "✅ 페이지/DB/블록 생성 + 모든 속성\n"
                "✅ DB 뷰 10종 (갤러리, 캘린더, 칸반 등)\n"
                "✅ 2단/3단 칼럼 레이아웃 + 색상 테마\n"
                "✅ 하위 페이지 + 샘플 데이터\n"
                "❌ 불가: 버튼 블록, 전체 너비"
            )
        return "궁금한 점이 있으시면 편하게 물어보세요! 또는 원하는 템플릿을 설명해주시면 바로 만들어드립니다."

    def _build_question(self, intent: IntentResult) -> str:
        lines = intent.missing_info or ["어떤 용도의 노션 템플릿을 만들어드릴까요?"]
        categories = ["📊 프로젝트 관리", "✅ 습관/목표 트래커", "📚 학습/독서 기록",
                       "🏢 업무용 (CRM, 회의록)", "🔖 북마크/자료 정리", "📝 일기/기록 노트"]
        return "\n".join(f"- {q}" for q in lines) + "\n\n인기 카테고리:\n" + "\n".join(f"  {c}" for c in categories)

    @staticmethod
    def _format_design_msg(blueprint: dict) -> str:
        meta = blueprint.get("metadata", {})
        skill = meta.get("skill_used", "?")
        method = meta.get("generation_method", "?")
        num_blocks = len(blueprint.get("blocks", []))
        num_dbs = len(blueprint.get("databases", []))
        msg = f"✅ 설계 완료: {skill} 스킬, 블록 {num_blocks}개, DB {num_dbs}개 ({method})"
        attempts = meta.get("gen_eval_attempts", 1)
        if attempts > 1:
            msg += f"\n   🔄 Gen-Eval: {attempts}회 시도"
        gen_time = meta.get("gen_eval_time", 0)
        if gen_time:
            msg += f" | ⏱️ {gen_time}s"
        return msg

    def _format_preview(self, blueprint: dict) -> str:
        meta = blueprint["metadata"]
        lines = [f"📄 **{meta['title']}** ({meta['template_type']})", f"🎨 색상: {meta['color_theme']}"]
        for db in blueprint.get("databases", []):
            lines.append(f"📊 DB: {db['title']} ({', '.join(db['properties'].keys())})")
        for sub in blueprint.get("sub_pages", []):
            lines.append(f"📁 하위: {sub['title']}")
        return "\n".join(lines)

    @staticmethod
    def _format_complete(result: dict) -> str:
        lines = [
            "✅ 템플릿 생성 완료!",
            f"📄 페이지 {len(result['pages'])}개",
            f"📊 데이터베이스 {len(result['databases'])}개",
            f"🧱 블록 {result['blocks']}개",
        ]
        if result.get("main_url"):
            lines.append(f"🔗 {result['main_url']}")
        lines.append("")
        lines.append("💡 **추가 설정 안내**")
        lines.append("• 전체 너비: 페이지 우측 상단 ··· → 전체 너비 활성화")
        if result.get("databases"):
            lines.append("• DB 뷰 변경: DB 상단 + 버튼 → 갤러리/캘린더/보드 선택")
        lines.append("")
        lines.append("💬 수정이 필요하면 말씀해주세요! (예: \"DB에 우선순위 속성 추가해줘\")")
        return "\n".join(lines)
