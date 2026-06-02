"""AI 자유 설계 Blueprint Generator (dev-2 v3)

핵심 변경: AI가 blocks[] 배열도 직접 생성
- 하드코딩 빌더 함수 7개 제거
- AI가 유저 요청 복잡도에 따라 블록 수/구조를 자유롭게 결정
- 스킬 .md는 AI에게 규칙/가이드만 제공
"""

import logging

logger = logging.getLogger("notionforge.blueprint_generator")

import json
import random as _random
from datetime import datetime, timezone
from pathlib import Path as _Path
from typing import Any

from app.agent.layout_router import layout_router
from app.agent.post_processor import blueprint_validator
from app.agent.prompt_assembler import prompt_assembler
from app.agent.skill_router import build_skill_guide as _build_skill_guide_async
from app.skills import get_tool_enum_description

# ============================================================
# Cover URL 로딩
# ============================================================


def _load_cover_urls() -> dict[str, list[str]]:
    p = _Path(__file__).parent / "data" / "cover_urls.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        # 하위 호환: string → list 변환
        return {k: (v if isinstance(v, list) else [v]) for k, v in data.items()}
    return {"default": ["https://images.unsplash.com/photo-1557683316-973673baf926?w=1600"]}


COVER_URLS: dict[str, list[str]] = _load_cover_urls()


def _pick_cover(category: str, color: str = "default") -> str:
    """카테고리/색상에 맞는 커버 URL을 랜덤 선택"""
    urls = COVER_URLS.get(category) or COVER_URLS.get(color) or COVER_URLS.get("default", [])
    return _random.choice(urls) if urls else ""


# ============================================================
# Fallback 템플릿 (JSON에서 로딩)
# ============================================================


def _load_fallback_templates() -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    p = _Path(__file__).parent / "data" / "fallback_templates.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return data["templates"], data["keywords"]


FALLBACK_TEMPLATES, FALLBACK_KEYWORDS = _load_fallback_templates()


# ============================================================
# Gen-Eval 검증
# ============================================================


def _evaluate_ai_output(content: dict[str, Any]) -> tuple[bool, list[str]]:
    """Gen-Eval: AI 출력의 구조적 결함을 검증. (pass, errors) 반환."""
    errors: list[str] = []

    # Level 0: 필수 필드 존재
    if not content.get("databases") and not content.get("db_properties"):
        errors.append("CRITICAL: 'databases' 또는 'db_properties' 필드가 없습니다. 최소 1개 DB가 필요합니다.")

    if not content.get("blocks"):
        errors.append("CRITICAL: 'blocks' 배열이 비어있습니다. 최소 3개 블록이 필요합니다.")

    # Level 1: 블록 구조 검증
    blocks = content.get("blocks", [])
    for i, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue  # string 등 잘못된 타입 스킵
        btype = block.get("type")
        if not btype:
            errors.append(f"blocks[{i}]: 'type' 필드가 없습니다.")
            continue
        if btype == "database_ref" and "db_index" not in block:
            errors.append(f"blocks[{i}]: database_ref에 'db_index'가 없습니다.")
        if btype == "column_list":
            cols = block.get("columns", [])
            for ci, col in enumerate(cols):
                if isinstance(col, list):
                    for item in col:
                        if item.get("type") == "database_ref":
                            errors.append(
                                f"blocks[{i}].columns[{ci}]: database_ref가 column_list 안에 있습니다. page level로 이동 필요."
                            )

    # Level 2: DB 구조 검증
    for di, db in enumerate(content.get("databases", [])):
        props = db.get("db_properties", db.get("properties", {}))
        if not props:
            errors.append(f"databases[{di}]: 속성(properties)이 비어있습니다.")
        has_title = any(v == "title" or (isinstance(v, dict) and v.get("type") == "title") for v in props.values())
        if not has_title:
            errors.append(f"databases[{di}]: title 타입 속성이 없습니다. 최소 1개 필요합니다.")
        samples = db.get("sample_items", [])
        if len(samples) < 3:
            errors.append(f"databases[{di}]: sample_items가 {len(samples)}개입니다. 최소 3개 필요합니다.")

    # Level 3: db_index 범위 검증
    db_count = len(content.get("databases", []))
    for i, block in enumerate(blocks):
        if block.get("type") == "database_ref":
            idx = block.get("db_index", 0)
            if idx >= db_count:
                errors.append(f"blocks[{i}]: db_index={idx}이지만 databases는 {db_count}개뿐입니다.")

    # Level 4: 디자인 품질 검증
    block_types = {b.get("type") for b in blocks if isinstance(b, dict)}
    has_callout = "callout" in block_types
    has_heading = any(t in block_types for t in ("heading_1", "heading_2"))
    if not has_callout:
        errors.append("디자인: callout 블록이 없습니다. 환영 메시지나 안내 카드를 추가하세요.")
    if not has_heading and len(blocks) >= 5:
        errors.append("디자인: heading 블록이 없습니다. 섹션 구분을 위해 heading을 추가하세요.")

    # 서브페이지 아이콘 검증
    for si, sub in enumerate(content.get("sub_pages", [])):
        if not sub.get("icon"):
            errors.append(f"sub_pages[{si}]: icon이 없습니다. 이모지 아이콘을 추가하세요.")

    # Level 5: Relation / Formula / Rollup 무결성 검증
    databases = content.get("databases", [])
    for di, db in enumerate(databases):
        props = db.get("db_properties", db.get("properties", {}))
        for pname, pspec in props.items():
            if not isinstance(pspec, dict):
                continue
            prop_type = pspec.get("type", "")

            if prop_type == "relation":
                target_idx = pspec.get("target_db_index")
                if target_idx is None:
                    errors.append(f"databases[{di}].{pname}: relation에 target_db_index가 없습니다.")
                elif not isinstance(target_idx, int) or target_idx < 0 or target_idx >= db_count:
                    errors.append(
                        f"databases[{di}].{pname}: target_db_index={target_idx}가 유효 범위(0~{db_count - 1})를 벗어납니다."
                    )
                elif target_idx == di:
                    errors.append(f"databases[{di}].{pname}: 자기 자신을 참조하는 relation은 지원하지 않습니다.")

            elif prop_type == "formula":
                expr = pspec.get("expression", "")
                if not expr:
                    errors.append(f"databases[{di}].{pname}: formula에 expression이 없습니다.")

            elif prop_type == "rollup":
                if not pspec.get("relation_property"):
                    errors.append(f"databases[{di}].{pname}: rollup에 relation_property가 없습니다.")
                rel_prop = pspec.get("relation_property", "")
                if rel_prop and rel_prop not in props:
                    errors.append(
                        f"databases[{di}].{pname}: rollup의 relation_property '{rel_prop}'가 같은 DB에 존재하지 않습니다."
                    )

    is_pass = len(errors) == 0
    return is_pass, errors


# ============================================================
# 메인 함수
# ============================================================


async def _finalize_blueprint(blueprint: dict[str, Any], ai_key: str, ai_model: str) -> dict[str, Any]:
    """성공 경로 마무리 — 설정 시 LLM 주관 심사를 metadata에 부착(비차단).

    심사 실패/미설정/예산초과 시 blueprint를 그대로 반환한다(생성은 막지 않음).
    """
    try:
        from app.config import settings

        if getattr(settings, "enable_llm_judge", True):
            from app.agent.premium_judge import judge_blueprint

            verdict = await judge_blueprint(blueprint, ai_key=ai_key, ai_model=ai_model)
            if verdict is not None:
                blueprint.setdefault("metadata", {}).update(verdict.to_metadata())
    except Exception as e:
        logger.info(f"[Judge 스킵] {str(e)[:80]}")
    return blueprint


async def generate_blueprint(
    user_message: str,
    ai_key: str = "",
    ai_model: str = "",
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Gen-Eval 피드백 루프: AI 생성 → 검증 → 실패 시 에러 피드백 → 재생성 (최대 3회)"""
    import time

    from app.agent.memory import Episode, memory
    from app.agent.providers.router import ProviderRouter

    provider = ProviderRouter.resolve_with_fallback(api_key=ai_key, ai_model=ai_model)
    skill_guide, skill_match = await _build_skill_guide_async(user_message, provider=provider)

    memory_context = memory.build_memory_context(skill=skill_match.skill_id or "", query=user_message)
    if memory_context:
        skill_guide += f"\n\n{memory_context}"

    # 도메인 매칭 우수 예시 주입 (Phase A5) — 멀티DB+집계 구조 모방 유도 (벡터 아님, 키워드 매칭)
    from app.agent.exemplar_retriever import build_exemplar_hint

    exemplar_hint = build_exemplar_hint(user_message)
    if exemplar_hint:
        skill_guide += f"\n\n{exemplar_hint}"

    max_retries = 3
    feedback_context = ""
    best_content: dict[str, Any] | None = None
    best_error_count = 999

    for attempt in range(max_retries):
        t0 = time.time()
        try:
            # 피드백이 있으면 유저 메시지에 추가
            enhanced_message = user_message
            if feedback_context:
                enhanced_message = (
                    f"{user_message}\n\n"
                    f"[SYSTEM FEEDBACK — 이전 출력에서 다음 오류가 발견되었습니다. 반드시 수정하세요]\n"
                    f"{feedback_context}"
                )

            ai_content = await _call_ai_for_content(
                enhanced_message,
                ai_key=ai_key,
                ai_model=ai_model,
                extra_context=skill_guide,
                conversation_history=conversation_history,
            )
            elapsed = time.time() - t0

            if not ai_content or (not ai_content.get("databases") and not ai_content.get("db_properties")):
                logger.info(f"[Gen-Eval 시도 {attempt + 1}/{max_retries}] AI 응답 파싱 실패 ({elapsed:.1f}s)")
                feedback_context = "JSON 파싱 실패. 반드시 유효한 JSON으로 응답하세요. databases 배열이 필수입니다."
                continue

            # Pydantic Structured Output 검증
            from app.schemas.blueprint import validate_ai_content

            ai_content, pydantic_errors = validate_ai_content(ai_content)
            if pydantic_errors:
                logger.info(f"[Pydantic 검증] {len(pydantic_errors)}개 오류: {pydantic_errors}")

            # Evaluate: 구조적 결함 검증
            is_pass, eval_errors = _evaluate_ai_output(ai_content)
            eval_errors.extend(pydantic_errors)

            # Level 6: CreationExecutor 무결성 검증 (relation/rollup/db_index 교차 검증)
            from app.agent.creation_executor import CreationExecutor

            integrity_issues = CreationExecutor.validate_blueprint_integrity(
                {"main_page": ai_content.get("main_page", {"title": "temp"}), **ai_content}
            )
            if integrity_issues:
                eval_errors.extend([f"무결성: {issue}" for issue in integrity_issues])

            is_pass = len(eval_errors) == 0

            if is_pass:
                # 검증 통과 → Post-processor 보정 → 반환
                ai_content = blueprint_validator.validate_and_fix(ai_content)
                blueprint = _assemble_blueprint(ai_content, user_message)
                blueprint["metadata"]["generation_method"] = "ai_dynamic"
                blueprint["metadata"]["skill_used"] = skill_match.skill_id or ai_content.get("skill", "custom")
                blueprint["metadata"]["skill_match_method"] = skill_match.method
                blueprint["metadata"]["gen_eval_attempts"] = attempt + 1
                blueprint["metadata"]["gen_eval_time"] = round(elapsed, 1)
                logger.info(f"[Gen-Eval 통과] 시도 {attempt + 1}/{max_retries}, {elapsed:.1f}s")
                memory.save_episode(
                    Episode(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        user_message=user_message[:200],
                        skill_used=skill_match.skill_id or "custom",
                        layout=layout_router.route(user_message).layout,
                        success=True,
                        gen_eval_attempts=attempt + 1,
                    )
                )
                return await _finalize_blueprint(blueprint, ai_key, ai_model)

            # 검증 실패 → 에러를 피드백으로 구성
            error_count = len(eval_errors)
            logger.info(f"[Gen-Eval 시도 {attempt + 1}/{max_retries}] 검증 실패: {error_count}개 오류 ({elapsed:.1f}s)")
            for err in eval_errors[:5]:
                logger.info(f"  - {err}")

            # 최선의 결과 추적 (Circuit Breaker: 가장 오류 적은 결과 보관)
            if error_count < best_error_count:
                best_error_count = error_count
                best_content = ai_content

            # 피드백 구성: 에러 메시지를 AI에게 다시 전달
            feedback_context = "\n".join(eval_errors[:8])

            # 전략 변경: 마지막 재시도에서는 구조 안정화 힌트 추가
            if attempt == max_retries - 2:
                feedback_context += (
                    "\n\n[STRATEGY CHANGE] 이전 시도들이 실패했습니다. "
                    "오류를 수정하는 데 집중하세요. databases 배열의 DB 개수는 유저 요청에 맞게 유지하되, "
                    "각 DB에 title 속성과 sample_items 3개 이상을 반드시 포함하세요. "
                    "column_list 안에 database_ref를 넣지 마세요. "
                    "중첩 구조를 줄이되, 유저가 요청한 DB 개수와 뷰는 보존하세요."
                )

        except Exception as e:
            from app.core.cost_control import BudgetExceededError

            if isinstance(e, BudgetExceededError):
                raise  # 비용 상한 초과는 폴백으로 삼키지 않고 중단
            elapsed = time.time() - t0
            logger.info(f"[Gen-Eval 시도 {attempt + 1}/{max_retries}] 예외: {str(e)[:100]} ({elapsed:.1f}s)")
            feedback_context = f"이전 시도에서 오류 발생: {str(e)[:200]}. 올바른 JSON으로 다시 응답하세요."

    # Circuit Breaker: 최대 재시도 초과 → 가장 좋았던 결과 사용 또는 폴백
    if best_content:
        logger.info(f"[Gen-Eval 소진] 최선의 결과 사용 (오류 {best_error_count}개, post-processor로 보정)")
        best_content = blueprint_validator.validate_and_fix(best_content)

        # 무결성 자동 교정 적용
        from app.agent.creation_executor import CreationExecutor

        temp_bp = {"main_page": best_content.get("main_page", {"title": "temp"}), **best_content}
        integrity_issues = CreationExecutor.validate_blueprint_integrity(temp_bp)
        if integrity_issues:
            temp_bp = CreationExecutor._auto_fix_blueprint(temp_bp, integrity_issues)
            best_content.update({k: v for k, v in temp_bp.items() if k in ("blocks", "databases", "sub_pages")})

        blueprint = _assemble_blueprint(best_content, user_message)
        blueprint["metadata"]["generation_method"] = "ai_dynamic_partial"
        blueprint["metadata"]["gen_eval_attempts"] = max_retries
        blueprint["metadata"]["gen_eval_errors"] = best_error_count
        return await _finalize_blueprint(blueprint, ai_key, ai_model)

    logger.info("[Gen-Eval 전체 실패 → 스마트 폴백 사용]")
    memory.save_episode(
        Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message=user_message[:200],
            skill_used=skill_match.skill_id or "custom",
            layout=layout_router.route(user_message).layout,
            success=False,
            gen_eval_attempts=max_retries,
            error_types=["gen_eval_exhausted"],
        )
    )
    content = _smart_fallback(user_message)
    blueprint = _assemble_blueprint(content, user_message)
    blueprint["metadata"]["generation_method"] = "smart_fallback"
    return blueprint


# ============================================================
# 모드 감지
# ============================================================


def _detect_mode(user_message: str) -> str:
    """유저 메시지에서 복잡도 모드 감지"""
    msg = user_message.lower()
    # 명시적 모드 지정
    if any(kw in msg for kw in ["간단", "심플", "simple", "기본"]):
        return "simple"
    if any(kw in msg for kw in ["고급", "복잡", "advanced", "상세", "완벽"]):
        return "advanced"
    # 키워드 기반 자동 감지
    complex_keywords = ["대시보드", "crm", "erp", "허브", "워크스페이스", "학급", "창업", "회사"]
    simple_keywords = ["기록", "트래커", "물", "습관", "체크", "메모"]
    if any(kw in msg for kw in complex_keywords):
        return "advanced"
    if any(kw in msg for kw in simple_keywords):
        return "simple"
    return "standard"


# ============================================================
# AI 호출
# ============================================================


def _fallback_candidates(exclude_provider: str, max_candidates: int = 3) -> list[tuple[str, str]]:
    """1차 provider 실패 시 시도할 폴백 (provider명, api_key) 목록.

    - 키가 있는 provider + copilot(키 불필요, 구독 인증)을 후보로 한다.
    - **circuit-open provider는 건너뛴다** — 예: Gemini가 429로 연속 실패해 차단되면
      매 시도마다 재호출해 낭비하던 문제를 막고, 건강한 provider(groq 등)에 우선권을 준다.
    - 누적 실패가 적은(건강한) 순으로 정렬해 성공 확률을 높인다.
    """
    from app.agent.providers.router import _circuit_breaker
    from app.config import settings

    pairs: list[tuple[str, str]] = []
    if settings.copilot_enabled and exclude_provider != "copilot":
        pairs.append(("copilot", ""))  # copilot은 키 불필요
    pairs.extend(
        [
            ("groq", settings.groq_api_key),
            ("gemini", settings.gemini_api_key),
            ("claude", settings.anthropic_api_key),
        ]
    )
    candidates = [
        (n, k) for n, k in pairs if n != exclude_provider and (n == "copilot" or k) and not _circuit_breaker.is_open(n)
    ]
    candidates.sort(key=lambda c: _circuit_breaker.failure_count(c[0]))
    return candidates[:max_candidates]


async def _call_ai_for_content(
    user_message: str,
    ai_key: str = "",
    ai_model: str = "",
    extra_context: str = "",
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    from app.agent.providers.router import ProviderRouter

    mode = _detect_mode(user_message)
    layout_result = layout_router.route(user_message)
    skills_desc = get_tool_enum_description()
    prompt = prompt_assembler.assemble(mode=mode, layout=layout_result.layout, skills=skills_desc)
    logger.info(
        f"[Harness] mode={mode}, layout={layout_result.layout} (conf={layout_result.confidence:.2f}, {layout_result.reason})"
    )

    if extra_context:
        prompt += f"\n\n## Skill Guidelines:\n{extra_context[:1200]}"

    if conversation_history and len(conversation_history) > 1:
        recent = conversation_history[-6:]
        history_text = "\n".join(f"[{m['role']}]: {m['content'][:150]}" for m in recent[:-1])
        prompt += f"\n\n## Conversation History:\n{history_text}"

    provider = ProviderRouter.resolve_with_fallback(api_key=ai_key, ai_model=ai_model)
    max_chars = provider.get_max_prompt_chars()
    if max_chars > 0 and len(prompt) > max_chars:
        prompt = prompt_assembler.assemble_compact(
            mode=mode,
            layout=layout_result.layout,
            skills=skills_desc,
            max_chars=max_chars,
        )
        if extra_context:
            prompt += f"\n\n## Skill Guidelines:\n{extra_context[:600]}"
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-6:]
            history_text = "\n".join(f"[{m['role']}]: {m['content'][:150]}" for m in recent[:-1])
            prompt += f"\n\n## History:\n{history_text[:400]}"

    timeout = 90.0 if mode == "advanced" else 45.0
    from app.core.cost_control import note_call

    def _valid(r: Any) -> bool:
        """유효한 blueprint 응답인지 — databases/db_properties가 있어야 한다.
        (databases 없는 truthy dict를 '성공'으로 처리해 폴백을 건너뛰던 결함 방지.)"""
        return bool(r) and isinstance(r, dict) and ("databases" in r or "db_properties" in r)

    note_call()
    result = await provider.call_with_retry(prompt, user_message, model=ai_model, timeout=timeout)

    if _valid(result):
        ProviderRouter.circuit_breaker.record_success(provider.name)
    else:
        ProviderRouter.circuit_breaker.record_failure(provider.name)
        # 1차 provider 실패(또는 무효 응답) 시 건강한 다른 provider로 폴백 (실 AI 생성 보장).
        from app.agent.providers.router import create_provider

        for fb_name, fb_key in _fallback_candidates(provider.name):
            try:
                fb_provider = create_provider(fb_name, api_key=fb_key)
            except Exception:
                continue
            note_call()
            result = await fb_provider.call_with_retry(prompt, user_message, model=ai_model, timeout=timeout)
            if _valid(result):
                ProviderRouter.circuit_breaker.record_success(fb_name)
                logger.info(f"[provider 폴백] {provider.name} 실패 → {fb_name} 성공")
                break
            ProviderRouter.circuit_breaker.record_failure(fb_name)

    if _valid(result):
        return result
    return None


# ============================================================
# Blueprint 조립: AI가 준 데이터를 그대로 사용
# ============================================================


def _strip_leading_emoji(title: str) -> str:
    """제목 앞의 이모지/픽토그램을 제거한다 — 아이콘이 따로 표시되므로 중복('📚 📚 ...')을 막는다.

    AI가 종종 제목에 이모지를 붙이는데(예: "📚 독서 기록"), main_page.icon이 같은 이모지면
    노션에서 아이콘+제목이 이중으로 보인다. 선두 이모지 런만 제거하고 본문 텍스트는 보존한다.
    """
    import re

    if not title:
        return title
    # 이모지/기호/변형선택자/ZWJ + 공백의 선두 런을 제거
    emoji_run = re.compile(
        r"^[\s\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
        r"\U00002190-\U000021FF\U00002B00-\U00002BFF️‍♀♂]+"
    )
    cleaned = emoji_run.sub("", title).strip()
    return cleaned or title  # 전부 이모지였다면 원본 유지


def _fallback_title_from_message(user_message: str) -> str:
    """AI가 제목을 안 줬을 때 사용자 요청에서 짧고 의미 있는 한국어 제목을 추출.

    과거: 긴 사용자 메시지 전체가 노션 페이지 제목이 되던 결함
    ("북마크 정리 트래커 . 사이트명, URL, 카테고리..."). 첫 구만 취하고 30자로 캡한다.
    """
    import re

    cleaned = _clean_title(user_message) if user_message else ""
    if not cleaned:
        return "새 템플릿"
    # 서술형 설명 제거: 문장부호/대시 기준 첫 조각만
    first = re.split(r"[.\n,·•:;?!]|\s-\s|—", cleaned)[0].strip()
    title = first or cleaned
    if len(title) > 30:  # 너무 길면 단어 경계로 절단
        title = title[:30].rsplit(" ", 1)[0].strip() or title[:30].strip()
    return title or "새 템플릿"


def _assemble_blueprint(content: dict, user_message: str = "") -> dict[str, Any]:
    """AI가 생성한 전체 구조를 Blueprint로 조립"""
    color = content.get("color", "gray")
    # AI(특히 Groq)가 title을 안 주거나 영어 기본값을 주면 사용자 요청에서 한국어 제목을 만든다
    # (과거 'My Template'/'Untitled'가 그대로, 또는 긴 메시지 전체가 노션 제목이 되던 결함).
    raw_title = (content.get("title") or "").strip()
    if not raw_title or raw_title.lower() in ("my template", "untitled", "template", "items"):
        raw_title = _fallback_title_from_message(user_message)
    title = _strip_leading_emoji(raw_title)

    # Pick cover: prefer category-specific, fallback to color-based
    cover_category = content.get("cover_category", "")
    cover_url = _pick_cover(cover_category, color)

    blueprint: dict[str, Any] = {
        "version": "3.0",
        "metadata": {"title": title, "template_type": content.get("skill", "custom"), "color_theme": color},
        "main_page": {"title": title, "icon": content.get("icon", "📋"), "cover_url": cover_url},
        "blocks": [],
        "databases": [],
        "sub_pages": [],
    }

    # blocks: AI가 생성했으면 그대로, 없으면 기본 구조
    if content.get("blocks"):
        blueprint["blocks"] = content["blocks"]
    else:
        # blocks가 없으면 (폴백 등) 기본 구조 생성
        bg = f"{color}_background" if color != "default" else "default"
        blueprint["blocks"] = [
            {
                "type": "callout",
                "text": content.get("callout_text", f"{title}에 오신 걸 환영합니다!"),
                "icon": content.get("icon", "📋"),
                "color": bg,
            },
            {"type": "divider"},
            {"type": "heading_1", "text": f"📊 {content.get('db_name', title)}", "color": bg},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
        ]
        for faq in content.get("faq", []):
            blueprint["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    # databases: AI 형식 통일
    if content.get("databases"):
        for i, db in enumerate(content["databases"]):
            views = []
            for v in db.get("views", ["table"]):
                if isinstance(v, str):
                    views.append({"type": v, "title": v})
                elif isinstance(v, dict):
                    views.append(v)
            # AI가 DB title을 안 주면(groq 등) 영어 'Items' 중복 대신 고유 한국어 기본값
            db_title = (db.get("title") or db.get("db_name") or "").strip()
            if not db_title or db_title.lower() == "items":
                db_title = "데이터베이스" if len(content["databases"]) == 1 else f"데이터베이스 {i + 1}"
            blueprint["databases"].append(
                {
                    "title": db_title,
                    "is_inline": True,
                    "properties": db.get("db_properties", db.get("properties", {"이름": "title"})),
                    "views": views,
                    "sample_items": db.get("sample_items", []),
                    "description": db.get("description", ""),
                    "icon": db.get("icon"),
                    "cover_url": db.get("cover_url"),
                }
            )
    elif content.get("db_properties"):
        # 단일 DB (하위 호환)
        views = []
        for v in content.get("views", ["table"]):
            if isinstance(v, str):
                views.append({"type": v, "title": v})
            elif isinstance(v, dict):
                views.append(v)
        single_db_title = (content.get("db_name") or "").strip()
        if not single_db_title or single_db_title.lower() == "items":
            single_db_title = "데이터베이스"
        blueprint["databases"].append(
            {
                "title": single_db_title,
                "is_inline": True,
                "properties": content["db_properties"],
                "views": views,
                "sample_items": content.get("sample_items", []),
            }
        )

    # sub_pages: AI가 blocks를 설계했으면 그대로 사용, 없으면 기본 블록
    bg = f"{color}_background" if color != "default" else "default"
    for sub in content.get("sub_pages", []):
        if not isinstance(sub, dict):
            continue
        sub_blocks = sub.get("blocks", [])
        if not sub_blocks:
            # AI가 블록을 설계하지 않은 경우에만 기본 블록 생성
            sub_blocks = [
                {
                    "type": "heading_1",
                    "text": f"{sub.get('icon', '📄')} {sub.get('name', sub.get('title', ''))}",
                    "color": bg,
                },
                {
                    "type": "callout",
                    "text": sub.get("description", f"{sub.get('name', '')} 관련 내용을 정리하세요."),
                    "icon": "📌",
                    "color": bg,
                },
                {"type": "divider"},
            ]
        blueprint["sub_pages"].append(
            {
                "title": sub.get("name", sub.get("title", "서브페이지")),
                "icon": sub.get("icon", "📄"),
                "blocks": sub_blocks,
            }
        )

    # 셀러빌리티(A2) + 시각 프리미엄(A3) 보강 → 리스팅 키트 (품질 측정 전에 적용)
    try:
        from app.agent.listing_kit import build_listing_kit
        from app.agent.sellability import enrich_blueprint
        from app.agent.visual_enrich import enrich_visuals

        enrich_blueprint(blueprint)  # A2: 온보딩/상단네비/목차
        enrich_visuals(blueprint)  # A3: 뷰 큐레이션(board/calendar) + 아이콘 보강
        blueprint["metadata"]["listing_kit"] = build_listing_kit(blueprint)
    except Exception as e:
        logger.info(f"[Enrich 스킵] {str(e)[:80]}")

    # 품질 스코어카드 (비차단, Phase A1) — 구조 점수 + 유료급 루브릭을 metadata에 기록
    try:
        from app.agent.quality_report import attach_deterministic_quality

        attach_deterministic_quality(blueprint)
    except Exception as e:
        logger.info(f"[QualityReport 스킵] {str(e)[:80]}")

    return blueprint


# ============================================================
# 스마트 폴백 (AI 실패 시)
# ============================================================


def _clean_title(user_message: str) -> str:
    """사용자 메시지에서 색상/스타일 지시와 요청 동사를 제거해 깔끔한 제목을 추출.

    색상어는 **토큰 단위 완전일치**로만 제거한다(substring 금지) — '블루베리', '그린팀',
    'Evergreen' 같은 정상 단어는 보존된다.
    예: "운동 습관 트래커 만들어줘, 주황색으로" → "운동 습관 트래커"
    """
    import re

    from app.agent.intent_analyzer import COLOR_MAP

    color_words = {w.lower() for w in COLOR_MAP}

    def _is_color_token(tok: str) -> bool:
        s = tok.strip(",，.!·").strip().lower()
        if not s:
            return False
        if s in color_words:
            return True
        for suffix in ("으로", "로"):  # "주황색으로", "파란색으로"
            if s.endswith(suffix) and s[: -len(suffix)] in color_words:
                return True
        return False

    t = user_message
    # 요청 동사/표현 제거 (동사는 어절 치환)
    for v in (
        "만들어주세요",
        "만들어 줘",
        "만들어줘",
        "제작해 줘",
        "제작해줘",
        "생성해줘",
        "만들어",
        "제작",
        "해줘",
        "만들기",
    ):
        t = t.replace(v, " ")
    t = t.replace("!", " ")
    # 색상 지시는 토큰 완전일치로만 제거
    kept = [tok for tok in re.split(r"\s+", t) if tok and not _is_color_token(tok)]
    result = re.sub(r"\s+", " ", " ".join(kept)).strip(" ,，.·\t")
    return result.strip()


def _smart_fallback(user_message: str) -> dict[str, Any]:
    msg = user_message.lower()
    for template_key, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            template = json.loads(json.dumps(FALLBACK_TEMPLATES[template_key]))
            clean_title = _clean_title(user_message)
            if clean_title and len(clean_title) < 30:
                template["title"] = clean_title
            return template

    # 기본 폴백
    defaults = json.loads(json.dumps(FALLBACK_TEMPLATES["프로젝트"]))
    clean_title = _clean_title(user_message)
    if clean_title and len(clean_title) < 30:
        defaults["title"] = clean_title
    return defaults
