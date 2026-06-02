"""Generation History: 생성 이력 파일 저장

각 생성 세션의 메트릭 + 블루프린트를 JSONL 파일로 저장.
data/history/ 디렉토리에 날짜별 파일.
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("notionforge.history")

HISTORY_DIR = Path(__file__).parent.parent.parent / "data" / "history"
# 전체 blueprint 본문 저장 (error analysis / 품질 회귀 분석용). 메타데이터 JSONL과 별개.
BLUEPRINT_DIR = Path(__file__).parent.parent.parent / "data" / "blueprints"


def save_generation_record(metrics_dict: dict, blueprint: dict | None = None) -> Path | None:
    """생성 이력을 JSONL 파일에 추가

    Args:
        metrics_dict: GenerationMetrics.to_dict() 결과
        blueprint: 생성에 사용된 블루프린트 (선택)

    Returns:
        저장된 파일 경로 또는 None (실패 시)
    """
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = HISTORY_DIR / f"{today}.jsonl"

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics_dict,
        }

        # 블루프린트는 메타데이터만 저장 (전체는 너무 큼)
        if blueprint:
            meta = blueprint.get("metadata", {})
            record["blueprint_meta"] = {
                "title": meta.get("title", ""),
                "template_type": meta.get("template_type", ""),
                "color_theme": meta.get("color_theme", ""),
                "skill_used": meta.get("skill_used", ""),
                "generation_method": meta.get("generation_method", ""),
                "blocks_count": len(blueprint.get("blocks", [])),
                "databases_count": len(blueprint.get("databases", [])),
                "sub_pages_count": len(blueprint.get("sub_pages", [])),
            }

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 전체 blueprint도 별도 파일로 보관 (error analysis용). 메타데이터 JSONL은 그대로 인덱스 역할.
        if blueprint:
            save_full_blueprint(blueprint)

        logger.info(f"[History] 이력 저장: {filepath.name}")
        return filepath

    except Exception as e:
        logger.warning(f"[History] 이력 저장 실패: {str(e)[:80]}")
        return None


def save_full_blueprint(blueprint: dict) -> Path | None:
    """전체 blueprint 본문을 data/blueprints/<date>/ 에 저장 (error analysis / 재현용).

    Phase A1: '메타데이터만 저장'(블루프린트 전체 유실) 한계를 DB 없이 로컬 파일로 보완.
    """
    if not blueprint:
        return None
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        day_dir = BLUEPRINT_DIR / today
        day_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%H%M%S_%f")
        filepath = day_dir / f"{stamp}.json"
        filepath.write_text(json.dumps(blueprint, ensure_ascii=False, indent=2), encoding="utf-8")
        return filepath
    except Exception as e:
        logger.warning(f"[History] 전체 blueprint 저장 실패: {str(e)[:80]}")
        return None


def load_recent_blueprints(limit: int = 100) -> list[dict]:
    """error analysis용 — 최근 저장된 전체 blueprint 본문 로드 (최신순)."""
    out: list[dict] = []
    if not BLUEPRINT_DIR.exists():
        return out
    files = sorted(BLUEPRINT_DIR.glob("*/*.json"), reverse=True)[:limit]
    for f in files:
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def cleanup_old_history(retention_days: int = 30) -> int:
    """오래된 이력 파일 삭제 (보존 정책)

    Returns:
        삭제된 파일 수
    """
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=retention_days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    deleted = 0

    if HISTORY_DIR.exists():
        for filepath in HISTORY_DIR.glob("*.jsonl"):
            if filepath.stem < cutoff_str:
                try:
                    filepath.unlink()
                    deleted += 1
                except Exception:
                    continue

    # 전체 blueprint 디렉토리(data/blueprints/<date>/)도 보존 기간 적용
    if BLUEPRINT_DIR.exists():
        for day_dir in BLUEPRINT_DIR.glob("*"):
            if day_dir.is_dir() and day_dir.name < cutoff_str:
                try:
                    shutil.rmtree(day_dir)
                    deleted += 1
                except Exception:
                    continue

    if deleted > 0:
        logger.info(f"[History] {deleted}개 오래된 이력/블루프린트 삭제 (>{retention_days}일)")
    return deleted


def get_recent_history(days: int = 7, limit: int = 50) -> list[dict]:
    """최근 생성 이력 조회"""
    records: list[dict] = []
    if not HISTORY_DIR.exists():
        return records

    files = sorted(HISTORY_DIR.glob("*.jsonl"), reverse=True)[:days]
    for filepath in files:
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
                        if len(records) >= limit:
                            return records
        except Exception:
            continue

    return records
