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

from app.agent.blueprint_generator import generate_blueprint
from app.agent.creation_executor import CreationExecutor
from app.agent.input_guardrail import validate_input
from app.agent.intent_analyzer import analyze_intent
from app.agent.modify_handler import ModifyHandler
from app.agent.quality_validator import quality_validator
from app.agent.tools.add_blocks import AddBlocksTool
from app.agent.tools.add_database_items import AddDatabaseItemsTool
from app.core.history import save_generation_record
from app.core.metrics import GenerationMetrics
from app.notion.client import NotionClient
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
        self.use_agent_loop: bool = False

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
        yield {
            "type": "progress",
            "step": "intent_done",
            "message": f"✅ 의도 파악: {intent.intent} ({intent.template_type})",
        }

        # 수정 모드 전환
        if intent.intent == "MODIFY" and self._last_result:
            async for event in self._modifier.handle_modify(message, intent, self._last_result, self._last_blueprint):
                yield event
            return

        if self._last_result and intent.intent == "CREATE":
            if self._should_switch_to_modify(message):
                yield {"type": "progress", "step": "intent_override", "message": "🔄 수정 모드로 전환합니다..."}
                async for event in self._modifier.handle_modify(
                    message, intent, self._last_result, self._last_blueprint
                ):
                    yield event
                return

        if intent.intent == "QUESTION":
            yield {"type": "ai_response", "content": self._answer_question(message)}
            return

        if intent.confidence < 0.5 and intent.missing_info:
            yield {"type": "question", "content": self._build_question(intent), "intent": intent.model_dump()}
            return

        # ── Agent Loop 모드: Plan-Execute-Reflect 직접 실행
        if self.use_agent_loop:
            metrics.start_stage("agent_loop")
            yield {"type": "progress", "step": "agent_loop", "message": "🤖 Agent Loop 모드로 직접 생성합니다..."}

            from app.agent.agent_loop import AgentLoop

            loop = AgentLoop(client=self.client, api_key=self.ai_key, ai_model=self.ai_model)
            async for event in loop.run_streaming(message, self.parent_page_id):
                if event.get("type") == "result":
                    loop_result = event["result"]
                else:
                    yield event

            metrics.end_stage()

            if not loop_result.get("success"):
                yield {"type": "error", "content": f"Agent Loop 실패: {loop_result.get('error', '알 수 없는 오류')}"}
                return

            result = {
                "pages": [{"id": loop_result.get("page_id")}],
                "databases": [],
                "blocks": loop_result.get("steps_completed", 0),
                "main_url": loop_result.get("page_url", ""),
            }
            self._last_result = result
            metrics.finish(success=True)
            save_generation_record(metrics.to_dict(), {})

            yield {"type": "complete", "content": self._format_complete(result), "result": result}
            return

        # ② AI 설계
        metrics.start_stage("blueprint_generation")
        blueprint = await self._generate_blueprint(message, metrics)
        metrics.end_stage()

        meta = blueprint.get("metadata", {})
        yield {"type": "progress", "step": "design_done", "message": self._format_design_msg(blueprint)}
        yield {"type": "blueprint_preview", "content": self._format_preview(blueprint), "blueprint": blueprint}

        # ── QualityValidator 3계층 검증
        qv_result = quality_validator.validate(blueprint)
        if not qv_result.passed and qv_result.critical_count > 0:
            critical_msgs = [i.message for i in qv_result.issues if i.severity == "critical"]
            logger.warning(f"[QualityValidator] 미통과: {critical_msgs}")

            # 치명적 이슈 시 1회 재생성 시도
            yield {
                "type": "progress",
                "step": "quality_retry",
                "message": f"⚠️ 품질 검증 미통과 (점수: {qv_result.score}/100). 재설계 중...",
            }
            blueprint = await self._generate_blueprint(message, metrics)
            qv_result = quality_validator.validate(blueprint)

        if qv_result.passed:
            yield {
                "type": "progress",
                "step": "quality_check",
                "message": f"✅ 품질 검증 통과 (점수: {qv_result.score}/100)",
            }
        else:
            yield {
                "type": "progress",
                "step": "quality_check",
                "message": f"⚠️ 품질 검증: {qv_result.score}/100 (계속 진행)",
            }

        # ── Approval Gate
        self._approval_event.clear()
        self._approval_granted = False
        yield {
            "type": "approval_request",
            "content": "템플릿 설계를 확인해주세요. 생성을 진행할까요?",
            "blueprint": blueprint,
            "quality_score": qv_result.score,
            "quality_issues": [
                {"severity": i.severity, "message": i.message, "path": i.path} for i in qv_result.issues
            ],
        }

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
            msg = (
                f"생성 실패로 롤백 완료: {', '.join(rolled)} 삭제됨.\n다시 시도해주세요."
                if rolled
                else "생성 실패. 다시 시도해주세요."
            )
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
        enhanced_msg = message
        if self.complexity != "standard":
            complexity_hint = {
                "simple": "\n[COMPLEXITY: simple — 10-15 blocks, 1 DB, minimal]",
                "advanced": "\n[COMPLEXITY: advanced — 25-40 blocks, 3-4 DB, 5+ sub_pages, dashboard layout]",
            }.get(self.complexity, "")
            enhanced_msg = message + complexity_hint
        if self.language != "ko":
            lang_hint = {
                "en": "\n[LANGUAGE: English — all text content in English]",
                "ja": "\n[LANGUAGE: Japanese — all text content in Japanese]",
            }.get(self.language, "")
            enhanced_msg += lang_hint

        use_pipeline = self.use_pipeline or self.complexity == "advanced"
        if use_pipeline:
            from app.agent.blueprint_generator import _assemble_blueprint
            from app.agent.pipeline import multi_agent_pipeline

            async for event in multi_agent_pipeline(enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model):
                if event.get("stage") == "complete":
                    blueprint = _assemble_blueprint(event.get("blueprint"))
                    blueprint["metadata"]["generation_method"] = "multi_agent_pipeline"
                    blueprint["metadata"]["skill_used"] = event.get("blueprint", {}).get("skill", "custom")
                    return blueprint

        return await generate_blueprint(
            enhanced_msg,
            ai_key=self.ai_key,
            ai_model=self.ai_model,
            conversation_history=self._conversation,
        )

    # ─── Private: Notion 생성 실행 ───

    async def _execute_creation(self, blueprint: dict) -> AsyncGenerator[dict[str, Any], None]:
        """Notion 생성 스트리밍 — CreationExecutor.execute_streaming에 위임"""
        async for event in self._executor.execute_streaming(blueprint, self.parent_page_id):
            if event.get("type") == "result":
                self._current_result = event["result"]
            else:
                yield event

    # ─── Private: 헬퍼 ───

    @staticmethod
    def _should_switch_to_modify(message: str) -> bool:
        """CREATE 의도이지만 수정 키워드가 있으면 MODIFY로 전환"""
        msg_lower = message.lower()
        modify_keywords = ["추가", "넣어", "바꿔", "변경", "삭제", "없애", "제거", "연결", "빼"]
        context_keywords = [
            "속성",
            "뷰",
            "db",
            "디비",
            "데이터베이스",
            "칼럼",
            "페이지",
            "블록",
            "수식",
            "formula",
            "d-day",
            "relation",
            "캘린더",
            "보드",
            "갤러리",
            "타임라인",
            "테이블",
            "리스트",
            "칸반",
        ]
        has_modify = any(kw in msg_lower for kw in modify_keywords)
        has_context = any(kw in msg_lower for kw in context_keywords)
        return has_modify and has_context

    def _answer_question(self, message: str) -> str:
        """QUESTION 의도 응답"""
        msg = message.lower()
        if "버튼" in msg:
            return "Notion API에서는 버튼 블록 생성이 불가능합니다.\n\n대안으로 콜아웃 블록에 아이콘을 넣어 버튼처럼 보이게 만들어드립니다."
        if any(w in msg for w in ["갤러리", "캘린더", "칸반", "뷰"]):
            return 'Views API (2026-03-19)로 갤러리, 캘린더, 칸반 뷰를 자동 생성할 수 있습니다!\n\n예: "프로젝트 보드 만들어줘, 칸반 뷰로"'
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
        categories = [
            "📊 프로젝트 관리",
            "✅ 습관/목표 트래커",
            "📚 학습/독서 기록",
            "🏢 업무용 (CRM, 회의록)",
            "🔖 북마크/자료 정리",
            "📝 일기/기록 노트",
        ]
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
            props = db.get("properties") or db.get("db_properties") or {}
            lines.append(f"📊 DB: {db['title']} ({', '.join(props.keys())})")
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
        lines.append('💬 수정이 필요하면 말씀해주세요! (예: "DB에 우선순위 속성 추가해줘")')
        return "\n".join(lines)
