"""Skill Loader: Load template & content skills from .md files"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent

# template_type → skill directory mapping
SKILL_MAP = {
    "dashboard": "template-dashboard",
    "tracker": "template-tracker",
    "bookmark": "template-bookmark",
    "onboarding": "template-onboarding",
    "note": "template-note",
    "project": "template-project",
    "crm": "template-crm",
}


def load_skill(template_type: str) -> str | None:
    """Load SKILL.md for a template type"""
    dir_name = SKILL_MAP.get(template_type)
    if not dir_name:
        return None
    skill_path = SKILLS_DIR / dir_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return None


def load_content_skill() -> str | None:
    """Load content writing skill"""
    path = SKILLS_DIR / "content-writing" / "SKILL.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def load_reference(template_type: str, ref_name: str) -> str | None:
    """Load a reference file from a skill directory"""
    dir_name = SKILL_MAP.get(template_type)
    if not dir_name:
        return None
    ref_path = SKILLS_DIR / dir_name / "reference" / f"{ref_name}.md"
    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8")
    return None


def list_skills() -> list[dict]:
    """List all available template skills"""
    skills = []
    for template_type, dir_name in SKILL_MAP.items():
        skill_path = SKILLS_DIR / dir_name / "SKILL.md"
        if skill_path.exists():
            # Parse frontmatter for description
            content = skill_path.read_text(encoding="utf-8")
            desc = ""
            for line in content.split("\n"):
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    break
            skills.append({"type": template_type, "directory": dir_name, "description": desc})
    return skills
