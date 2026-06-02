"""status/select 옵션 coercion 테스트 (E2E 품질보정).

AI가 옵션을 문자열로 주면 Notion은 {name,color} 객체를 기대해 400이 났다
(status가 raw 통과하던 결함). 문자열·객체 모두 객체로 강제됨을 검증.
"""

from app.notion.block_builder import build_database_properties


def test_status_options_coerced_from_strings():
    out = build_database_properties(
        {"이름": {"type": "title"}, "상태": {"type": "status", "options": ["시작 전", "진행 중", "완료"]}}
    )
    opts = out["상태"]["status"]["options"]
    assert all(isinstance(o, dict) and "name" in o and "color" in o for o in opts)
    assert {o["name"] for o in opts} == {"시작 전", "진행 중", "완료"}


def test_select_options_coerced_mixed():
    out = build_database_properties(
        {"이름": {"type": "title"}, "분류": {"type": "select", "options": ["A", {"name": "B", "color": "blue"}]}}
    )
    opts = out["분류"]["select"]["options"]
    assert {o["name"] for o in opts} == {"A", "B"}
    assert any(o["name"] == "B" and o["color"] == "blue" for o in opts)
    # 문자열 옵션도 객체화 + 유효 색 폴백
    assert all(isinstance(o, dict) and "name" in o for o in opts)
