from app.core.config import settings
from app.worker import tasks


def test_sweep_removes_only_unreferenced_files(tmp_path, monkeypatch):
    up = tmp_path / "uploads"
    rep = tmp_path / "reports"
    up.mkdir()
    rep.mkdir()
    keep = up / "keep.pdf"
    keep.write_text("x")
    orphan = up / "orphan.pdf"
    orphan.write_text("y")
    gitkeep = up / ".gitkeep"
    gitkeep.write_text("")

    monkeypatch.setattr(settings, "UPLOAD_DIR", str(up))
    monkeypatch.setattr(settings, "REPORT_DIR", str(rep))

    removed = tasks._sweep_orphans({str(keep)})

    assert removed == 1
    assert keep.exists()
    assert gitkeep.exists()  # never swept
    assert not orphan.exists()
