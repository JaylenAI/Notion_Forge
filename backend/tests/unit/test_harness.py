"""하네스 엔지니어링 테스트: PromptAssembler + LayoutRouter + PostProcessor"""

from app.agent.layout_router import LayoutRouter
from app.agent.post_processor import BlueprintValidator
from app.agent.prompt_assembler import PromptAssembler

# ============================================================
# PromptAssembler 테스트
# ============================================================


class TestPromptAssembler:
    def setup_method(self):
        self.assembler = PromptAssembler()

    def test_assemble_default(self):
        """기본 조립: base + standard + views + relations + design_tokens"""
        prompt = self.assembler.assemble(skills="test_skills")
        assert "WORLD-CLASS Notion template designer" in prompt
        assert "test_skills" in prompt
        assert "VIEW CATALOG" in prompt
        assert "RELATION" in prompt
        assert "ANTI-PATTERNS" in prompt

    def test_assemble_simple_mode(self):
        """simple 모드 포함 확인"""
        prompt = self.assembler.assemble(mode="simple", skills="")
        assert "Simple" in prompt
        assert "8-12 blocks" in prompt

    def test_assemble_advanced_mode(self):
        """advanced 모드 포함 확인"""
        prompt = self.assembler.assemble(mode="advanced", skills="")
        assert "Advanced" in prompt
        assert "20-35 blocks" in prompt

    def test_assemble_with_layout(self):
        """레이아웃 포함 확인"""
        prompt = self.assembler.assemble(mode="standard", layout="kanban_board", skills="")
        assert "Kanban Board" in prompt or "BOARD VIEW" in prompt

    def test_assemble_invalid_mode_fallback(self):
        """잘못된 모드는 standard로 폴백"""
        prompt = self.assembler.assemble(mode="invalid_mode", skills="")
        assert "Standard" in prompt

    def test_assemble_compact(self):
        """compact 모드는 더 짧아야 함"""
        full = self.assembler.assemble(skills="")
        compact = self.assembler.assemble_compact(skills="")
        assert len(compact) < len(full)
        # compact에는 design_tokens가 없어야 함
        assert "ANTI-PATTERNS" not in compact

    def test_assemble_compact_max_chars(self):
        """compact은 max_chars를 초과하지 않아야 함"""
        compact = self.assembler.assemble_compact(skills="", max_chars=5000)
        assert len(compact) <= 5000

    def test_available_layouts(self):
        """8개 레이아웃 .md 파일 존재 확인"""
        layouts = self.assembler.available_layouts()
        assert len(layouts) == 8
        expected = {
            "sidebar_main",
            "gallery_hero",
            "category_hub",
            "kanban_board",
            "calendar_main",
            "dashboard_widgets",
            "simple_tracker",
            "portfolio",
        }
        assert set(layouts) == expected

    def test_available_modes(self):
        """3개 모드 확인"""
        modes = self.assembler.available_modes()
        assert modes == ["simple", "standard", "advanced"]

    def test_all_layouts_loadable(self):
        """모든 레이아웃 .md가 로드 가능한지"""
        for layout in self.assembler.available_layouts():
            prompt = self.assembler.assemble(layout=layout, skills="")
            assert len(prompt) > 100

    def test_skills_placeholder_replaced(self):
        """{skills} 플레이스홀더가 치환되는지"""
        prompt = self.assembler.assemble(skills="track=Daily tracking, manage=Projects")
        assert "track=Daily tracking" in prompt
        assert "{skills}" not in prompt


# ============================================================
# LayoutRouter 테스트
# ============================================================


class TestLayoutRouter:
    def setup_method(self):
        self.router = LayoutRouter()

    def test_simple_tracker(self):
        result = self.router.route("물 마신 양 기록해줘")
        assert result.layout == "simple_tracker"
        assert result.confidence > 0.5

    def test_gallery_hero_journal(self):
        result = self.router.route("일기장 만들어줘")
        assert result.layout == "gallery_hero"

    def test_gallery_hero_recipe(self):
        result = self.router.route("레시피 컬렉션 만들어줘")
        assert result.layout == "gallery_hero"

    def test_kanban_board(self):
        result = self.router.route("프로젝트 관리 보드 만들어줘")
        assert result.layout == "kanban_board"

    def test_calendar_main(self):
        result = self.router.route("콘텐츠 캘린더 만들어줘")
        assert result.layout == "calendar_main"

    def test_dashboard_widgets(self):
        result = self.router.route("CRM 대시보드 만들어줘")
        assert result.layout == "dashboard_widgets"

    def test_category_hub(self):
        result = self.router.route("회사 온보딩 가이드 만들어줘")
        assert result.layout == "category_hub"

    def test_portfolio(self):
        result = self.router.route("포트폴리오 만들어줘")
        assert result.layout == "portfolio"

    def test_default_sidebar(self):
        """매칭 키워드 없으면 sidebar_main 기본값"""
        result = self.router.route("뭔가 좋은거 만들어줘")
        assert result.layout == "sidebar_main"
        assert result.confidence == 0.5

    def test_exercise_tracker(self):
        result = self.router.route("운동 기록 트래커")
        assert result.layout == "simple_tracker"

    def test_book_collection(self):
        result = self.router.route("독서 기록 만들어줘")
        assert result.layout == "gallery_hero"

    def test_team_wiki(self):
        result = self.router.route("팀 위키 만들어줘")
        assert result.layout == "category_hub"

    def test_available_layouts(self):
        layouts = self.router.available_layouts()
        assert len(layouts) == 8


# ============================================================
# PostProcessor 테스트
# ============================================================


class TestPostProcessor:
    def setup_method(self):
        self.validator = BlueprintValidator()

    def test_ensure_welcome_callout(self):
        """첫 블록이 callout이 아니면 추가"""
        content = {
            "title": "테스트",
            "icon": "📋",
            "color": "blue",
            "blocks": [{"type": "heading_1", "text": "제목"}],
            "databases": [],
        }
        result = self.validator.validate_and_fix(content)
        assert result["blocks"][0]["type"] == "callout"
        assert "테스트" in result["blocks"][0]["text"]

    def test_keep_existing_callout(self):
        """이미 callout이 있으면 추가하지 않음"""
        content = {
            "blocks": [{"type": "callout", "text": "환영!", "icon": "🎉", "color": "blue_background"}],
            "databases": [],
        }
        result = self.validator.validate_and_fix(content)
        assert len([b for b in result["blocks"] if b["type"] == "callout" and "환영" in b.get("text", "")]) == 1

    def test_ensure_guide_toggle(self):
        """가이드 toggle이 없으면 추가"""
        content = {
            "blocks": [{"type": "callout", "text": "환영", "icon": "📋", "color": "blue_background"}],
            "databases": [],
        }
        result = self.validator.validate_and_fix(content)
        toggles = [b for b in result["blocks"] if b["type"] == "toggle"]
        assert any("가이드" in t.get("text", "") for t in toggles)

    def test_fix_db_ref_in_columns(self):
        """column_list 안의 database_ref를 바깥으로 이동"""
        content = {
            "blocks": [
                {"type": "callout", "text": "환영", "icon": "📋", "color": "blue_background"},
                {
                    "type": "column_list",
                    "columns": [
                        [{"type": "callout", "text": "stat"}],
                        [{"type": "database_ref", "db_index": 0}],
                    ],
                },
            ],
            "databases": [{"title": "DB1", "db_properties": {"이름": "title"}, "sample_items": []}],
        }
        result = self.validator.validate_and_fix(content)
        # database_ref가 column_list 밖에 있어야 함
        for block in result["blocks"]:
            if block.get("type") == "column_list":
                for col in block.get("columns", []):
                    if isinstance(col, list):
                        for item in col:
                            assert item.get("type") != "database_ref"

    def test_validate_db_refs(self):
        """유효하지 않은 db_index를 0으로 보정"""
        content = {
            "blocks": [
                {"type": "callout", "text": "환영", "icon": "📋", "color": "blue_background"},
                {"type": "database_ref", "db_index": 5},
            ],
            "databases": [{"title": "DB1", "db_properties": {"이름": "title"}, "sample_items": []}],
        }
        result = self.validator.validate_and_fix(content)
        db_refs = [b for b in result["blocks"] if b["type"] == "database_ref"]
        assert all(r["db_index"] == 0 for r in db_refs)

    def test_fix_status_values(self):
        """영어 상태값을 한국어로 매핑"""
        content = {
            "blocks": [{"type": "callout", "text": "환영", "icon": "📋", "color": "blue_background"}],
            "databases": [
                {
                    "title": "Tasks",
                    "db_properties": {"이름": "title", "상태": "status"},
                    "sample_items": [
                        {"이름": "Task1", "상태": "Not started"},
                        {"이름": "Task2", "상태": "In progress"},
                        {"이름": "Task3", "상태": "Done"},
                    ],
                }
            ],
        }
        result = self.validator.validate_and_fix(content)
        statuses = [item["상태"] for item in result["databases"][0]["sample_items"]]
        assert statuses == ["시작 전", "진행 중", "완료"]

    def test_ensure_cover_category(self):
        """cover_category가 없으면 color 기반 추론"""
        content = {
            "color": "orange",
            "blocks": [{"type": "callout", "text": "환영", "icon": "📋", "color": "orange_background"}],
            "databases": [],
        }
        result = self.validator.validate_and_fix(content)
        assert result["cover_category"] == "fitness"

    def test_full_pipeline(self):
        """전체 파이프라인 통합 테스트"""
        content = {
            "title": "프로젝트 보드",
            "icon": "📊",
            "color": "blue",
            "blocks": [
                {"type": "callout", "text": "프로젝트를 관리하세요!", "icon": "📊", "color": "blue_background"},
                {"type": "heading_2", "text": "태스크 보드"},
                {"type": "database_ref", "db_index": 0},
                {"type": "divider"},
            ],
            "databases": [
                {
                    "title": "태스크",
                    "db_properties": {"이름": "title", "상태": "status", "날짜": "date"},
                    "views": [{"type": "board", "title": "칸반"}],
                    "sample_items": [
                        {"이름": "작업1", "상태": "진행 중", "날짜": "2026-04-01"},
                        {"이름": "작업2", "상태": "완료", "날짜": "2026-04-02"},
                        {"이름": "작업3", "상태": "시작 전", "날짜": "2026-04-03"},
                    ],
                }
            ],
        }
        result = self.validator.validate_and_fix(content)
        # callout 유지
        assert result["blocks"][0]["type"] == "callout"
        # 가이드 toggle 추가됨
        assert any(b.get("type") == "toggle" for b in result["blocks"])
        # cover_category 추론됨
        assert result["cover_category"] == "business"
