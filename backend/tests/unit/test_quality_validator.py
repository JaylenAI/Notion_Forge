"""QualityValidator 3계층 검증 테스트"""

import pytest

from app.agent.quality_validator import QualityValidator, ValidationIssue, ValidationResult


@pytest.fixture
def validator():
    return QualityValidator()


def _make_blueprint(**overrides):
    base = {
        "title": "테스트 템플릿",
        "icon": "📋",
        "color": "blue",
        "blocks": [
            {"type": "callout", "text": "환영합니다!", "icon": "👋", "color": "blue_background"},
            {"type": "paragraph", "text": ""},
            {"type": "heading_1", "text": "📊 메인 섹션", "color": "blue"},
            {"type": "database_ref", "db_index": 0},
        ],
        "databases": [
            {
                "title": "작업 목록",
                "db_properties": {"이름": "title", "상태": {"type": "status"}, "날짜": "date"},
                "sample_items": [
                    {"이름": "첫 번째 작업", "상태": "시작 전"},
                    {"이름": "두 번째 작업", "상태": "진행 중"},
                    {"이름": "세 번째 작업", "상태": "완료"},
                ],
                "views": [{"type": "board"}],
            }
        ],
        "sub_pages": [{"title": "가이드", "icon": "📖"}],
        "metadata": {},
    }
    return {**base, **overrides}


# ─── Layer 1: Schema Tests ───


class TestSchemaValidation:
    def test_valid_blueprint_passes(self, validator):
        bp = _make_blueprint()
        issues = validator.validate_schema(bp)
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0

    def test_missing_title(self, validator):
        bp = _make_blueprint(title="")
        issues = validator.validate_schema(bp)
        assert any("title" in i.message for i in issues if i.severity == "critical")

    def test_empty_blocks(self, validator):
        bp = _make_blueprint(blocks=[])
        issues = validator.validate_schema(bp)
        assert any("blocks" in i.message for i in issues if i.severity == "critical")

    def test_empty_databases(self, validator):
        bp = _make_blueprint(databases=[])
        issues = validator.validate_schema(bp)
        assert any("databases" in i.message for i in issues if i.severity == "critical")

    def test_block_without_type(self, validator):
        bp = _make_blueprint(blocks=[{"text": "orphan"}])
        issues = validator.validate_schema(bp)
        assert any("type" in i.message for i in issues if i.severity == "critical")

    def test_invalid_block_type(self, validator):
        bp = _make_blueprint(blocks=[{"type": "nonexistent_widget"}])
        issues = validator.validate_schema(bp)
        assert any("알 수 없는 블록" in i.message for i in issues)

    def test_db_ref_missing_index(self, validator):
        bp = _make_blueprint(blocks=[{"type": "database_ref"}])
        issues = validator.validate_schema(bp)
        assert any("db_index" in i.message for i in issues if i.severity == "critical")

    def test_db_ref_out_of_range(self, validator):
        bp = _make_blueprint(blocks=[{"type": "database_ref", "db_index": 5}])
        issues = validator.validate_schema(bp)
        assert any("범위 초과" in i.message for i in issues if i.severity == "critical")

    def test_db_ref_inside_column(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "column_list", "columns": [[{"type": "database_ref", "db_index": 0}]]},
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("column_list 내부" in i.message for i in issues if i.severity == "critical")

    def test_empty_column_list(self, validator):
        bp = _make_blueprint(blocks=[{"type": "column_list", "columns": []}])
        issues = validator.validate_schema(bp)
        assert any("columns가 비어있음" in i.message for i in issues)

    def test_db_missing_title_property(self, validator):
        bp = _make_blueprint(
            databases=[
                {"title": "No Title DB", "db_properties": {"상태": "status"}, "sample_items": [{}, {}, {}]},
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("title 속성 누락" in i.message for i in issues if i.severity == "critical")

    def test_db_empty_properties(self, validator):
        bp = _make_blueprint(
            databases=[
                {"title": "Empty DB", "db_properties": {}, "sample_items": [{}, {}, {}]},
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("비어있습니다" in i.message for i in issues if i.severity == "critical")

    def test_relation_missing_target(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "연결": {"type": "relation"}},
                    "sample_items": [{}, {}, {}],
                },
                {"title": "DB2", "db_properties": {"이름": "title"}, "sample_items": [{}, {}, {}]},
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("target_db_index 누락" in i.message for i in issues)

    def test_relation_target_out_of_range(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "연결": {"type": "relation", "target_db_index": 99}},
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("범위 초과" in i.message for i in issues)

    def test_self_referencing_relation(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "셀프": {"type": "relation", "target_db_index": 0}},
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("자기 참조" in i.message for i in issues)

    def test_formula_missing_expression(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "수식": {"type": "formula"}},
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("expression 누락" in i.message for i in issues)

    def test_rollup_missing_relation_property(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "집계": {"type": "rollup"}},
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("relation_property 누락" in i.message for i in issues)

    def test_rollup_invalid_relation_property(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {
                        "이름": "title",
                        "집계": {"type": "rollup", "relation_property": "없는속성"},
                    },
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("같은 DB에 없음" in i.message for i in issues)

    def test_invalid_property_type_string(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title", "잘못된": "imaginary_type"},
                    "sample_items": [{}, {}, {}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("알 수 없는 속성 타입" in i.message for i in issues)

    def test_invalid_view_type(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title"},
                    "sample_items": [{}, {}, {}],
                    "views": [{"type": "unknown_view"}],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("알 수 없는 뷰" in i.message for i in issues)

    def test_non_dict_block(self, validator):
        bp = _make_blueprint(blocks=["not a dict", {"type": "paragraph", "text": "ok"}])
        issues = validator.validate_schema(bp)
        assert any("dict가 아닙니다" in i.message for i in issues)

    def test_view_type_as_string(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB1",
                    "db_properties": {"이름": "title"},
                    "sample_items": [{}, {}, {}],
                    "views": ["fantasy_view"],
                },
            ]
        )
        issues = validator.validate_schema(bp)
        assert any("알 수 없는 뷰" in i.message for i in issues)


# ─── Layer 2: Content Tests ───


class TestContentValidation:
    def test_valid_content_passes(self, validator):
        bp = _make_blueprint()
        issues = validator.validate_content(bp)
        assert not any(i.severity == "critical" for i in issues)

    def test_insufficient_samples(self, validator):
        bp = _make_blueprint(
            databases=[
                {"title": "DB", "db_properties": {"이름": "title"}, "sample_items": [{"이름": "하나"}]},
            ]
        )
        issues = validator.validate_content(bp)
        assert any("최소 3개" in i.message for i in issues)

    def test_duplicate_titles(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB",
                    "db_properties": {"이름": "title"},
                    "sample_items": [
                        {"이름": "중복 제목"},
                        {"이름": "중복 제목"},
                        {"이름": "다른 제목"},
                    ],
                },
            ]
        )
        issues = validator.validate_content(bp)
        assert any("중복 제목" in i.message for i in issues)

    def test_short_title_warning(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB",
                    "db_properties": {"이름": "title"},
                    "sample_items": [{"이름": "A"}, {"이름": "정상 제목"}, {"이름": "B"}],
                },
            ]
        )
        issues = validator.validate_content(bp)
        assert any("짧은 제목" in i.message for i in issues)

    def test_status_diversity_low(self, validator):
        bp = _make_blueprint(
            databases=[
                {
                    "title": "DB",
                    "db_properties": {"이름": "title", "상태": {"type": "status"}},
                    "sample_items": [
                        {"이름": "A항목", "상태": "시작 전"},
                        {"이름": "B항목", "상태": "시작 전"},
                        {"이름": "C항목", "상태": "시작 전"},
                    ],
                },
            ]
        )
        issues = validator.validate_content(bp)
        assert any("다양성 부족" in i.message for i in issues)

    def test_too_many_empty_blocks(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "paragraph", "text": ""},
                {"type": "paragraph", "text": ""},
                {"type": "paragraph", "text": ""},
                {"type": "paragraph", "text": ""},
                {"type": "paragraph", "text": "내용 있음"},
            ]
        )
        issues = validator.validate_content(bp)
        assert any("빈 텍스트 블록" in i.message for i in issues)

    def test_sub_page_missing_title(self, validator):
        bp = _make_blueprint(sub_pages=[{"icon": "📝"}])
        issues = validator.validate_content(bp)
        assert any("title 누락" in i.message for i in issues)


# ─── Layer 3: Design Tests ───


class TestDesignValidation:
    def test_valid_design_passes(self, validator):
        bp = _make_blueprint()
        issues = validator.validate_design(bp)
        assert not any(i.severity == "critical" for i in issues)

    def test_no_callout_first(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "paragraph", "text": "first"},
                {"type": "heading_1", "text": "제목"},
            ]
        )
        issues = validator.validate_design(bp)
        assert any("callout이 아닙니다" in i.message for i in issues)

    def test_no_heading_warning(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "callout", "text": "환영"},
                {"type": "paragraph", "text": "1"},
                {"type": "paragraph", "text": "2"},
                {"type": "paragraph", "text": "3"},
                {"type": "paragraph", "text": "4"},
            ]
        )
        issues = validator.validate_design(bp)
        assert any("heading 블록 없음" in i.message for i in issues)

    def test_invalid_color(self, validator):
        bp = _make_blueprint(color="rainbow")
        issues = validator.validate_design(bp)
        assert any("알 수 없는 색상" in i.message for i in issues)

    def test_consecutive_same_blocks(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "callout", "text": "a"},
                {"type": "callout", "text": "b"},
                {"type": "callout", "text": "c"},
                {"type": "callout", "text": "d"},
                {"type": "heading_1", "text": "제목"},
            ]
        )
        issues = validator.validate_design(bp)
        assert any("4회 이상 연속" in i.message for i in issues)

    def test_sub_page_missing_icon(self, validator):
        bp = _make_blueprint(sub_pages=[{"title": "가이드"}])
        issues = validator.validate_design(bp)
        assert any("icon 누락" in i.message for i in issues)

    def test_missing_main_icon(self, validator):
        bp = _make_blueprint(icon="")
        issues = validator.validate_design(bp)
        assert any("메인 페이지 icon" in i.message for i in issues)

    def test_db_ref_in_top_3(self, validator):
        bp = _make_blueprint(
            blocks=[
                {"type": "callout", "text": "환영"},
                {"type": "database_ref", "db_index": 0},
                {"type": "heading_1", "text": "제목"},
            ]
        )
        issues = validator.validate_design(bp)
        assert any("상단 3블록" in i.message for i in issues)


# ─── Integration: Full Validate ───


class TestFullValidation:
    def test_perfect_blueprint_passes(self, validator):
        bp = _make_blueprint()
        result = validator.validate(bp)
        assert result.passed is True
        assert result.score >= 80.0

    def test_empty_blueprint_fails(self, validator):
        result = validator.validate({"blocks": [], "databases": []})
        assert result.passed is False
        assert result.critical_count > 0

    def test_score_calculation(self, validator):
        bp = _make_blueprint()
        result = validator.validate(bp)
        assert "schema" in result.layer_scores
        assert "content" in result.layer_scores
        assert "design" in result.layer_scores
        assert all(0.0 <= s <= 100.0 for s in result.layer_scores.values())

    def test_critical_always_fails(self, validator):
        bp = _make_blueprint(title="", blocks=[], databases=[])
        result = validator.validate(bp)
        assert result.passed is False

    def test_warnings_only_can_pass(self, validator):
        bp = _make_blueprint(
            sub_pages=[{"title": "가이드"}],  # icon 누락 = warning
        )
        result = validator.validate(bp)
        assert result.passed is True
        assert result.warning_count > 0


class TestValidationResult:
    def test_critical_count(self):
        r = ValidationResult(
            passed=False,
            score=0,
            issues=[
                ValidationIssue("schema", "critical", "a"),
                ValidationIssue("schema", "warning", "b"),
                ValidationIssue("content", "critical", "c"),
            ],
        )
        assert r.critical_count == 2
        assert r.warning_count == 1
