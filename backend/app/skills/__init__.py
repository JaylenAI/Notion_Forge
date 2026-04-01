"""Skill System: Load and manage template skills

Each skill defines:
- SKILL.md: Structure guide (layout, block order, required views)
- examples/: Real usage examples for AI reference
- reference/: Detailed guides for specific features
"""

from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).parent

# All available skills
SKILL_REGISTRY: dict[str, dict[str, str]] = {
    "track": {
        "name": "track",
        "description": "Daily tracking & habits (exercise, study, routines, diet, water intake, sleep)",
        "keywords": "추적,습관,운동,공부,루틴,다이어트,체크,매일,기록일지,출석,트래커,헬스,피트니스,수면,물섭취,걸음,체중,tracker,habit,exercise,workout,daily",
    },
    "collect": {
        "name": "collect",
        "description": "Collect & record items (wine, books, recipes, movies, music, archives)",
        "keywords": "수집,기록,노트,와인,독서,맛집,영화,레시피,아카이브,리뷰,컬렉션,시음,음악,앨범,만화,웹툰,전시,공연,카페,맛집,음식,책,도서,서평,collect,review,archive",
    },
    "manage": {
        "name": "manage",
        "description": "Process & status management (projects, hiring, sales, bugs, sprints)",
        "keywords": "관리,프로젝트,채용,영업,버그,파이프라인,스프린트,칸반,태스크,업무,이슈,릴리즈,배포,agile,kanban,sprint,project,task,manage",
    },
    "plan": {
        "name": "plan",
        "description": "Planning & scheduling (wedding, travel, moving, exams, events, goals)",
        "keywords": "계획,일정,결혼,여행,이사,시험,행사,준비,D-day,할일,체크리스트,목표,신년,plan,schedule,checklist,goal,event,trip",
    },
    "organize": {
        "name": "organize",
        "description": "Organize & structure info (bookmarks, contacts, budget, inventory, links)",
        "keywords": "정리,북마크,연락처,재고,목록,분류,카탈로그,즐겨찾기,링크,자료,리소스,organize,bookmark,inventory,catalog,resource",
    },
    "guide": {
        "name": "guide",
        "description": "Guides & documentation (onboarding, manuals, FAQ, wiki, handover)",
        "keywords": "안내,온보딩,인수인계,매뉴얼,가이드,FAQ,위키,설명서,신입,가이드라인,절차,프로세스,guide,onboarding,manual,wiki,faq,documentation",
    },
    "hub": {
        "name": "hub",
        "description": "Dashboard & home pages (team home, workspace, project hub, overview)",
        "keywords": "대시보드,홈,허브,워크스페이스,메인,한눈에,전체,팀,포탈,현황판,dashboard,home,hub,workspace,overview,portal",
    },
    "finance": {
        "name": "finance",
        "description": "Financial management (budgets, expenses, subscriptions, investments, savings)",
        "keywords": "가계부,예산,지출,수입,투자,구독,절약,저축,돈,월급,카드,소비,정산,재테크,금융,주식,펀드,finance,budget,expense,subscription,investment,money",
    },
    "journal": {
        "name": "journal",
        "description": "Journaling & reflection (diary, mood tracking, gratitude, weekly review)",
        "keywords": "일기,회고,감사,무드,기분,리뷰,주간,월간,성찰,다이어리,감정,하루,오늘,일상,메모,journal,diary,mood,gratitude,reflection,review",
    },
    "content": {
        "name": "content",
        "description": "Content planning (social media, blog, YouTube, editorial calendar, newsletter)",
        "keywords": "콘텐츠,SNS,블로그,유튜브,인스타,틱톡,편집,캘린더,뉴스레터,포스팅,마케팅,소셜미디어,content,blog,youtube,instagram,social,marketing,editorial",
    },
    "learn": {
        "name": "learn",
        "description": "Learning & study (courses, exam prep, language learning, skill roadmap)",
        "keywords": "학습,공부,강의,시험,어학,영어,코딩,스킬,로드맵,커리큘럼,수업,과목,자격증,토익,코스,learn,study,course,exam,language,skill,curriculum",
    },
    "crm": {
        "name": "crm",
        "description": "Customer & relationship management (clients, sales pipeline, meetings, leads)",
        "keywords": "고객,CRM,영업,세일즈,리드,미팅,거래,계약,클라이언트,파트너,제안,비즈니스,crm,client,sales,lead,meeting,deal,pipeline,customer",
    },
}


def auto_discover_skills() -> dict[str, dict[str, str]]:
    """Auto-discover skills by scanning for SKILL.md files"""
    skills = {}
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            name = skill_dir.name
            desc = ""
            keywords = ""
            for line in content.split("\n"):
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                elif line.startswith("keywords:"):
                    keywords = line.split(":", 1)[1].strip()
            skills[name] = {
                "name": name,
                "description": desc or f"Template skill: {name}",
                "keywords": keywords or name,
            }
    return skills


def load_skill(skill_name: str) -> str | None:
    """Load SKILL.md content for a skill"""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return None


def load_skill_examples(skill_name: str) -> list[str]:
    """Load all example files for a skill"""
    examples_dir = SKILLS_DIR / skill_name / "examples"
    if not examples_dir.exists():
        return []
    return [f.read_text(encoding="utf-8") for f in sorted(examples_dir.glob("*.md"))]


def get_skill_summary() -> str:
    """Get summary of all skills for AI system prompt"""
    lines = []
    for skill_id, info in SKILL_REGISTRY.items():
        lines.append(f"- {skill_id}: {info['description']}")
    return "\n".join(lines)


def get_tool_enum_description() -> str:
    """Get skill descriptions for Tool schema enum"""
    parts = []
    for skill_id, info in SKILL_REGISTRY.items():
        parts.append(f"{skill_id}={info['description']}")
    return ", ".join(parts)


def list_skills() -> list[dict[str, Any]]:
    """List all available skills with metadata"""
    return [
        {
            "id": skill_id,
            "name": info["name"],
            "description": info["description"],
            "has_skill_md": (SKILLS_DIR / skill_id / "SKILL.md").exists(),
        }
        for skill_id, info in SKILL_REGISTRY.items()
    ]
