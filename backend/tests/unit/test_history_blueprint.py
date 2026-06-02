"""history 전체 blueprint 영속성 테스트 (Phase A1)."""

from app.core import history


def test_save_and_load_full_blueprint(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "BLUEPRINT_DIR", tmp_path / "blueprints")
    bp = {"metadata": {"title": "검증템플릿"}, "databases": [{"title": "DB"}], "blocks": []}

    path = history.save_full_blueprint(bp)
    assert path is not None and path.exists()

    loaded = history.load_recent_blueprints(limit=10)
    assert any(b.get("metadata", {}).get("title") == "검증템플릿" for b in loaded)


def test_save_full_blueprint_empty_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "BLUEPRINT_DIR", tmp_path / "blueprints")
    assert history.save_full_blueprint({}) is None


def test_save_generation_record_also_persists_blueprint(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path / "history")
    monkeypatch.setattr(history, "BLUEPRINT_DIR", tmp_path / "blueprints")
    bp = {"metadata": {"title": "기록연동"}, "databases": [{"title": "DB"}], "blocks": []}

    history.save_generation_record({"ok": True}, bp)

    loaded = history.load_recent_blueprints(limit=10)
    assert any(b.get("metadata", {}).get("title") == "기록연동" for b in loaded)


def test_cleanup_removes_old_blueprint_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path / "history")
    bp_root = tmp_path / "blueprints"
    monkeypatch.setattr(history, "BLUEPRINT_DIR", bp_root)
    # 오래된 날짜 디렉토리 생성
    old_dir = bp_root / "2000-01-01"
    old_dir.mkdir(parents=True)
    (old_dir / "x.json").write_text("{}", encoding="utf-8")

    deleted = history.cleanup_old_history(retention_days=30)
    assert deleted >= 1
    assert not old_dir.exists()
