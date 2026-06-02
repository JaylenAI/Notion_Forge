"""ExemplarRetriever 단위 + 실데이터(recipe 코퍼스) 검증 (Phase A5)."""

from app.agent import exemplar_retriever as er
from app.agent.exemplar_retriever import build_exemplar_hint, load_corpus, retrieve_exemplars


def test_corpus_loads_recipes():
    corpus = load_corpus()
    assert len(corpus) >= 3  # crm/okr/project/reading
    assert all("blueprint" in r for r in corpus)


def test_retrieve_matches_crm_domain():
    top = retrieve_exemplars("고객 관리 CRM 영업 파이프라인 만들어줘", k=1)
    assert top and top[0]["id"] == "crm-dashboard"


def test_retrieve_matches_okr_domain():
    top = retrieve_exemplars("OKR 목표 관리 대시보드", k=1)
    assert top and top[0]["id"] == "okr-dashboard"


def test_retrieve_matches_korean_only_request():
    """영어 태그 없이 한국어만 써도 매칭돼야 함(라이브에서 발견한 누락 보완)."""
    top = retrieve_exemplars("고객 관리 영업 시스템 만들어줘", k=1)
    assert top and top[0]["id"] == "crm-dashboard"
    assert build_exemplar_hint("고객 관리 영업 시스템 만들어줘")  # 멀티DB 힌트 주입됨


def test_retrieve_returns_empty_for_unrelated():
    assert retrieve_exemplars("xyzzy 아무 의미 없는 요청 12345") == []


def test_hint_for_multidb_domain_mentions_structure():
    hint = build_exemplar_hint("고객 관리 CRM 파이프라인")
    assert hint  # 비어있지 않음
    assert "relation" in hint
    assert "멀티" in hint or "DB" in hint


def test_hint_empty_for_unrelated():
    assert build_exemplar_hint("xyzzy 무관한 요청") == ""


def test_hint_skips_single_db_exemplar(monkeypatch):
    """매칭돼도 단일DB 예시는 '멀티DB 모방' 가치가 없으므로 주입 안 함."""
    single_db_recipe = {
        "name": "심플",
        "blueprint": {"databases": [{"title": "목록", "properties": {"이름": "title"}}]},
    }
    monkeypatch.setattr(er, "retrieve_exemplars", lambda msg, k=1: [single_db_recipe])
    assert build_exemplar_hint("아무 요청") == ""
