"""Metrics: 생성 파이프라인 메트릭 수집

각 생성 세션별로:
- 총 소요시간 / 스테이지별 소요시간
- AI 모델 / 토큰 사용량
- 성공/실패 여부
- 블록/DB/서브페이지 수
"""

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger("notionforge.metrics")


@dataclass
class StageMetric:
    """단일 스테이지 메트릭"""
    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = True
    error: str = ""

    @property
    def duration_ms(self) -> int:
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time) * 1000)
        return 0


@dataclass
class GenerationMetrics:
    """한 번의 템플릿 생성에 대한 전체 메트릭"""
    session_id: str = ""
    user_input: str = ""
    skill: str = ""
    layout: str = ""
    model: str = ""
    complexity: str = "standard"

    # 결과
    blocks_count: int = 0
    databases_count: int = 0
    sub_pages_count: int = 0
    success: bool = False
    error: str = ""

    # AI 관련
    gen_eval_attempts: int = 1
    tokens_used: int = 0

    # 타이밍
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    stages: list[StageMetric] = field(default_factory=list)

    # 현재 진행 중인 스테이지
    _current_stage: StageMetric | None = field(default=None, repr=False)

    def start_stage(self, name: str) -> None:
        """스테이지 시작 기록"""
        self._current_stage = StageMetric(name=name, start_time=time.time())

    def end_stage(self, success: bool = True, error: str = "") -> None:
        """스테이지 종료 기록"""
        if self._current_stage:
            self._current_stage.end_time = time.time()
            self._current_stage.success = success
            self._current_stage.error = error
            self.stages.append(self._current_stage)
            self._current_stage = None

    def finish(self, success: bool = True, error: str = "") -> None:
        """전체 세션 종료"""
        self.end_time = time.time()
        self.success = success
        self.error = error
        self._log_summary()

    @property
    def total_duration_ms(self) -> int:
        end = self.end_time or time.time()
        return int((end - self.start_time) * 1000)

    def _log_summary(self) -> None:
        """메트릭 요약 로깅"""
        stage_summary = {s.name: s.duration_ms for s in self.stages}
        logger.info(
            "[Metrics] 생성 완료",
            extra={
                "skill": self.skill,
                "layout": self.layout,
                "model": self.model,
                "duration_ms": self.total_duration_ms,
                "blocks": self.blocks_count,
                "databases": self.databases_count,
                "attempt": self.gen_eval_attempts,
                "stage": str(stage_summary),
            },
        )

    def to_dict(self) -> dict:
        """직렬화용 dict 변환"""
        return {
            "session_id": self.session_id,
            "user_input": self.user_input[:200],
            "skill": self.skill,
            "layout": self.layout,
            "model": self.model,
            "complexity": self.complexity,
            "blocks_count": self.blocks_count,
            "databases_count": self.databases_count,
            "sub_pages_count": self.sub_pages_count,
            "success": self.success,
            "error": self.error,
            "gen_eval_attempts": self.gen_eval_attempts,
            "tokens_used": self.tokens_used,
            "total_duration_ms": self.total_duration_ms,
            "stages": [
                {"name": s.name, "duration_ms": s.duration_ms, "success": s.success}
                for s in self.stages
            ],
        }
