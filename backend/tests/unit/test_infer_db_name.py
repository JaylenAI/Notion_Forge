"""DB명 유추 테스트 — generic '데이터베이스 N' 폴백 방지 (라이브 출판사 회귀 고정).

AI가 DB title을 누락해도: ① 역방향 relation 이름 ② description 핵심 명사
③ 구별되는 title 속성명 순으로 의미 있는 DB명을 만든다.
"""

from app.agent.blueprint_generator import _db_name_from_description, _infer_db_name


def test_desc_noun_extraction():
    assert _db_name_from_description("출판사 작가 정보") == "작가"
    assert _db_name_from_description("출판된 도서 정보") == "도서"
    assert _db_name_from_description("도서 판매 기록") == "판매"
    assert _db_name_from_description("고객 정보") == "고객"


def test_desc_noun_skips_empty_and_long():
    assert _db_name_from_description("") is None
    assert _db_name_from_description(None) is None
    # 문장형(>4 토큰)은 신뢰 낮아 스킵
    assert _db_name_from_description("이 데이터베이스는 모든 작가를 자세히 관리하는 곳입니다") is None


def test_infer_prefers_reverse_relation():
    dbs = [
        {"title": "고객", "properties": {"이름": "title", "거래": {"type": "relation", "target_db_index": 1}}},
        {"properties": {"제목": "title"}, "description": "거래 내역"},
    ]
    # DB1은 고객의 '거래' relation 대상 → '거래'
    assert _infer_db_name(dbs, 1) == "거래"


def test_infer_falls_back_to_description():
    """역방향 relation이 없으면 description 핵심 명사를 쓴다 (출판사 케이스)."""
    dbs = [
        {"properties": {"이름": "title"}, "description": "출판사 작가 정보"},
        {"properties": {"제목": "title"}, "description": "출판된 도서 정보"},
        {"properties": {"판매 ID": "title"}, "description": "도서 판매 기록"},
    ]
    assert _infer_db_name(dbs, 0) == "작가"
    assert _infer_db_name(dbs, 1) == "도서"
    assert _infer_db_name(dbs, 2) == "판매"


def test_infer_falls_back_to_distinctive_title_prop():
    """relation·description 없으면 구별되는 title 속성명에서 유추 (판매 ID → 판매)."""
    dbs = [{"properties": {"판매 ID": "title", "금액": "number"}}]
    assert _infer_db_name(dbs, 0) == "판매"


def test_infer_returns_none_when_nothing_distinctive():
    """단서가 없으면 None (호출부가 generic 폴백 사용)."""
    dbs = [{"properties": {"이름": "title"}}]
    assert _infer_db_name(dbs, 0) is None
