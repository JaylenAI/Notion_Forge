"""AI 자유 설계 Blueprint Generator (dev-2 v3)

핵심 변경: AI가 blocks[] 배열도 직접 생성
- 하드코딩 빌더 함수 7개 제거
- AI가 유저 요청 복잡도에 따라 블록 수/구조를 자유롭게 결정
- 스킬 .md는 AI에게 규칙/가이드만 제공
"""

import logging

logger = logging.getLogger("notionforge.blueprint_generator")

import json
from typing import Any

from app.config import settings
from app.skills import get_tool_enum_description
from app.agent.prompt_assembler import prompt_assembler
from app.agent.layout_router import layout_router
from app.agent.post_processor import blueprint_validator
from app.agent.skill_router import build_skill_guide as _build_skill_guide_async

from pathlib import Path as _Path

import random as _random


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
                            errors.append(f"blocks[{i}].columns[{ci}]: database_ref가 column_list 안에 있습니다. page level로 이동 필요.")

    # Level 2: DB 구조 검증
    for di, db in enumerate(content.get("databases", [])):
        props = db.get("db_properties", db.get("properties", {}))
        if not props:
            errors.append(f"databases[{di}]: 속성(properties)이 비어있습니다.")
        has_title = any(
            v == "title" or (isinstance(v, dict) and v.get("type") == "title")
            for v in props.values()
        )
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

    is_pass = len(errors) == 0
    return is_pass, errors


# ============================================================
# 메인 함수
# ============================================================

async def generate_blueprint(
    user_message: str,
    ai_key: str = "",
    ai_model: str = "",
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Gen-Eval 피드백 루프: AI 생성 → 검증 → 실패 시 에러 피드백 → 재생성 (최대 3회)"""
    import time
    from app.agent.providers.router import ProviderRouter

    provider = ProviderRouter.resolve(api_key=ai_key, ai_model=ai_model)
    skill_guide, skill_match = await _build_skill_guide_async(user_message, provider=provider)

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
                enhanced_message, ai_key=ai_key, ai_model=ai_model,
                extra_context=skill_guide, conversation_history=conversation_history,
            )
            elapsed = time.time() - t0

            if not ai_content or (not ai_content.get("databases") and not ai_content.get("db_properties")):
                logger.info(f"[Gen-Eval 시도 {attempt+1}/{max_retries}] AI 응답 파싱 실패 ({elapsed:.1f}s)")
                feedback_context = "JSON 파싱 실패. 반드시 유효한 JSON으로 응답하세요. databases 배열이 필수입니다."
                continue

            # Evaluate: 구조적 결함 검증
            is_pass, eval_errors = _evaluate_ai_output(ai_content)

            if is_pass:
                # 검증 통과 → Post-processor 보정 → 반환
                ai_content = blueprint_validator.validate_and_fix(ai_content)
                blueprint = _assemble_blueprint(ai_content)
                blueprint["metadata"]["generation_method"] = "ai_dynamic"
                blueprint["metadata"]["skill_used"] = skill_match.skill_id or ai_content.get("skill", "custom")
                blueprint["metadata"]["skill_match_method"] = skill_match.method
                blueprint["metadata"]["gen_eval_attempts"] = attempt + 1
                blueprint["metadata"]["gen_eval_time"] = round(elapsed, 1)
                logger.info(f"[Gen-Eval 통과] 시도 {attempt+1}/{max_retries}, {elapsed:.1f}s")
                return blueprint

            # 검증 실패 → 에러를 피드백으로 구성
            error_count = len(eval_errors)
            logger.info(f"[Gen-Eval 시도 {attempt+1}/{max_retries}] 검증 실패: {error_count}개 오류 ({elapsed:.1f}s)")
            for err in eval_errors[:5]:
                logger.info(f"  - {err}")

            # 최선의 결과 추적 (Circuit Breaker: 가장 오류 적은 결과 보관)
            if error_count < best_error_count:
                best_error_count = error_count
                best_content = ai_content

            # 피드백 구성: 에러 메시지를 AI에게 다시 전달
            feedback_context = "\n".join(eval_errors[:8])

            # 전략 변경: 마지막 재시도에서는 간소화 힌트 추가
            if attempt == max_retries - 2:
                feedback_context += (
                    "\n\n[STRATEGY CHANGE] 이전 시도들이 실패했습니다. "
                    "더 간단한 구조로 생성하세요: DB 1-2개, 블록 8-12개, "
                    "복잡한 중첩 구조 대신 평면적 배치를 사용하세요."
                )

        except Exception as e:
            elapsed = time.time() - t0
            logger.info(f"[Gen-Eval 시도 {attempt+1}/{max_retries}] 예외: {str(e)[:100]} ({elapsed:.1f}s)")
            feedback_context = f"이전 시도에서 오류 발생: {str(e)[:200]}. 올바른 JSON으로 다시 응답하세요."

    # Circuit Breaker: 최대 재시도 초과 → 가장 좋았던 결과 사용 또는 폴백
    if best_content:
        logger.info(f"[Gen-Eval 소진] 최선의 결과 사용 (오류 {best_error_count}개, post-processor로 보정)")
        best_content = blueprint_validator.validate_and_fix(best_content)
        blueprint = _assemble_blueprint(best_content)
        blueprint["metadata"]["generation_method"] = "ai_dynamic_partial"
        blueprint["metadata"]["gen_eval_attempts"] = max_retries
        blueprint["metadata"]["gen_eval_errors"] = best_error_count
        return blueprint

    logger.info("[Gen-Eval 전체 실패 → 스마트 폴백 사용]")
    content = _smart_fallback(user_message)
    blueprint = _assemble_blueprint(content)
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
    logger.info(f"[Harness] mode={mode}, layout={layout_result.layout} (conf={layout_result.confidence:.2f}, {layout_result.reason})")

    if extra_context:
        prompt += f"\n\n## Skill Guidelines:\n{extra_context[:1200]}"

    if conversation_history and len(conversation_history) > 1:
        recent = conversation_history[-6:]
        history_text = "\n".join(f"[{m['role']}]: {m['content'][:150]}" for m in recent[:-1])
        prompt += f"\n\n## Conversation History:\n{history_text}"

    provider = ProviderRouter.resolve(api_key=ai_key, ai_model=ai_model)
    max_chars = provider.get_max_prompt_chars()
    if max_chars > 0 and len(prompt) > max_chars:
        prompt = prompt_assembler.assemble_compact(
            mode=mode, layout=layout_result.layout, skills=skills_desc, max_chars=max_chars,
        )
        if extra_context:
            prompt += f"\n\n## Skill Guidelines:\n{extra_context[:600]}"
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-6:]
            history_text = "\n".join(f"[{m['role']}]: {m['content'][:150]}" for m in recent[:-1])
            prompt += f"\n\n## History:\n{history_text[:400]}"

    result = await provider.call(prompt, user_message, model=ai_model)
    if not result:
        return None
    if "databases" in result or "db_properties" in result:
        return result
    return None


# ============================================================
# Blueprint 조립: AI가 준 데이터를 그대로 사용
# ============================================================

def _assemble_blueprint(content: dict) -> dict[str, Any]:
    """AI가 생성한 전체 구조를 Blueprint로 조립"""
    color = content.get("color", "gray")
    title = content.get("title", "My Template")

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
            {"type": "callout", "text": content.get("callout_text", f"{title}에 오신 걸 환영합니다!"), "icon": content.get("icon", "📋"), "color": bg},
            {"type": "divider"},
            {"type": "heading_1", "text": f"📊 {content.get('db_name', title)}", "color": bg},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
        ]
        for faq in content.get("faq", []):
            blueprint["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    # databases: AI 형식 통일
    if content.get("databases"):
        for db in content["databases"]:
            views = []
            for v in db.get("views", ["table"]):
                if isinstance(v, str):
                    views.append({"type": v, "title": v})
                elif isinstance(v, dict):
                    views.append(v)
            blueprint["databases"].append({
                "title": db.get("title", db.get("db_name", "Items")),
                "is_inline": True,
                "properties": db.get("db_properties", db.get("properties", {"이름": "title"})),
                "views": views,
                "sample_items": db.get("sample_items", []),
                "description": db.get("description", ""),
                "icon": db.get("icon"),
                "cover_url": db.get("cover_url"),
            })
    elif content.get("db_properties"):
        # 단일 DB (하위 호환)
        views = []
        for v in content.get("views", ["table"]):
            if isinstance(v, str):
                views.append({"type": v, "title": v})
            elif isinstance(v, dict):
                views.append(v)
        blueprint["databases"].append({
            "title": content.get("db_name", "Items"),
            "is_inline": True,
            "properties": content["db_properties"],
            "views": views,
            "sample_items": content.get("sample_items", []),
        })

    # sub_pages: AI가 blocks를 설계했으면 그대로 사용, 없으면 기본 블록
    bg = f"{color}_background" if color != "default" else "default"
    for sub in content.get("sub_pages", []):
        if not isinstance(sub, dict):
            continue
        sub_blocks = sub.get("blocks", [])
        if not sub_blocks:
            # AI가 블록을 설계하지 않은 경우에만 기본 블록 생성
            sub_blocks = [
                {"type": "heading_1", "text": f"{sub.get('icon', '📄')} {sub.get('name', sub.get('title', ''))}", "color": bg},
                {"type": "callout", "text": sub.get("description", f"{sub.get('name', '')} 관련 내용을 정리하세요."), "icon": "📌", "color": bg},
                {"type": "divider"},
            ]
        blueprint["sub_pages"].append({
            "title": sub.get("name", sub.get("title", "서브페이지")),
            "icon": sub.get("icon", "📄"),
            "blocks": sub_blocks,
        })

    return blueprint


# ============================================================
# 스마트 폴백 (AI 실패 시)
# ============================================================

def _smart_fallback(user_message: str) -> dict[str, Any]:
    msg = user_message.lower()
    for template_key, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            template = json.loads(json.dumps(FALLBACK_TEMPLATES[template_key]))
            clean_title = user_message.replace("만들어줘", "").replace("제작해줘", "").replace("!", "").strip()
            if clean_title and len(clean_title) < 30:
                template["title"] = clean_title
            return template

    # 기본 폴백
    defaults = json.loads(json.dumps(FALLBACK_TEMPLATES["프로젝트"]))
    clean_title = user_message.replace("만들어줘", "").replace("제작해줘", "").replace("!", "").strip()
    if clean_title and len(clean_title) < 30:
        defaults["title"] = clean_title
    return defaults
