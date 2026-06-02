"""토큰 집계 테스트 (Phase 5/C1) — provider note_tokens → metrics.tokens_used 실측.

기존: tokens_used가 한 번도 set 안 돼 /metrics가 항상 0(정직성 결함).
이제 provider가 note_tokens로 누적 → metrics.finish가 세션 토큰을 기록.
"""

from app.core.cost_control import note_tokens, reset_budget, set_budget
from app.core.metrics import GenerationMetrics


def test_metrics_finish_records_session_tokens():
    reset_budget()
    set_budget(40)
    note_tokens(1500)  # provider 호출 1
    note_tokens(500)  # provider 호출 2
    m = GenerationMetrics(skill="crm")
    m.finish()
    assert m.tokens_used == 2000
    reset_budget()


def test_metrics_finish_no_budget_keeps_zero():
    reset_budget()
    m = GenerationMetrics()
    m.finish()
    assert m.tokens_used == 0


def test_note_tokens_noop_without_budget():
    reset_budget()
    note_tokens(999)  # 예산 미설정 → no-op, 에러 없어야
    from app.core.cost_control import current_budget

    assert current_budget() is None
