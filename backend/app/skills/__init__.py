"""Skill System: Load and manage template skills

Each skill defines:
- SKILL.md: Structure guide (layout, block order, required views)
- examples/: Real usage examples for AI reference
- reference/: Detailed guides for specific features

Custom Skills:
- 유저가 직접 만든 스킬은 custom_skills/ 디렉토리에 저장
- 내장 스킬과 동일한 포맷 (SKILL.md + YAML frontmatter)
- 내장 스킬과 이름이 겹치면 커스텀 스킬이 우선
"""

from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).parent
CUSTOM_SKILLS_DIR = SKILLS_DIR.parent.parent.parent / "custom_skills"  # project root/custom_skills/

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
    # ── 세분화 스킬 (Tier 2) ──
    "fitness": {"name": "fitness", "description": "Exercise & workout tracking (sets, reps, body parts, calories)", "keywords": "운동,헬스,피트니스,러닝,웨이트,요가,수영,스쿼트,벤치프레스,유산소,근력,스트레칭,운동기록,운동일지,운동일기,fitness,exercise,workout,gym"},
    "habit": {"name": "habit", "description": "Habit tracking & streaks (daily check, streak count, routines)", "keywords": "습관,루틴,매일,출석,streak,도전,30일,체크,daily,routine,habit"},
    "health": {"name": "health", "description": "Health tracking (sleep, water, weight, blood pressure, mood)", "keywords": "수면,물,체중,혈압,건강,기분,무드,에너지,수분,sleep,water,weight,health,mood"},
    "diet": {"name": "diet", "description": "Diet & nutrition tracking (meals, calories, macros, recipes)", "keywords": "식단,칼로리,영양,단백질,탄수화물,다이어트,식사,아침,점심,저녁,diet,nutrition,meal,calorie"},
    "reading": {"name": "reading", "description": "Reading log & book collection (title, author, genre, rating, review)", "keywords": "독서,책,도서,서평,북리뷰,읽기,독후감,작가,reading,book,review"},
    "recipe": {"name": "recipe", "description": "Recipe collection (ingredients, cook time, difficulty, cuisine)", "keywords": "레시피,요리,재료,조리,음식,맛집,쿠킹,recipe,cooking,food,cuisine"},
    "movie": {"name": "movie", "description": "Movie & drama tracking (title, genre, rating, platform, review)", "keywords": "영화,드라마,넷플릭스,시리즈,애니,웹툰,만화,감상,movie,drama,netflix,anime"},
    "music": {"name": "music", "description": "Music & album collection (artist, genre, mood, rating)", "keywords": "음악,앨범,아티스트,플레이리스트,노래,음반,music,album,playlist,song"},
    "cafe": {"name": "cafe", "description": "Cafe & restaurant review (name, location, menu, rating, photo)", "keywords": "카페,맛집,레스토랑,커피,디저트,위치,메뉴,음식점,cafe,restaurant,coffee"},
    "project": {"name": "project", "description": "Project management with kanban (tasks, assignees, priority, deadline)", "keywords": "프로젝트,태스크,담당자,마감,일정,진행,project,task,deadline,assignee"},
    "sprint": {"name": "sprint", "description": "Sprint & agile management (stories, points, epics, velocity)", "keywords": "스프린트,애자일,스크럼,스토리,포인트,에픽,백로그,sprint,agile,scrum,epic,backlog"},
    "bug": {"name": "bug", "description": "Bug tracker (severity, status, reproduction, assignee)", "keywords": "버그,이슈,에러,오류,재현,수정,bug,issue,error,fix,debug"},
    "meeting": {"name": "meeting", "description": "Meeting notes (agenda, attendees, action items, date)", "keywords": "회의,미팅,안건,참석자,회의록,액션아이템,meeting,agenda,minutes,notes"},
    "travel": {"name": "travel", "description": "Travel planning (destination, dates, accommodation, budget, checklist)", "keywords": "여행,계획,목적지,숙소,항공,비용,짐싸기,여행지,travel,trip,destination,itinerary"},
    "wedding": {"name": "wedding", "description": "Wedding & event planning (items, category, budget, D-Day, checklist)", "keywords": "결혼,웨딩,행사,이벤트,준비,예산,D-day,체크리스트,wedding,event"},
    "goals": {"name": "goals", "description": "Goal & OKR tracking (objectives, key results, progress, period)", "keywords": "목표,OKR,신년,분기,연간,핵심결과,진행률,달성,goal,objective,target"},
    "bookmark": {"name": "bookmark", "description": "Bookmark & link organizer (URL, category, tags, description)", "keywords": "북마크,링크,즐겨찾기,URL,사이트,웹,자료,리소스,bookmark,link,resource"},
    "inventory": {"name": "inventory", "description": "Inventory & asset tracking (item, quantity, location, category, price)", "keywords": "재고,물품,자산,수량,위치,입출고,장비,비품,inventory,asset,stock"},
    "contact": {"name": "contact", "description": "Contact & address book (name, phone, email, company, group)", "keywords": "연락처,전화,이메일,주소,명함,인맥,contact,phone,email,address"},
    "budget": {"name": "budget", "description": "Budget & expense tracking (income, expense, category, date, memo)", "keywords": "가계부,예산,지출,수입,소비,카드,정산,월급,budget,expense,income"},
    "investment": {"name": "investment", "description": "Investment portfolio tracking (stock, buy price, quantity, current, return)", "keywords": "투자,주식,ETF,펀드,매수,매도,수익률,배당,포트폴리오,investment,stock,portfolio"},
    "subscription": {"name": "subscription", "description": "Subscription management (service, price, billing date, category)", "keywords": "구독,넷플릭스,유튜브프리미엄,월정액,결제일,해지,구독료,subscription,billing"},
    "study": {"name": "study", "description": "Study log (subject, duration, comprehension, topic, date)", "keywords": "공부,스터디,과목,시험,수능,공시,자격증,토익,study,exam,test"},
    "language": {"name": "language", "description": "Language learning (word, meaning, example, mastery, review date)", "keywords": "어학,영어,일본어,중국어,단어,문법,회화,토플,language,english,vocabulary"},
    "sales": {"name": "sales", "description": "Sales pipeline (customer, stage, amount, probability, close date)", "keywords": "세일즈,파이프라인,거래,계약,영업기회,제안서,견적,sales,pipeline,deal,opportunity"},
    # ── Phase 4 추가 스킬 (Tier 2) ──
    "onboarding": {"name": "onboarding", "description": "Onboarding guide (steps, checklist, responsible person, timeline)", "keywords": "온보딩,신입,입사,적응,환영,안내,체크리스트,OJT,onboarding,welcome,new hire"},
    "wiki": {"name": "wiki", "description": "Team wiki & knowledge base (category, author, tags, last updated)", "keywords": "위키,지식베이스,문서화,사내,매뉴얼,정책,절차,나무위키,wiki,knowledge,docs"},
    "sop": {"name": "sop", "description": "Standard operating procedures (process, steps, responsible, frequency)", "keywords": "SOP,표준업무,절차서,프로세스,매뉴얼,규정,가이드라인,업무절차,sop,procedure,process"},
    "team_home": {"name": "team_home", "description": "Team home dashboard (members, links, announcements, goals)", "keywords": "팀홈,팀대시보드,팀페이지,부서,조직,팀원,공지,team home,team page,department"},
    "life_os": {"name": "life_os", "description": "Life OS & personal dashboard (areas, projects, goals, routines)", "keywords": "라이프OS,개인대시보드,삶관리,영역,프로젝트,습관,인생,life os,personal,dashboard,second brain"},
    "diary": {"name": "diary", "description": "Daily diary & journal (date, mood, weather, content, photo)", "keywords": "다이어리,하루,오늘,매일,일상,diary,daily,journal"},
    "gratitude": {"name": "gratitude", "description": "Gratitude journal (date, grateful for, category, mood)", "keywords": "감사,감사일기,감사노트,감사일지,고마운,행복,긍정,gratitude,thankful,grateful"},
    "review": {"name": "review", "description": "Weekly/monthly review (period, achievements, lessons, next goals)", "keywords": "회고,리뷰,주간,월간,분기,연간,성찰,피드백,review,retrospective,weekly,monthly"},
    "blog": {"name": "blog", "description": "Blog content management (title, category, status, publish date, SEO)", "keywords": "블로그,포스팅,글쓰기,발행,SEO,키워드,카테고리,blog,post,article,writing"},
    "youtube": {"name": "youtube", "description": "YouTube content planning (title, script status, filming, editing, upload)", "keywords": "유튜브,영상,촬영,편집,업로드,스크립트,썸네일,youtube,video,filming,editing"},
    "social": {"name": "social", "description": "Social media calendar (platform, content type, schedule, hashtags, analytics)", "keywords": "SNS,소셜미디어,인스타,틱톡,트위터,페이스북,해시태그,일정,social media,instagram,tiktok"},
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
    """Load SKILL.md content for a skill — 커스텀 스킬 우선"""
    # 커스텀 스킬 먼저 확인
    custom_path = CUSTOM_SKILLS_DIR / skill_name / "SKILL.md"
    if custom_path.exists():
        return custom_path.read_text(encoding="utf-8")
    # 내장 스킬
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


def _get_all_skills() -> dict[str, dict[str, str]]:
    """내장 + 커스텀 스킬 합쳐서 반환 (커스텀 우선)"""
    merged = dict(SKILL_REGISTRY)
    custom = load_custom_skills()
    merged.update(custom)  # 커스텀이 같은 이름이면 덮어씀
    return merged


def get_tool_enum_description() -> str:
    """Get skill descriptions for Tool schema enum (내장 + 커스텀)"""
    parts = []
    for skill_id, info in _get_all_skills().items():
        parts.append(f"{skill_id}={info['description']}")
    return ", ".join(parts)


def list_skills() -> list[dict[str, Any]]:
    """List all available skills with metadata (내장 + 커스텀)"""
    result = []
    all_skills = _get_all_skills()
    for skill_id, info in all_skills.items():
        is_custom = (CUSTOM_SKILLS_DIR / skill_id / "SKILL.md").exists()
        is_builtin = (SKILLS_DIR / skill_id / "SKILL.md").exists()
        result.append({
            "id": skill_id,
            "name": info["name"],
            "description": info["description"],
            "has_skill_md": is_custom or is_builtin,
            "is_custom": is_custom,
            "keywords": info.get("keywords", ""),
        })
    return result


# ============================================================
# 커스텀 스킬 CRUD
# ============================================================

def load_custom_skills() -> dict[str, dict[str, str]]:
    """custom_skills/ 디렉토리에서 유저 커스텀 스킬 로드"""
    skills: dict[str, dict[str, str]] = {}
    if not CUSTOM_SKILLS_DIR.exists():
        return skills
    for skill_dir in CUSTOM_SKILLS_DIR.iterdir():
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
                "description": desc or f"Custom skill: {name}",
                "keywords": keywords or name,
            }
    return skills


def _validate_skill_id(skill_id: str) -> bool:
    """스킬 ID 안전성 검증 — Path Traversal 방지"""
    import re
    if not skill_id or not re.match(r'^[a-z][a-z0-9_]{0,49}$', skill_id):
        return False
    if '..' in skill_id or '/' in skill_id or '\\' in skill_id:
        return False
    return True


def save_custom_skill(skill_id: str, content: str) -> bool:
    """커스텀 스킬 저장 (SKILL.md) — Path Traversal 방지"""
    if not _validate_skill_id(skill_id):
        raise ValueError(f"Invalid skill ID: {skill_id}. Must be lowercase alphanumeric + underscore, max 50 chars.")
    skill_dir = CUSTOM_SKILLS_DIR / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return True


def delete_custom_skill(skill_id: str) -> bool:
    """커스텀 스킬 삭제 — Path Traversal 방지"""
    if not _validate_skill_id(skill_id):
        raise ValueError(f"Invalid skill ID: {skill_id}")
    import shutil
    skill_dir = CUSTOM_SKILLS_DIR / skill_id
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
        return True
    return False


def get_custom_skill(skill_id: str) -> dict[str, Any] | None:
    """커스텀 스킬 상세 조회"""
    skill_path = CUSTOM_SKILLS_DIR / skill_id / "SKILL.md"
    if not skill_path.exists():
        return None
    content = skill_path.read_text(encoding="utf-8")
    return {"id": skill_id, "content": content}
