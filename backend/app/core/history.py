"""Generation History: 생성 이력 파일 저장

각 생성 세션의 메트릭 + 블루프린트를 JSONL 파일로 저장.
data/history/ 디렉토리에 날짜별 파일.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("notionforge.history")

HISTORY_DIR = Path(__file__).parent.parent.parent / "data" / "history"


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

        logger.info(f"[History] 이력 저장: {filepath.name}")
        return filepath

    except Exception as e:
        logger.warning(f"[History] 이력 저장 실패: {str(e)[:80]}")
        return None


def cleanup_old_history(retention_days: int = 30) -> int:
    """오래된 이력 파일 삭제 (보존 정책)

    Returns:
        삭제된 파일 수
    """
    if not HISTORY_DIR.exists():
        return 0

    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=retention_days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    deleted = 0

    for filepath in HISTORY_DIR.glob("*.jsonl"):
        if filepath.stem < cutoff_str:
            try:
                filepath.unlink()
                deleted += 1
            except Exception:
                continue

    if deleted > 0:
        logger.info(f"[History] {deleted}개 오래된 이력 파일 삭제 (>{retention_days}일)")
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
