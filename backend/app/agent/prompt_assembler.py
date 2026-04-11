"""Prompt Assembler: 모듈별 .md 파일을 동적으로 조립하여 시스템 프롬프트 생성

Phase 1: base + mode + views_catalog + relations + design_tokens
Phase 2+: base + mode + layout + views_catalog + relations + design_tokens
"""

from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).parent / "prompts"


@lru_cache(maxsize=32)
def _load_module(relative_path: str) -> str:
    """프롬프트 모듈 .md 파일 로드 (캐싱)"""
    path = PROMPTS_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Prompt module not found: {path}")
    return path.read_text(encoding="utf-8")


def _load_module_safe(relative_path: str) -> str:
    """모듈 로드 — 없으면 빈 문자열 반환"""
    try:
        return _load_module(relative_path)
    except FileNotFoundError:
        return ""


class PromptAssembler:
    """프롬프트 모듈을 동적으로 조립하는 어셈블러

    사용:
        assembler = PromptAssembler()
        prompt = assembler.assemble(mode="standard", layout="kanban_board", skills="...")
    """

    VALID_MODES = ("simple", "standard", "advanced")

    def assemble(
        self,
        mode: str = "standard",
        layout: str | None = None,
        skills: str = "",
    ) -> str:
        """모듈별 .md를 조립하여 최종 시스템 프롬프트 생성

        Args:
            mode: 복잡도 모드 (simple/standard/advanced)
            layout: 레이아웃 타입 (Phase 2에서 활성화)
            skills: 사용 가능한 스킬 목록 문자열
        """
        if mode not in self.VALID_MODES:
            mode = "standard"

        sections: list[str] = []

        # 1. Base prompt (철학 + 블록타입 + DB규칙 + 출력포맷)
        base = _load_module("base.md").format(skills=skills)
        sections.append(base)

        # 2. Mode prompt (복잡도별 가이드)
        mode_prompt = _load_module_safe(f"modes/{mode}.md")
        if mode_prompt:
            sections.append(mode_prompt)

        # 3. Layout prompt (Phase 2+에서 활성화)
        if layout:
            layout_prompt = _load_module_safe(f"layouts/{layout}.md")
            if layout_prompt:
                sections.append(layout_prompt)

        # 4. Views catalog
        views = _load_module_safe("views_catalog.md")
        if views:
            sections.append(views)

        # 5. Relations & formulas
        relations = _load_module_safe("relations.md")
        if relations:
            sections.append(relations)

        # 6. Design tokens & anti-patterns
        tokens = _load_module_safe("design_tokens.md")
        if tokens:
            sections.append(tokens)

        return "\n\n".join(sections)

    def assemble_compact(
        self,
        mode: str = "standard",
        layout: str | None = None,
        skills: str = "",
        max_chars: int = 16000,
    ) -> str:
        """Groq 등 토큰 제한이 있는 프로바이더용 축약 프롬프트

        views_catalog을 축약하고, design_tokens를 제거하여 토큰 절약.
        """
        if mode not in self.VALID_MODES:
            mode = "standard"

        sections: list[str] = []

        # 1. Base (필수)
        base = _load_module("base.md").format(skills=skills)
        sections.append(base)

        # 2. Mode (필수)
        mode_prompt = _load_module_safe(f"modes/{mode}.md")
        if mode_prompt:
            sections.append(mode_prompt)

        # 3. Layout (Phase 2+)
        if layout:
            layout_prompt = _load_module_safe(f"layouts/{layout}.md")
            if layout_prompt:
                sections.append(layout_prompt)

        # 4. Views catalog (축약)
        compact_views = """## VIEW CATALOG (compact)
DB "views" array types: table, board, gallery, calendar, timeline, chart, list, form, map, dashboard.
View config options: group_by, cover(page_cover/property), cover_size(small/medium/large), chart_type(donut/column/bar/line), x_axis, y_axis, color_theme, date_property, arrows_by, zoom_level, show_data_labels, height.
Choose views that fit. Simple request = 1-2 views. Complex = 3-4 views."""
        sections.append(compact_views)

        # 5. Relations (축약 없이 포함 — 비교적 짧음)
        relations = _load_module_safe("relations.md")
        if relations:
            sections.append(relations)

        # design_tokens는 생략 (토큰 절약)

        result = "\n\n".join(sections)

        # 최종 길이 체크
        if len(result) > max_chars:
            # relations도 제거
            sections_trimmed = [s for s in sections if "RELATION" not in s]
            result = "\n\n".join(sections_trimmed)

        return result[:max_chars]

    @staticmethod
    def available_layouts() -> list[str]:
        """사용 가능한 레이아웃 목록 반환"""
        layouts_dir = PROMPTS_DIR / "layouts"
        if not layouts_dir.exists():
            return []
        return [p.stem for p in sorted(layouts_dir.glob("*.md"))]

    @staticmethod
    def available_modes() -> list[str]:
        """사용 가능한 모드 목록 반환"""
        return list(PromptAssembler.VALID_MODES)

    @staticmethod
    def clear_cache() -> None:
        """프롬프트 캐시 초기화 (개발/핫리로드용)"""
        _load_module.cache_clear()


# 싱글턴 인스턴스
prompt_assembler = PromptAssembler()
