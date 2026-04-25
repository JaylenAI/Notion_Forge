"""Episodic Memory: 에이전트 학습 기억 시스템

생성 성공/실패 패턴, 유저 피드백, 스킬 사용 통계를 파일 기반으로 저장.
향후 생성 시 컨텍스트로 주입하여 품질 향상.
키워드 기반 유사도 검색으로 관련 에피소드를 매칭.
"""

import json
import logging
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("notionforge.memory")

MEMORY_DIR = Path(__file__).parent.parent.parent / "data" / "memory"

_STOP_WORDS = frozenset(
    {
        "만들어줘",
        "만들어",
        "제작해줘",
        "좀",
        "해줘",
        "주세요",
        "나",
        "내",
        "를",
        "을",
        "의",
        "에",
        "이",
        "가",
        "는",
        "은",
        "와",
        "과",
        "도",
        "로",
        "으로",
        "에서",
        "한",
        "a",
        "the",
        "is",
        "for",
        "and",
        "my",
        "me",
        "make",
        "create",
        "please",
    }
)


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[가-힣]+|[a-zA-Z]+", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


def _keyword_similarity(query_tokens: list[str], target_tokens: list[str]) -> float:
    if not query_tokens or not target_tokens:
        return 0.0
    query_set = set(query_tokens)
    target_set = set(target_tokens)
    intersection = query_set & target_set
    if not intersection:
        for qt in query_tokens:
            for tt in target_tokens:
                if qt in tt or tt in qt:
                    intersection.add(qt)
    union = query_set | target_set
    return len(intersection) / len(union) if union else 0.0


@dataclass
class Episode:
    timestamp: str
    user_message: str
    skill_used: str
    layout: str
    success: bool
    gen_eval_attempts: int = 1
    error_types: list[str] = field(default_factory=list)
    user_feedback: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    def __init__(self, memory_dir: Path = MEMORY_DIR):
        self._dir = memory_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._episodes_file = self._dir / "episodes.jsonl"
        self._preferences_file = self._dir / "preferences.json"
        self._stats_file = self._dir / "skill_stats.json"
        self._cache: list[Episode] | None = None
        self._cache_mtime: float = 0.0

    def _invalidate_cache(self) -> None:
        self._cache = None

    def _load_episodes_cached(self) -> list[Episode]:
        if not self._episodes_file.exists():
            return []
        current_mtime = self._episodes_file.stat().st_mtime
        if self._cache is not None and current_mtime == self._cache_mtime:
            return self._cache

        lines = self._episodes_file.read_text(encoding="utf-8").strip().split("\n")
        episodes = []
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                episodes.append(Episode(**data))
            except (json.JSONDecodeError, TypeError):
                continue
        self._cache = episodes
        self._cache_mtime = current_mtime
        return episodes

    def save_episode(self, episode: Episode) -> None:
        with open(self._episodes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(episode), ensure_ascii=False) + "\n")
        self._invalidate_cache()
        self._update_stats(episode)
        logger.info(f"[Memory] 에피소드 저장: skill={episode.skill_used}, success={episode.success}")

    def get_recent_episodes(self, limit: int = 10) -> list[Episode]:
        episodes = self._load_episodes_cached()
        return list(reversed(episodes[-limit:]))

    def get_similar_episodes(self, skill: str, limit: int = 5, query: str = "") -> list[Episode]:
        all_episodes = self._load_episodes_cached()

        if not query:
            return [ep for ep in reversed(all_episodes) if ep.skill_used == skill][:limit]

        query_tokens = _tokenize(query)
        scored: list[tuple[float, Episode]] = []

        for ep in all_episodes:
            score = 0.0
            if ep.skill_used == skill:
                score += 0.5

            ep_tokens = _tokenize(ep.user_message)
            sim = _keyword_similarity(query_tokens, ep_tokens)
            score += sim * 0.5

            if score > 0.05:
                scored.append((score, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:limit]]

    def get_skill_success_patterns(self, skill: str) -> dict[str, Any]:
        """특정 스킬의 성공/실패 패턴 분석"""
        episodes = [ep for ep in self._load_episodes_cached() if ep.skill_used == skill]
        if not episodes:
            return {}

        successful = [ep for ep in episodes if ep.success]
        failed = [ep for ep in episodes if not ep.success]

        layout_counter: Counter[str] = Counter()
        for ep in successful:
            if ep.layout:
                layout_counter[ep.layout] += 1

        error_counter: Counter[str] = Counter()
        for ep in failed:
            for err in ep.error_types:
                error_counter[err] += 1

        return {
            "total": len(episodes),
            "success_count": len(successful),
            "fail_count": len(failed),
            "best_layouts": layout_counter.most_common(3),
            "common_errors": error_counter.most_common(3),
            "avg_attempts": (round(sum(ep.gen_eval_attempts for ep in episodes) / len(episodes), 1) if episodes else 0),
        }

    def save_preference(self, key: str, value: Any) -> None:
        prefs = self._load_preferences()
        prefs[key] = {
            "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._preferences_file.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_preference(self, key: str, default: Any = None) -> Any:
        prefs = self._load_preferences()
        entry = prefs.get(key)
        if entry is None:
            return default
        return entry.get("value", default)

    def get_all_preferences(self) -> dict[str, Any]:
        prefs = self._load_preferences()
        return {k: v.get("value") for k, v in prefs.items()}

    def _load_preferences(self) -> dict[str, Any]:
        if not self._preferences_file.exists():
            return {}
        try:
            return json.loads(self._preferences_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def get_skill_stats(self) -> dict[str, Any]:
        if not self._stats_file.exists():
            return {}
        try:
            return json.loads(self._stats_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _update_stats(self, episode: Episode) -> None:
        stats = self.get_skill_stats()
        skill = episode.skill_used or "unknown"

        if skill not in stats:
            stats[skill] = {"total": 0, "success": 0, "fail": 0, "avg_attempts": 0.0}

        entry = stats[skill]
        entry["total"] += 1
        if episode.success:
            entry["success"] += 1
        else:
            entry["fail"] += 1

        total = entry["total"]
        prev_avg = entry["avg_attempts"]
        entry["avg_attempts"] = round(prev_avg + (episode.gen_eval_attempts - prev_avg) / total, 2)

        self._stats_file.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    def build_memory_context(self, skill: str = "", query: str = "", limit: int = 3) -> str:
        """AI 프롬프트에 주입할 메모리 컨텍스트 빌드"""
        parts: list[str] = []

        prefs = self.get_all_preferences()
        if prefs:
            pref_lines = [f"- {k}: {v}" for k, v in list(prefs.items())[:5]]
            parts.append("## User Preferences\n" + "\n".join(pref_lines))

        if skill:
            similar = self.get_similar_episodes(skill, limit=limit, query=query)
            successful = [ep for ep in similar if ep.success]
            if successful:
                parts.append(f"## Past Successful {skill} Generations")
                for ep in successful[:2]:
                    feedback = f" (feedback: {ep.user_feedback})" if ep.user_feedback else ""
                    parts.append(f"- layout={ep.layout}, attempts={ep.gen_eval_attempts}{feedback}")

            failed = [ep for ep in similar if not ep.success]
            if failed:
                errors = set()
                for ep in failed:
                    errors.update(ep.error_types[:2])
                if errors:
                    parts.append(f"⚠️ Common errors for {skill}: {', '.join(list(errors)[:3])}")

            patterns = self.get_skill_success_patterns(skill)
            if patterns and patterns.get("best_layouts"):
                best = patterns["best_layouts"][0]
                parts.append(f"💡 Best layout for {skill}: {best[0]} ({best[1]} successes)")

        stats = self.get_skill_stats()
        if skill and skill in stats:
            s = stats[skill]
            rate = round(s["success"] / s["total"] * 100) if s["total"] > 0 else 0
            parts.append(f"📊 {skill} success rate: {rate}% ({s['total']} total)")

        return "\n".join(parts) if parts else ""

    def clear(self) -> None:
        for f in [self._episodes_file, self._preferences_file, self._stats_file]:
            if f.exists():
                f.unlink()
        self._invalidate_cache()


memory = EpisodicMemory()
