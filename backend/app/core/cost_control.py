"""세션 단위 LLM 호출 예산 — 비용 폭주 방지 (SEC-17).

ContextVar 기반이라 동시 세션(다중 WebSocket/요청) 간 격리된다.
예산이 설정되지 않으면(기본) 모든 함수는 무동작(no-op)이므로,
오케스트레이터 밖에서 직접 호출되는 경로(단위 테스트 등)는 영향받지 않는다.

사용:
    set_budget(settings.max_llm_calls_per_session)   # 세션 시작 시
    ...
    note_call()   # 각 LLM 호출 직전 (상한 초과 시 BudgetExceededError)

향후 provider가 usage(토큰)를 보고하면 note_tokens()로 누적하여 비용 가시화로 확장한다.
"""

import contextvars
import logging
from dataclasses import dataclass

logger = logging.getLogger("notionforge.cost")


class BudgetExceededError(RuntimeError):
    """세션 LLM 호출 상한 초과."""


@dataclass
class CostBudget:
    max_calls: int = 30
    calls: int = 0
    tokens: int = 0  # provider usage 보고 시 누적 (현재는 note_tokens로만 채워짐)

    def note_call(self) -> None:
        self.calls += 1
        if self.calls > self.max_calls:
            raise BudgetExceededError(f"세션 LLM 호출 상한 초과: {self.calls}/{self.max_calls}")

    def note_tokens(self, n: int) -> None:
        if n > 0:
            self.tokens += n


_budget: contextvars.ContextVar[CostBudget | None] = contextvars.ContextVar("cost_budget", default=None)


def set_budget(max_calls: int) -> CostBudget:
    """현재 컨텍스트(태스크)에 새 예산을 설정하고 반환."""
    b = CostBudget(max_calls=max_calls)
    _budget.set(b)
    return b


def reset_budget() -> None:
    _budget.set(None)


def current_budget() -> CostBudget | None:
    return _budget.get()


def note_call() -> None:
    """LLM 호출 1건 기록. 예산 미설정이면 no-op. 상한 초과 시 BudgetExceededError 발생."""
    b = _budget.get()
    if b is not None:
        b.note_call()


def note_tokens(n: int) -> None:
    """토큰 사용량 누적 (예산 미설정이면 no-op)."""
    b = _budget.get()
    if b is not None:
        b.note_tokens(n)
