"""rollup 샘플 링크 폴백 결정적 테스트 — 라이브에서 발견한 'rollup 집계 0' 회귀 고정.

AI/recipe가 샘플 relation 값을 누락하거나 대상 제목과 안 맞으면 제목 매칭 해석이 0건이라
rollup이 0/None으로 집계되지 않았다(습관 트래커 라이브 케이스). 폴백 오토링커는 rollup을
먹이는 relation에 한해 대상 샘플을 라운드로빈 배정해 반드시 집계되게 한다.
"""

from app.agent.creation_executor import CreationExecutor


def _title_row(rid: str, title: str) -> dict:
    return {"id": rid, "properties": {"이름": {"type": "title", "title": [{"plain_text": title}]}}}


class _FakeClient:
    """post_process_sample_links가 쓰는 query_database/update_page만 가진 가짜 클라이언트."""

    def __init__(self, db_rows: dict[str, list]):
        self._db_rows = db_rows
        self.updates: list[tuple[str, dict]] = []

    async def query_database(self, db_id: str):
        return self._db_rows.get(db_id, [])

    async def update_page(self, page_id: str, properties: dict | None = None):
        self.updates.append((page_id, properties or {}))
        return {"id": page_id}


def _blueprint(habit_samples: list[dict]) -> dict:
    return {
        "databases": [
            {
                "title": "습관",
                "properties": {
                    "이름": {"type": "title"},
                    "일일기록": {"type": "relation", "target_db_index": 1},
                    "전체기록": {
                        "type": "rollup",
                        "relation_property": "일일기록",
                        "rollup_property": "이름",
                        "function": "count",
                    },
                },
                "sample_items": habit_samples,
            },
            {
                "title": "일일기록",
                "properties": {
                    "이름": {"type": "title"},
                    "습관": {"type": "relation", "target_db_index": 0},
                },
                "sample_items": [{"이름": "1일차"}, {"이름": "2일차"}, {"이름": "3일차"}],
            },
        ],
    }


def _linked_targets(updates: list[tuple[str, dict]], rel_name: str) -> dict[str, set]:
    linked: dict[str, set] = {}
    for pid, props in updates:
        rel = props.get(rel_name, {}).get("relation")
        if rel:
            linked.setdefault(pid, set()).update(r["id"] for r in rel)
    return linked


def _client_and_result() -> tuple[_FakeClient, dict]:
    habit_rows = [_title_row("habit-0", "운동"), _title_row("habit-1", "독서")]
    log_rows = [_title_row("log-0", "1일차"), _title_row("log-1", "2일차"), _title_row("log-2", "3일차")]
    client = _FakeClient({"db0": habit_rows, "db1": log_rows})
    return client, {"databases": [{"id": "db0"}, {"id": "db1"}]}


async def test_fallback_wires_rollup_relation_when_titles_mismatch():
    """제목 불일치/누락으로 해석이 0건이어도 폴백이 rollup용 relation을 연결한다."""
    blueprint = _blueprint([{"이름": "운동", "일일기록": "존재하지않는행"}, {"이름": "독서"}])
    client, result = _client_and_result()

    await CreationExecutor(client, None).post_process_sample_links(blueprint, result)

    linked = _linked_targets(client.updates, "일일기록")
    all_targets = set().union(*linked.values()) if linked else set()
    # 폴백이 일일기록 3개를 습관 행들에 라운드로빈 배정 → rollup이 집계할 링크 존재
    assert all_targets == {"log-0", "log-1", "log-2"}, f"폴백 링크 누락: {linked}"
    assert any(linked.get(h) for h in ("habit-0", "habit-1")), "습관 행에 일일기록 링크 0건"


async def test_fallback_preserves_ai_links_when_titles_match():
    """AI가 매칭되는 제목을 주면 폴백이 라운드로빈으로 덮어쓰지 않는다(의미 보존)."""
    blueprint = _blueprint([{"이름": "운동", "일일기록": ["1일차", "2일차"]}, {"이름": "독서"}])
    client, result = _client_and_result()

    await CreationExecutor(client, None).post_process_sample_links(blueprint, result)

    linked = _linked_targets(client.updates, "일일기록")
    # habit-0(운동)은 AI가 준 1일차·2일차만 — 폴백이 3일차를 추가로 라운드로빈하지 않음
    assert linked.get("habit-0") == {"log-0", "log-1"}, f"AI 링크 변형됨: {linked.get('habit-0')}"


async def test_fallback_skips_relation_without_rollup():
    """rollup이 참조하지 않는 relation은 폴백이 건드리지 않는다."""
    blueprint = _blueprint([{"이름": "운동"}, {"이름": "독서"}])
    # 습관의 rollup을 제거 → '일일기록' relation은 rollup을 먹이지 않음
    del blueprint["databases"][0]["properties"]["전체기록"]
    client, result = _client_and_result()

    await CreationExecutor(client, None).post_process_sample_links(blueprint, result)

    linked = _linked_targets(client.updates, "일일기록")
    assert not linked, f"rollup 없는 relation을 폴백이 연결함: {linked}"
