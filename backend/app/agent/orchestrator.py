"""Agent Orchestrator: 사용자 요청 → 의도 분석 → Blueprint → Tool 실행 → 결과

고도화 항목:
1. 생성 완료 후 안내 메시지 (전체 너비, 뷰 변경 등)
2. 대화 맥락 유지 (후속 수정 지원)
3. 스킬 동적 로딩 (AI가 .md 읽고 Blueprint 생성)
"""

import logging

logger = logging.getLogger("notionforge.orchestrator")

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
        self._last_blueprint: dict[str, Any] | None = None

        # 사용자 설정
        self.complexity: str = "standard"  # simple, standard, advanced
        self.language: str = "ko"  # ko, en, ja
        self.use_pipeline: bool = False  # 멀티 에이전트 파이프라인 사용 여부

    async def process(self, message: str) -> AsyncGenerator[dict[str, Any], None]:
        """메인 처리 파이프라인 — 실시간 스트리밍"""

        self._conversation.append({"role": "user", "content": message})

        # ① 의도 분석
        yield {"type": "progress", "step": "intent_analysis", "message": "🔍 요청을 분석하고 있어요..."}
        intent = await analyze_intent(message)
        yield {"type": "progress", "step": "intent_done", "message": f"✅ 의도 파악: {intent.intent} ({intent.template_type})"}

        # 이전 생성 결과가 있고 수정 의도가 감지되면 멀티턴 수정 모드
        if intent.intent == "MODIFY" and self._last_result:
            async for event in self._handle_modify(message, intent):
                yield event
            return

        # 이전 결과가 있고, CREATE이지만 수정 키워드가 포함된 경우 → MODIFY로 전환
        if self._last_result and intent.intent == "CREATE":
            msg_lower = message.lower()
            modify_keywords = ["추가", "넣어", "바꿔", "변경", "삭제", "없애", "제거", "연결", "빼"]
            context_keywords = ["속성", "뷰", "db", "디비", "데이터베이스", "칼럼", "페이지", "블록",
                                "수식", "formula", "d-day", "relation", "캘린더", "보드", "갤러리",
                                "타임라인", "테이블", "리스트", "칸반"]
            has_modify = any(kw in msg_lower for kw in modify_keywords)
            has_context = any(kw in msg_lower for kw in context_keywords)
            if has_modify and has_context:
                yield {"type": "progress", "step": "intent_override", "message": "🔄 수정 모드로 전환합니다..."}
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
        complexity_label = {"simple": "간단한", "standard": "표준", "advanced": "고급"}.get(self.complexity, "표준")
        # 복잡도 + 언어 힌트를 메시지에 추가
        enhanced_msg = message
        if self.complexity != "standard":
            complexity_hint = {"simple": "\n[COMPLEXITY: simple — 10-15 blocks, 1 DB, minimal]", "advanced": "\n[COMPLEXITY: advanced — 25-40 blocks, 3-4 DB, 5+ sub_pages, dashboard layout]"}.get(self.complexity, "")
            enhanced_msg = message + complexity_hint
        if self.language != "ko":
            lang_hint = {"en": "\n[LANGUAGE: English — all text content in English]", "ja": "\n[LANGUAGE: Japanese — all text content in Japanese]"}.get(self.language, "")
            enhanced_msg += lang_hint

        # 멀티 에이전트 파이프라인 or 단일 에이전트
        # advanced 모드에서는 자동으로 파이프라인 활성화 (더 높은 품질)
        use_pipeline = self.use_pipeline or self.complexity == "advanced"
        if use_pipeline:
            yield {"type": "progress", "step": "designing", "message": f"🧠 멀티 에이전트 파이프라인으로 {complexity_label} 템플릿을 설계하고 있어요..."}
            from app.agent.pipeline import multi_agent_pipeline
            from app.agent.blueprint_generator import _assemble_blueprint
            pipeline_result = None
            async for event in multi_agent_pipeline(enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model):
                if event.get("stage") == "complete":
                    pipeline_result = event.get("blueprint")
                elif event.get("stage") == "error":
                    break
                else:
                    yield {"type": "progress", "step": event.get("stage", "pipeline"), "message": event.get("message", "")}

            if pipeline_result:
                blueprint = _assemble_blueprint(pipeline_result)
                blueprint["metadata"]["generation_method"] = "multi_agent_pipeline"
                blueprint["metadata"]["skill_used"] = pipeline_result.get("skill", "custom")
            else:
                yield {"type": "progress", "step": "designing", "message": f"🎨 AI가 {complexity_label} 템플릿을 설계하고 있어요... (단일 에이전트 폴백)"}
                blueprint = await generate_blueprint(enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model)
        else:
            yield {"type": "progress", "step": "designing", "message": f"🎨 AI가 {complexity_label} 템플릿을 설계하고 있어요..."}
            blueprint = await generate_blueprint(enhanced_msg, ai_key=self.ai_key, ai_model=self.ai_model)

        meta = blueprint.get("metadata", {})
        method = meta.get("generation_method", "?")
        skill = meta.get("skill_used", "?")
        num_blocks = len(blueprint.get("blocks", []))
        num_dbs = len(blueprint.get("databases", []))
        gen_eval_attempts = meta.get("gen_eval_attempts", 1)
        gen_eval_time = meta.get("gen_eval_time", 0)
        gen_eval_errors = meta.get("gen_eval_errors", 0)

        design_msg = f"✅ 설계 완료: {skill} 스킬, 블록 {num_blocks}개, DB {num_dbs}개 ({method})"
        if gen_eval_attempts > 1:
            design_msg += f"\n   🔄 Gen-Eval: {gen_eval_attempts}회 시도"
        if gen_eval_errors > 0:
            design_msg += f" (잔여 오류 {gen_eval_errors}개 자동 보정)"
        if gen_eval_time:
            design_msg += f" | ⏱️ {gen_eval_time}s"
        yield {"type": "progress", "step": "design_done", "message": design_msg}

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
            yield {"type": "progress", "step": "page_done", "message": f"✅ 페이지 생성됨: {main.get('icon','')} {main['title']}"}
        except Exception as e:
            yield {"type": "progress", "step": "error", "message": f"❌ 페이지 생성 실패: {str(e)[:100]}"}
            yield {"type": "error", "content": f"메인 페이지 생성 실패: {str(e)[:200]}"}
            return

        # ── Pass 1: 서브페이지 먼저 생성 (ID 확보, toggle heading에서 link_to_page 가능)
        sub_page_map: dict[str, str] = {}
        for sub in blueprint.get("sub_pages", []):
            yield {"type": "progress", "step": "sub_page", "message": f"📁 하위 페이지: {sub.get('icon','')} {sub['title']}"}
            try:
                sub_page = await self.client.create_page(
                    parent_id=main_page_id,
                    title=sub["title"],
                    icon=sub.get("icon"),
                    position="page_end",
                )
                sub_page_map[sub["title"]] = sub_page["id"]
                result["pages"].append({"id": sub_page["id"], "title": sub["title"]})
            except Exception as e:
                yield {"type": "progress", "step": "warning", "message": f"⚠️ {sub['title']} 스킵: {str(e)[:50]}"}

        # ── Pass 1.5: sub_page_ref → 실제 page_id 치환 (link_to_page 동적 주입)
        self._resolve_sub_page_refs(blueprint.get("blocks", []), sub_page_map)
        for sub in blueprint.get("sub_pages", []):
            self._resolve_sub_page_refs(sub.get("blocks", []), sub_page_map)

        # ── Pass 2: 블록 + DB 순차 삽입
        blocks = blueprint.get("blocks", [])
        databases = blueprint.get("databases", [])
        db_index = 0

        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue  # AI가 string을 넣은 경우 스킵
            block_type = block.get("type", "?")
            try:
                if block_type == "database_ref":
                    if db_index < len(databases):
                        db_spec = databases[db_index]
                        db_title = db_spec.get("title", db_spec.get("db_name", "DB"))

                        # DB 배치 전략: db_parent가 있으면 서브페이지에 생성
                        db_parent_name = db_spec.get("db_parent", "")
                        db_parent_id = main_page_id
                        if db_parent_name and db_parent_name in sub_page_map:
                            db_parent_id = sub_page_map[db_parent_name]
                            yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title} (→ {db_parent_name})"}
                        else:
                            yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title}"}

                        try:
                            db_result = await self._create_database_with_data(parent_id=db_parent_id, db_spec=db_spec)
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
                    for ref_idx in db_refs_in_col:
                        if db_index < len(databases):
                            db_spec = databases[db_index]
                            db_title = db_spec.get("title", db_spec.get("db_name", "DB"))
                            yield {"type": "progress", "step": "database", "message": f"📊 데이터베이스 생성 중: {db_title}"}
                            try:
                                db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=db_spec)
                                result["databases"].append(db_result)
                                num_props = len(db_spec.get("db_properties", db_spec.get("properties", {})))
                                yield {"type": "progress", "step": "db_created", "message": f"✅ {db_title} DB 생성됨 (속성 {num_props}개)"}

                                # 뷰 진행 표시
                                views = db_spec.get("views", [])
                                for view in views:
                                    view_type = view if isinstance(view, str) else view.get("type", "?")
                                    view_icons = {"table": "📋", "gallery": "🖼️", "board": "📊", "calendar": "📅", "timeline": "📈", "list": "📝"}
                                    yield {"type": "progress", "step": "view", "message": f"  {view_icons.get(view_type, '📋')} {view_type} 뷰 추가됨"}
                            except Exception as e:
                                yield {"type": "progress", "step": "warning", "message": f"⚠️ DB 생성 스킵: {str(e)[:80]}"}
                            db_index += 1
                    column_block = await self._build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            logger.info(f"[칼럼 블록 추가 실패] {str(e)[:100]}")
                    yield {"type": "progress", "step": "block_done", "message": "✅ 칼럼 레이아웃 생성됨"}

                    # column 안에 있던 DB를 page level에 inline으로 표시
                    # (inline DB는 column 안에 들어갈 수 없으므로 column 아래에 배치)
                    col_db_refs = self._collect_db_refs_in_columns(block)
                    for ref_idx in col_db_refs:
                        created_dbs = result.get("databases", [])
                        if ref_idx < len(created_dbs):
                            pass  # DB는 이미 inline으로 생성됨 (parent=main_page_id)

                elif block_type == "linked_view":
                    # 링크드 DB 뷰 (같은 DB를 다른 필터로 표시)
                    linked_db_idx = block.get("db_index", 0)
                    created_dbs = result.get("databases", [])
                    if linked_db_idx < len(created_dbs):
                        db_id = created_dbs[linked_db_idx].get("id", "")
                        view_type = block.get("view_type", "table")
                        view_title = block.get("title", view_type)
                        view_filter = block.get("filter")
                        if db_id:
                            yield {"type": "progress", "step": "linked_view", "message": f"🔗 링크드 뷰: {view_title} ({view_type})"}
                            try:
                                await self.client.create_linked_view(
                                    source_database_id=db_id,
                                    target_page_id=main_page_id,
                                    view_type=view_type,
                                    title=view_title,
                                    filters=view_filter,
                                )
                                result["blocks"] += 1
                            except Exception as e:
                                logger.info(f"[링크드 뷰 스킵] {view_title}: {str(e)[:80]}")

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
                        logger.info(f"[블록 스킵] {block_type}: {str(e)[:80]}")

            except Exception as e:
                logger.info(f"[블록 처리 오류] {block_type}: {str(e)[:80]}")

        # 남은 DB
        while db_index < len(databases):
            try:
                db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=databases[db_index])
                result["databases"].append(db_result)
            except Exception:
                pass
            db_index += 1

        # ── Pass 3: 하위 페이지 블록 내용 채우기
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
                        yield {"type": "progress", "step": "sub_page_blocks", "message": f"  📝 {sub.get('icon','')} {sub['title']} 내용 추가됨"}
                except Exception as e:
                    logger.info(f"[하위 페이지 블록 스킵] {sub['title']}: {str(e)[:80]}")
            else:
                # blocks가 없으면 기본 블록 자동 생성
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
                    yield {"type": "progress", "step": "sub_page_blocks", "message": f"  📝 {sub.get('icon','')} {sub['title']} 기본 내용 추가됨"}
                except Exception as e:
                    logger.info(f"[하위 페이지 기본 블록 실패] {sub['title']}: {str(e)[:80]}")

        # ── Pass 4: Relation / Rollup / Formula 후처리 (DB 간 연결)
        await self._post_process_relations(blueprint, result, lambda msg: None)
        relation_count = sum(1 for db in databases for _, v in db.get("properties", db.get("db_properties", {})).items()
                             if isinstance(v, dict) and v.get("type") in ("relation", "rollup", "formula") or
                             (isinstance(v, dict) and "target_db_index" in v))
        if relation_count > 0:
            yield {"type": "progress", "step": "relations", "message": f"🔗 DB 간 연결 완료 (Relation/Rollup/Formula {relation_count}개)"}

        # ── Pass 5: Post-Creation Validation (생성 후 검증)
        validation_issues = await self._validate_creation(main_page_id, blueprint, result)
        if validation_issues:
            yield {"type": "progress", "step": "validation", "message": f"🔍 검증: {len(validation_issues)}개 항목 확인"}
            for issue in validation_issues[:3]:
                yield {"type": "progress", "step": "validation_detail", "message": f"  ⚠️ {issue}"}
        else:
            yield {"type": "progress", "step": "validation", "message": "✅ 생성 결과 검증 완료 — 모든 항목 정상"}

        # 결과 저장
        self._last_intent = intent
        self._last_result = result
        self._last_blueprint = blueprint

        # ④ 완료
        yield {"type": "complete", "content": self._format_complete(result), "result": result}

    async def _handle_modify(self, message: str, intent: IntentResult) -> AsyncGenerator[dict[str, Any], None]:
        """후속 수정 처리 — AI 기반 멀티턴 대화형 수정

        지원하는 수정:
        - 속성 추가/삭제/변경
        - 뷰 추가/변경
        - DB 추가
        - Relation/Formula 연결
        - 서브페이지 추가
        - 블록 추가
        """
        msg = message.lower()
        result = self._last_result

        if not result or not result.get("pages"):
            yield {"type": "ai_response", "content": "수정할 템플릿이 없습니다. 먼저 템플릿을 생성해주세요."}
            return

        main_page_id = result["pages"][0]["id"]
        has_dbs = bool(result.get("databases"))

        # ── 1. 속성 삭제/제거
        if has_dbs and any(w in msg for w in ["삭제", "없애", "제거", "빼"]) and "속성" in msg:
            yield {"type": "progress", "step": "modifying", "message": "🗑️ 속성을 삭제하고 있어요..."}
            db_id = self._pick_target_db(msg, result)
            prop_name = self._extract_property_name(message)
            if prop_name:
                try:
                    await self.client.update_database(db_id, {"properties": {prop_name: None}})
                    yield {"type": "complete", "content": f"✅ \"{prop_name}\" 속성 삭제 완료!"}
                except Exception as e:
                    yield {"type": "error", "content": f"속성 삭제 실패: {str(e)[:100]}"}
            else:
                yield {"type": "question", "content": "어떤 속성을 삭제할까요? 속성 이름을 정확히 알려주세요."}
            return

        # ── 2. 속성 추가
        if has_dbs and "속성" in msg and any(w in msg for w in ["추가", "넣어", "만들어"]):
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
                yield {"type": "question", "content": "어떤 속성을 추가할까요?\n\n예시:\n- \"우선순위 select 속성 추가해줘 (높음/중간/낮음)\"\n- \"마감일 날짜 속성 추가해줘\"\n- \"메모 텍스트 속성 추가해줘\""}
            return

        # ── 3. 뷰 추가/변경
        if has_dbs and any(w in msg for w in ["뷰", "보드", "캘린더", "갤러리", "타임라인", "테이블", "칸반"]):
            yield {"type": "progress", "step": "modifying", "message": "📋 뷰를 추가하고 있어요..."}
            db_id = self._pick_target_db(msg, result)
            view_type = self._detect_view_type(msg)
            view_title = {"board": "칸반 보드", "calendar": "캘린더", "gallery": "갤러리", "timeline": "타임라인", "table": "테이블", "list": "리스트"}.get(view_type, view_type)

            group_by = None
            view_config_spec = {"type": view_type}
            if view_type == "board":
                group_by = {"property": "상태"}
                view_config_spec["cover"] = {"type": "page_cover"}
                view_config_spec["cover_size"] = "medium"
            elif view_type == "gallery":
                view_config_spec["cover"] = {"type": "page_cover"}
                view_config_spec["cover_size"] = "medium"

            configuration = self._build_view_configuration(view_config_spec)

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
            return

        # ── 4. DB 추가 (새 데이터베이스)
        if any(w in msg for w in ["db ", "데이터베이스", "디비"]) and any(w in msg for w in ["추가", "만들어", "생성"]):
            yield {"type": "progress", "step": "modifying", "message": "📊 새 데이터베이스를 생성 중..."}
            # AI에게 DB 설계 요청
            try:
                from app.agent.blueprint_generator import generate_blueprint
                bp = await generate_blueprint(f"단일 데이터베이스만 만들어줘: {message}", ai_key=self.ai_key, ai_model=self.ai_model)
                if bp.get("databases"):
                    db_spec = bp["databases"][0]
                    db_result = await self._create_database_with_data(parent_id=main_page_id, db_spec=db_spec)
                    result["databases"].append(db_result)
                    yield {"type": "complete", "content": f"✅ \"{db_spec['title']}\" 데이터베이스 추가 완료!\n📊 속성 {len(db_spec.get('properties', {}))}개, 샘플 데이터 포함"}
                else:
                    yield {"type": "error", "content": "DB 설계 실패. 다시 시도해주세요."}
            except Exception as e:
                yield {"type": "error", "content": f"DB 추가 실패: {str(e)[:100]}"}
            return

        # ── 5. Relation 연결
        if has_dbs and any(w in msg for w in ["연결", "relation", "릴레이션", "관계"]):
            yield {"type": "progress", "step": "modifying", "message": "🔗 DB를 연결하고 있어요..."}
            if len(result["databases"]) < 2:
                yield {"type": "question", "content": "Relation 연결은 2개 이상의 DB가 필요합니다.\n먼저 DB를 추가해주세요! (예: \"태스크 DB 추가해줘\")"}
                return

            # 첫 번째 DB에 두 번째 DB로의 relation 추가
            source_db = result["databases"][0]
            target_db = result["databases"][1]

            # 메시지에서 더 구체적인 DB 지정 시도
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
                await self.client.update_database(source_db["id"], {
                    "properties": {
                        relation_name: {
                            "relation": {
                                "database_id": target_db["id"],
                                "single_property": {},
                            }
                        }
                    }
                })
                yield {"type": "complete", "content": f"✅ Relation 연결 완료!\n🔗 {source_db['title']} → {target_db['title']}\n📊 \"{relation_name}\" 속성 추가됨"}
            except Exception as e:
                yield {"type": "error", "content": f"Relation 연결 실패: {str(e)[:100]}"}
            return

        # ── 6. Formula 추가
        if has_dbs and any(w in msg for w in ["수식", "formula", "포뮬라", "계산", "d-day", "디데이"]):
            yield {"type": "progress", "step": "modifying", "message": "🔢 수식 속성을 추가하고 있어요..."}
            db_id = self._pick_target_db(msg, result)
            formula = self._detect_formula(msg)
            if formula:
                try:
                    await self.client.update_database(db_id, {
                        "properties": {
                            formula["name"]: {
                                "formula": {"expression": formula["expression"]}
                            }
                        }
                    })
                    yield {"type": "complete", "content": f"✅ 수식 속성 추가 완료!\n🔢 \"{formula['name']}\" = {formula['expression'][:50]}"}
                except Exception as e:
                    yield {"type": "error", "content": f"수식 추가 실패: {str(e)[:100]}"}
            else:
                yield {"type": "question", "content": "어떤 수식을 추가할까요?\n\n예시:\n- \"D-Day 수식 추가해줘\" (마감일까지 남은 일수)\n- \"진행률 수식 추가해줘\" (상태 기반 %)\n- \"총액 수식 추가해줘\" (단가 × 수량)"}
            return

        # ── 7. 서브페이지 추가
        if any(w in msg for w in ["하위 페이지", "서브페이지", "페이지 추가", "새 페이지"]):
            yield {"type": "progress", "step": "modifying", "message": "📁 하위 페이지를 추가하고 있어요..."}
            import re
            # 제목 추출
            title_match = re.search(r"[\"']([^\"']+)[\"']", message)
            page_title = title_match.group(1) if title_match else message.replace("하위 페이지", "").replace("서브페이지", "").replace("추가해줘", "").replace("만들어줘", "").strip()
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
                # 기본 내용 추가
                default_blocks = [
                    bb.callout(f"{page_title} 페이지입니다.", icon="📄", color="blue_background"),
                    bb.divider(),
                    bb.heading(f"📋 {page_title} 개요", level=2),
                    bb.paragraph("이 페이지의 내용을 자유롭게 작성해보세요."),
                ]
                await self.client.add_blocks(sub_page["id"], default_blocks)
                result["pages"].append({"id": sub_page["id"], "title": page_title})
                yield {"type": "complete", "content": f"✅ \"{page_title}\" 하위 페이지 추가 완료!"}
            except Exception as e:
                yield {"type": "error", "content": f"페이지 추가 실패: {str(e)[:100]}"}
            return

        # ── 8. 블록 추가
        if any(w in msg for w in ["블록", "섹션", "내용", "텍스트", "faq", "가이드"]) and any(w in msg for w in ["추가", "넣어"]):
            yield {"type": "progress", "step": "modifying", "message": "🧱 블록을 추가하고 있어요..."}
            blocks_to_add = self._parse_block_request(message)
            try:
                notion_blocks = [spec_to_block(b) for b in blocks_to_add]
                await self.client.add_blocks(main_page_id, notion_blocks)
                yield {"type": "complete", "content": f"✅ 블록 {len(blocks_to_add)}개 추가 완료!"}
            except Exception as e:
                yield {"type": "error", "content": f"블록 추가 실패: {str(e)[:100]}"}
            return

        # ── 9. 뷰 삭제
        if has_dbs and any(w in msg for w in ["뷰", "보드", "캘린더", "갤러리", "타임라인"]) and any(w in msg for w in ["삭제", "없애", "제거", "빼"]):
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
                    view_name = {"board": "칸반 보드", "calendar": "캘린더", "gallery": "갤러리", "timeline": "타임라인", "table": "테이블"}.get(target_view_type, target_view_type)
                    yield {"type": "complete", "content": f"✅ {view_name} 뷰 삭제 완료!"}
                else:
                    yield {"type": "error", "content": f"해당 타입의 뷰를 찾을 수 없습니다."}
            except Exception as e:
                yield {"type": "error", "content": f"뷰 삭제 실패: {str(e)[:100]}"}
            return

        # ── 10. 블록 삭제 (섹션/내용 삭제)
        if any(w in msg for w in ["블록", "섹션", "내용"]) and any(w in msg for w in ["삭제", "없애", "제거", "빼"]):
            yield {"type": "progress", "step": "modifying", "message": "🗑️ 블록을 삭제하고 있어요..."}
            import re
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
                        yield {"type": "complete", "content": f"✅ \"{target_text}\" 포함 블록 삭제 완료!"}
                    else:
                        yield {"type": "error", "content": f"\"{target_text}\"을 포함하는 블록을 찾을 수 없습니다."}
                except Exception as e:
                    yield {"type": "error", "content": f"블록 삭제 실패: {str(e)[:100]}"}
            else:
                yield {"type": "question", "content": "어떤 블록을 삭제할까요?\n삭제할 블록의 텍스트를 따옴표로 감싸서 알려주세요.\n예: \"FAQ\" 블록 삭제해줘"}
            return

        # ── 기타: AI에게 수정 의도 분석 요청 (폴백)
        yield {
            "type": "question",
            "content": (
                "어떤 수정을 원하시나요?\n\n"
                "**속성 관련:**\n"
                "- \"우선순위 select 속성 추가해줘 (높음/중간/낮음)\"\n"
                "- \"예산 속성 삭제해줘\"\n\n"
                "**뷰 관련:**\n"
                "- \"캘린더 뷰 추가해줘\"\n"
                "- \"칸반 보드 뷰 추가해줘\"\n\n"
                "**DB 관련:**\n"
                "- \"태스크 DB 추가해줘\"\n"
                "- \"프로젝트랑 태스크 연결해줘\"\n\n"
                "**수식:**\n"
                "- \"D-Day 수식 추가해줘\"\n"
                "- \"진행률 계산 추가해줘\"\n\n"
                "**삭제:**\n"
                "- \"캘린더 뷰 삭제해줘\"\n"
                "- \"'FAQ' 블록 삭제해줘\"\n\n"
                "**구조:**\n"
                "- \"새 하위 페이지 추가해줘\"\n"
                "- \"FAQ 섹션 추가해줘\""
            ),
        }

    def _pick_target_db(self, msg: str, result: dict) -> str:
        """메시지에서 대상 DB 식별. 이름이 언급되지 않으면 첫 번째 DB."""
        for db in result.get("databases", []):
            title = db.get("title", "").lower()
            if title and title in msg:
                return db["id"]
        return result["databases"][0]["id"] if result.get("databases") else ""

    def _extract_property_name(self, message: str) -> str:
        """메시지에서 속성 이름 추출"""
        import re
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
            "보드": "board", "칸반": "board", "kanban": "board", "board": "board",
            "캘린더": "calendar", "달력": "calendar", "calendar": "calendar",
            "갤러리": "gallery", "gallery": "gallery",
            "타임라인": "timeline", "timeline": "timeline",
            "리스트": "list", "list": "list",
            "테이블": "table", "table": "table",
        }
        for keyword, view_type in view_map.items():
            if keyword in msg:
                return view_type
        return "table"

    def _build_view_configuration(self, view_spec: dict) -> dict | None:
        """AI blueprint의 view spec에서 Views API configuration 객체를 빌드.

        AI가 view spec에 넣은 세부 설정(cover, chart_type, date_property 등)을
        Notion Views API의 configuration 포맷으로 변환.
        설정이 없으면 None 반환 (기본값 사용).
        """
        vtype = view_spec.get("type", "table")
        config: dict[str, Any] = {"type": vtype}
        has_config = False

        if vtype == "board":
            # cover 설정
            cover = view_spec.get("cover")
            if cover:
                config["cover"] = cover if isinstance(cover, dict) else {"type": cover}
                has_config = True
            cover_size = view_spec.get("cover_size")
            if cover_size:
                config["cover_size"] = cover_size
                has_config = True
            cover_aspect = view_spec.get("cover_aspect")
            if cover_aspect:
                config["cover_aspect"] = cover_aspect
                has_config = True
            card_layout = view_spec.get("card_layout")
            if card_layout:
                config["card_layout"] = card_layout
                has_config = True

        elif vtype == "gallery":
            cover = view_spec.get("cover")
            if cover:
                config["cover"] = cover if isinstance(cover, dict) else {"type": cover}
                has_config = True
            cover_size = view_spec.get("cover_size", "medium")
            if cover:
                config["cover_size"] = cover_size
                config["cover_aspect"] = view_spec.get("cover_aspect", "cover")
                has_config = True
            card_layout = view_spec.get("card_layout")
            if card_layout:
                config["card_layout"] = card_layout
                has_config = True

        elif vtype == "calendar":
            date_prop = view_spec.get("date_property") or view_spec.get("date_property_id")
            if date_prop:
                config["date_property_id"] = date_prop
                has_config = True
            show_weekends = view_spec.get("show_weekends")
            if show_weekends is not None:
                config["show_weekends"] = show_weekends
                has_config = True

        elif vtype == "chart":
            chart_type = view_spec.get("chart_type")
            if chart_type:
                config["chart_type"] = chart_type
                has_config = True
            x_axis = view_spec.get("x_axis")
            if x_axis:
                config["x_axis"] = x_axis
                has_config = True
            y_axis = view_spec.get("y_axis")
            if y_axis:
                config["y_axis"] = y_axis
                has_config = True
            color_theme = view_spec.get("color_theme")
            if color_theme:
                config["color_theme"] = color_theme
                has_config = True
            if view_spec.get("show_data_labels") is not None:
                config["show_data_labels"] = view_spec["show_data_labels"]
                has_config = True
            height = view_spec.get("height")
            if height:
                config["height"] = height
                has_config = True

        elif vtype == "timeline":
            date_prop = view_spec.get("date_property") or view_spec.get("date_property_id")
            if date_prop:
                config["date_property_id"] = date_prop
                has_config = True
            end_date = view_spec.get("end_date_property_id")
            if end_date:
                config["end_date_property_id"] = end_date
                has_config = True
            arrows_by = view_spec.get("arrows_by")
            if arrows_by:
                config["arrows_by"] = arrows_by
                has_config = True
            zoom = view_spec.get("zoom_level")
            if zoom:
                config["preference"] = {"zoom_level": zoom}
                has_config = True

        elif vtype == "table":
            wrap_cells = view_spec.get("wrap_cells")
            if wrap_cells is not None:
                config["wrap_cells"] = wrap_cells
                has_config = True
            frozen = view_spec.get("frozen_column_index")
            if frozen is not None:
                config["frozen_column_index"] = frozen
                has_config = True

        elif vtype == "map":
            map_by = view_spec.get("map_by")
            if map_by:
                config["map_by"] = map_by
                has_config = True
            height = view_spec.get("height")
            if height:
                config["height"] = height
                has_config = True

        elif vtype == "form":
            if view_spec.get("anonymous_submissions") is not None:
                config["anonymous_submissions"] = view_spec["anonymous_submissions"]
                has_config = True
            permissions = view_spec.get("submission_permissions")
            if permissions:
                config["submission_permissions"] = permissions
                has_config = True

        return config if has_config else None

    def _detect_formula(self, msg: str) -> dict[str, str] | None:
        """메시지에서 수식 패턴 감지"""
        if any(w in msg for w in ["d-day", "디데이", "남은 일", "마감까지"]):
            return {"name": "D-Day", "expression": 'dateBetween(prop("마감일"), now(), "days")'}
        if any(w in msg for w in ["진행률", "진행율", "progress"]):
            return {"name": "진행률", "expression": 'if(prop("상태") == "완료", 100, if(prop("상태") == "진행 중", 50, 0))'}
        if any(w in msg for w in ["총액", "합계", "total", "총"]) and any(w in msg for w in ["단가", "수량", "가격"]):
            return {"name": "총액", "expression": 'prop("단가") * prop("수량")'}
        if any(w in msg for w in ["상태 이모지", "체크", "완료 표시"]):
            return {"name": "상태 표시", "expression": 'if(prop("완료"), "✅", "⬜")'}
        if any(w in msg for w in ["지연", "overdue", "초과"]):
            return {"name": "지연 여부", "expression": 'if(prop("마감일") < now(), "⚠️ 지연", "정상")'}
        # 사용자가 직접 수식을 지정한 경우
        import re
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
            import re
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

    async def _validate_creation(self, page_id: str, blueprint: dict, result: dict) -> list[str]:
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

    @staticmethod
    def _resolve_sub_page_refs(blocks: list[dict], sub_page_map: dict[str, str]) -> None:
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
                AgentOrchestrator._resolve_sub_page_refs(children, sub_page_map)

            # column_list의 columns 처리
            if block.get("type") == "column_list":
                for col in block.get("columns", []):
                    if isinstance(col, list):
                        AgentOrchestrator._resolve_sub_page_refs(col, sub_page_map)

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
            logger.info(f"[MODIFY 페이지 생성 실패] {e}")
            return result

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
                logger.info(f"[하위 페이지 생성 스킵] {sub.get('title', '?')}: {str(e)[:100]}")

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
                            logger.info(f"[DB 생성 스킵] {str(e)[:100]}")
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
                                logger.info(f"[칼럼 내 DB 스킵] {str(e)[:100]}")
                            db_index += 1

                    column_block = await self._build_column_with_db(block, main_page_id, sub_page_map, result)
                    if column_block:
                        try:
                            await self.client.add_blocks(main_page_id, [column_block])
                            result["blocks"] += 1
                        except Exception as e:
                            logger.info(f"[칼럼 블록 스킵] {str(e)[:100]}")

                else:
                    notion_block = spec_to_block(block)
                    try:
                        await self.client.add_blocks(main_page_id, [notion_block])
                        result["blocks"] += 1
                    except Exception as e:
                        logger.info(f"[블록 스킵] {block.get('type', '?')}: {str(e)[:100]}")

            except Exception as e:
                logger.info(f"[블록 처리 오류] {block.get('type', '?')}: {str(e)[:100]}")

        # 남은 DB 추가
        while db_index < len(databases):
            try:
                db_result = await self._create_database_with_data(
                    parent_id=main_page_id,
                    db_spec=databases[db_index],
                )
                result["databases"].append(db_result)
            except Exception as e:
                logger.info(f"[DB 생성 스킵] {str(e)[:100]}")
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
                    logger.info(f"[하위 페이지 블록 스킵] {sub['title']}: {str(e)[:80]}")

        return result

    async def _post_process_relations(self, blueprint: dict, result: dict, log_fn) -> None:
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

    async def _create_database_with_data(self, parent_id: str, db_spec: dict) -> dict[str, Any]:
        """DB 생성 + 샘플 데이터 + 뷰 자동 생성"""
        # relation/rollup/formula는 후처리에서 추가 (target DB ID 필요)
        deferred_prop_names: set[str] = set()
        filtered_props = {}
        for k, v in db_spec["properties"].items():
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
                configuration = self._build_view_configuration(view_spec)
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
                logger.info(f"[뷰 생성 스킵] {view.get('type', '?')}: {str(e)[:80]}")

        return {"id": db_id, "title": db_spec["title"], "views": len(views)}

    async def _build_column_with_db(self, block: dict, page_id: str, sub_page_map: dict, result: dict) -> dict | None:
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

    def _collect_db_refs_in_columns(self, block: dict) -> list[int]:
        refs = []
        for col in block.get("columns", []):
            col_items = col if isinstance(col, list) else col.get("blocks", []) if isinstance(col, dict) else []
            for b in col_items:
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
