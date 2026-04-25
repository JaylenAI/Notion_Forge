"""QualityValidator: 블루프린트 3계층 품질 검증

Notion 생성 전 블루프린트 품질을 3단계로 검증:
  Layer 1 — Schema: 구조적 무결성 (필수 필드, 타입, 범위)
  Layer 2 — Content: 콘텐츠 완성도 (샘플 데이터, 텍스트 품질, 다양성)
  Layer 3 — Design: UX/레이아웃 규칙 (블록 순서, 색상 일관성, 가독성)

각 계층은 독립 실행 가능하며, validate()로 3계층 통합 검증 수행.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("notionforge.quality_validator")

VALID_BLOCK_TYPES = frozenset(
    {
        "heading_1",
        "heading_2",
        "heading_3",
        "paragraph",
        "callout",
        "quote",
        "toggle",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "divider",
        "table_of_contents",
        "column_list",
        "database_ref",
        "linked_view",
        "image",
        "bookmark",
        "embed",
        "code",
        "synced_block",
        "equation",
    }
)

VALID_PROPERTY_TYPES = frozenset(
    {
        "title",
        "rich_text",
        "number",
        "select",
        "multi_select",
        "status",
        "date",
        "people",
        "files",
        "checkbox",
        "url",
        "email",
        "phone_number",
        "formula",
        "relation",
        "rollup",
        "created_time",
        "last_edited_time",
    }
)

VALID_COLORS = frozenset(
    {
        "default",
        "blue",
        "brown",
        "gray",
        "green",
        "orange",
        "pink",
        "purple",
        "red",
        "yellow",
    }
)

VALID_VIEW_TYPES = frozenset(
    {
        "table",
        "board",
        "calendar",
        "list",
        "gallery",
        "timeline",
    }
)


@dataclass
class ValidationIssue:
    layer: str
    severity: str  # critical, warning, info
    message: str
    path: str = ""


@dataclass
class ValidationResult:
    passed: bool
    score: float
    issues: list[ValidationIssue] = field(default_factory=list)
    layer_scores: dict[str, float] = field(default_factory=dict)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


class QualityValidator:
    """3계층 블루프린트 품질 검증기"""

    def validate(self, blueprint: dict[str, Any]) -> ValidationResult:
        schema_issues = self.validate_schema(blueprint)
        content_issues = self.validate_content(blueprint)
        design_issues = self.validate_design(blueprint)

        all_issues = schema_issues + content_issues + design_issues

        schema_score = self._calc_score(schema_issues)
        content_score = self._calc_score(content_issues)
        design_score = self._calc_score(design_issues)

        total_score = schema_score * 0.5 + content_score * 0.3 + design_score * 0.2
        passed = total_score >= 60.0 and not any(i.severity == "critical" for i in all_issues)

        result = ValidationResult(
            passed=passed,
            score=round(total_score, 1),
            issues=all_issues,
            layer_scores={
                "schema": round(schema_score, 1),
                "content": round(content_score, 1),
                "design": round(design_score, 1),
            },
        )

        logger.info(
            f"[QualityValidator] score={result.score} passed={result.passed} "
            f"(schema={schema_score:.0f} content={content_score:.0f} design={design_score:.0f}) "
            f"critical={result.critical_count} warning={result.warning_count}"
        )
        return result

    # ── Layer 1: Schema Validation ──

    def validate_schema(self, bp: dict[str, Any]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        blocks = bp.get("blocks", [])
        databases = bp.get("databases", [])

        if not bp.get("title"):
            issues.append(ValidationIssue("schema", "critical", "title 필드가 없습니다.", "title"))

        if not blocks:
            issues.append(ValidationIssue("schema", "critical", "blocks 배열이 비어있습니다.", "blocks"))

        if not databases:
            issues.append(ValidationIssue("schema", "critical", "databases가 없습니다. 최소 1개 필요.", "databases"))

        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                issues.append(
                    ValidationIssue("schema", "critical", f"블록이 dict가 아닙니다: {type(block)}", f"blocks[{i}]")
                )
                continue
            btype = block.get("type")
            if not btype:
                issues.append(ValidationIssue("schema", "critical", "type 필드 누락", f"blocks[{i}]"))
            elif btype not in VALID_BLOCK_TYPES:
                issues.append(ValidationIssue("schema", "warning", f"알 수 없는 블록 타입: {btype}", f"blocks[{i}]"))
            if btype == "database_ref" and "db_index" not in block:
                issues.append(ValidationIssue("schema", "critical", "database_ref에 db_index 누락", f"blocks[{i}]"))
            if btype == "database_ref":
                idx = block.get("db_index", 0)
                if isinstance(idx, int) and idx >= len(databases):
                    issues.append(
                        ValidationIssue(
                            "schema",
                            "critical",
                            f"db_index={idx} 범위 초과 (databases={len(databases)}개)",
                            f"blocks[{i}]",
                        )
                    )
            if btype == "column_list":
                cols = block.get("columns", [])
                if not cols:
                    issues.append(
                        ValidationIssue("schema", "warning", "column_list에 columns가 비어있음", f"blocks[{i}]")
                    )
                for ci, col in enumerate(cols if isinstance(cols, list) else []):
                    if isinstance(col, list):
                        for item in col:
                            if isinstance(item, dict) and item.get("type") == "database_ref":
                                issues.append(
                                    ValidationIssue(
                                        "schema",
                                        "critical",
                                        "database_ref가 column_list 내부에 있음 — page level로 이동 필요",
                                        f"blocks[{i}].columns[{ci}]",
                                    )
                                )

        db_count = len(databases)
        for di, db in enumerate(databases):
            props = db.get("db_properties", db.get("properties", {}))
            if not isinstance(props, dict):
                issues.append(
                    ValidationIssue("schema", "critical", "properties가 dict가 아닙니다.", f"databases[{di}]")
                )
                continue

            if not props:
                issues.append(ValidationIssue("schema", "critical", "속성이 비어있습니다.", f"databases[{di}]"))

            has_title = any(v == "title" or (isinstance(v, dict) and v.get("type") == "title") for v in props.values())
            if not has_title:
                issues.append(ValidationIssue("schema", "critical", "title 속성 누락", f"databases[{di}]"))

            for pname, pspec in props.items():
                if isinstance(pspec, str):
                    if pspec not in VALID_PROPERTY_TYPES:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "warning",
                                f"알 수 없는 속성 타입: {pspec}",
                                f"databases[{di}].{pname}",
                            )
                        )
                    continue
                if not isinstance(pspec, dict):
                    continue

                ptype = pspec.get("type", "")
                if ptype and ptype not in VALID_PROPERTY_TYPES:
                    issues.append(
                        ValidationIssue(
                            "schema",
                            "warning",
                            f"알 수 없는 속성 타입: {ptype}",
                            f"databases[{di}].{pname}",
                        )
                    )

                if ptype == "relation":
                    target = pspec.get("target_db_index")
                    if target is None:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                "relation에 target_db_index 누락",
                                f"databases[{di}].{pname}",
                            )
                        )
                    elif not isinstance(target, int) or target < 0 or target >= db_count:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                f"target_db_index={target} 범위 초과",
                                f"databases[{di}].{pname}",
                            )
                        )
                    elif target == di:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                "자기 참조 relation",
                                f"databases[{di}].{pname}",
                            )
                        )

                elif ptype == "formula":
                    if not pspec.get("expression"):
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                "formula에 expression 누락",
                                f"databases[{di}].{pname}",
                            )
                        )

                elif ptype == "rollup":
                    rel = pspec.get("relation_property", "")
                    if not rel:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                "rollup에 relation_property 누락",
                                f"databases[{di}].{pname}",
                            )
                        )
                    elif rel not in props:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "critical",
                                f"rollup의 relation_property '{rel}'가 같은 DB에 없음",
                                f"databases[{di}].{pname}",
                            )
                        )

            for vs in db.get("views", []):
                if isinstance(vs, dict):
                    vtype = vs.get("type", "")
                    if vtype and vtype not in VALID_VIEW_TYPES:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "warning",
                                f"알 수 없는 뷰 타입: {vtype}",
                                f"databases[{di}].views",
                            )
                        )
                elif isinstance(vs, str):
                    if vs not in VALID_VIEW_TYPES:
                        issues.append(
                            ValidationIssue(
                                "schema",
                                "warning",
                                f"알 수 없는 뷰 타입: {vs}",
                                f"databases[{di}].views",
                            )
                        )

        return issues

    # ── Layer 2: Content Validation ──

    def validate_content(self, bp: dict[str, Any]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        databases = bp.get("databases", [])
        blocks = bp.get("blocks", [])
        sub_pages = bp.get("sub_pages", [])

        for di, db in enumerate(databases):
            samples = db.get("sample_items", [])
            if len(samples) < 3:
                issues.append(
                    ValidationIssue(
                        "content",
                        "warning",
                        f"sample_items {len(samples)}개 — 최소 3개 권장",
                        f"databases[{di}]",
                    )
                )

            if samples:
                props = db.get("db_properties", db.get("properties", {}))
                title_key = next(
                    (k for k, v in props.items() if v == "title" or (isinstance(v, dict) and v.get("type") == "title")),
                    None,
                )
                if title_key:
                    titles = [s.get(title_key, "") for s in samples if s.get(title_key)]
                    if len(titles) != len(set(titles)):
                        issues.append(
                            ValidationIssue(
                                "content",
                                "warning",
                                "sample_items에 중복 제목 존재",
                                f"databases[{di}]",
                            )
                        )

                    short_titles = [t for t in titles if len(str(t)) < 2]
                    if short_titles:
                        issues.append(
                            ValidationIssue(
                                "content",
                                "warning",
                                f"sample_items 중 너무 짧은 제목 {len(short_titles)}개",
                                f"databases[{di}]",
                            )
                        )

            status_props = [
                k
                for k, v in db.get("db_properties", db.get("properties", {})).items()
                if v == "status" or (isinstance(v, dict) and v.get("type") == "status")
            ]
            if status_props and samples:
                for sk in status_props:
                    statuses = {s.get(sk) for s in samples if s.get(sk)}
                    if len(statuses) < 2:
                        issues.append(
                            ValidationIssue(
                                "content",
                                "info",
                                f"status '{sk}'의 값 다양성 부족 ({len(statuses)}종)",
                                f"databases[{di}]",
                            )
                        )

        text_blocks = [
            b for b in blocks if isinstance(b, dict) and b.get("type") in ("paragraph", "callout", "quote", "toggle")
        ]
        empty_text_count = sum(1 for b in text_blocks if not b.get("text", "").strip())
        content_text_count = sum(1 for b in text_blocks if b.get("text", "").strip())
        if content_text_count > 0 and empty_text_count > content_text_count:
            issues.append(
                ValidationIssue(
                    "content",
                    "warning",
                    f"빈 텍스트 블록({empty_text_count})이 내용 블록({content_text_count})보다 많음",
                    "blocks",
                )
            )

        for si, sub in enumerate(sub_pages):
            if not sub.get("title"):
                issues.append(
                    ValidationIssue(
                        "content",
                        "warning",
                        "서브페이지 title 누락",
                        f"sub_pages[{si}]",
                    )
                )

        return issues

    # ── Layer 3: Design Validation ──

    def validate_design(self, bp: dict[str, Any]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        blocks = bp.get("blocks", [])
        color = bp.get("color", "default")
        sub_pages = bp.get("sub_pages", [])

        if not blocks:
            return issues

        block_types = [b.get("type") for b in blocks if isinstance(b, dict)]

        if blocks and (not isinstance(blocks[0], dict) or blocks[0].get("type") != "callout"):
            issues.append(
                ValidationIssue(
                    "design",
                    "warning",
                    "첫 번째 블록이 callout이 아닙니다 — 환영 메시지 권장",
                    "blocks[0]",
                )
            )

        has_heading = any(t in ("heading_1", "heading_2") for t in block_types)
        if len(blocks) >= 5 and not has_heading:
            issues.append(
                ValidationIssue(
                    "design",
                    "warning",
                    "heading 블록 없음 — 5개 이상 블록 시 섹션 구분 권장",
                    "blocks",
                )
            )

        if color and color not in VALID_COLORS:
            issues.append(
                ValidationIssue(
                    "design",
                    "warning",
                    f"알 수 없는 색상: {color}",
                    "color",
                )
            )

        if color and color != "default":
            expected_bg = f"{color}_background"
            callouts = [b for b in blocks if isinstance(b, dict) and b.get("type") == "callout"]
            mismatched = [
                b
                for b in callouts
                if b.get("color")
                and b["color"] != expected_bg
                and b["color"] != f"{color}_background"
                and not b["color"].startswith(color)
            ]
            if len(mismatched) > len(callouts) // 2 and callouts:
                issues.append(
                    ValidationIssue(
                        "design",
                        "info",
                        f"callout 색상이 테마({color})와 불일치 {len(mismatched)}/{len(callouts)}개",
                        "blocks",
                    )
                )

        consecutive_same = 0
        prev_type = None
        for bt in block_types:
            if bt == prev_type and bt not in ("paragraph", "bulleted_list_item", "numbered_list_item", "to_do"):
                consecutive_same += 1
            else:
                consecutive_same = 0
            prev_type = bt
            if consecutive_same >= 3:
                issues.append(
                    ValidationIssue(
                        "design",
                        "warning",
                        f"동일 블록 타입({bt})이 4회 이상 연속 — 다양성 부족",
                        "blocks",
                    )
                )
                break

        for si, sub in enumerate(sub_pages):
            if not sub.get("icon"):
                issues.append(
                    ValidationIssue(
                        "design",
                        "warning",
                        "서브페이지 icon 누락",
                        f"sub_pages[{si}]",
                    )
                )

        if not bp.get("icon"):
            issues.append(
                ValidationIssue(
                    "design",
                    "info",
                    "메인 페이지 icon 누락",
                    "icon",
                )
            )

        db_ref_in_first_3 = any(
            isinstance(blocks[i], dict) and blocks[i].get("type") == "database_ref" for i in range(min(3, len(blocks)))
        )
        if db_ref_in_first_3:
            issues.append(
                ValidationIssue(
                    "design",
                    "info",
                    "database_ref가 상단 3블록 이내 — 환영 메시지/설명 후 배치 권장",
                    "blocks",
                )
            )

        return issues

    # ── Score Calculation ──

    @staticmethod
    def _calc_score(issues: list[ValidationIssue]) -> float:
        score = 100.0
        for issue in issues:
            if issue.severity == "critical":
                score -= 25.0
            elif issue.severity == "warning":
                score -= 8.0
            elif issue.severity == "info":
                score -= 2.0
        return max(0.0, score)


quality_validator = QualityValidator()
