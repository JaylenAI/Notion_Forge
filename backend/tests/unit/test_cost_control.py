"""세션 LLM 호출 예산(SEC-17) 단위 테스트."""

import pytest

from app.core.cost_control import (
    BudgetExceededError,
    CostBudget,
    current_budget,
    note_call,
    note_tokens,
    reset_budget,
    set_budget,
)


def test_unset_budget_is_noop():
    reset_budget()
    assert current_budget() is None
    # 예산 미설정이면 호출 기록은 무동작 (예외 없음)
    for _ in range(1000):
        note_call()
    note_tokens(99999)
    assert current_budget() is None


def test_budget_counts_calls():
    b = set_budget(max_calls=5)
    assert current_budget() is b
    for _ in range(5):
        note_call()
    assert b.calls == 5


def test_budget_raises_when_exceeded():
    set_budget(max_calls=3)
    note_call()
    note_call()
    note_call()
    with pytest.raises(BudgetExceededError):
        note_call()  # 4번째 → 상한 초과


def test_set_budget_resets_count():
    set_budget(max_calls=2)
    note_call()
    set_budget(max_calls=2)  # 새 세션 → 카운트 리셋
    assert current_budget().calls == 0


def test_note_tokens_accumulates():
    b = set_budget(max_calls=10)
    note_tokens(100)
    note_tokens(50)
    note_tokens(-5)  # 음수는 무시
    assert b.tokens == 150


def test_cost_budget_dataclass_direct():
    b = CostBudget(max_calls=2)
    b.note_call()
    b.note_call()
    with pytest.raises(BudgetExceededError):
        b.note_call()
