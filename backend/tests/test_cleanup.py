from app.core.storage import LocalStorage
from app.worker import tasks


def test_sweep_removes_only_unreferenced_files(tmp_path):
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

    store = LocalStorage(root=str(tmp_path))
    removed = tasks._sweep_local_orphans({"uploads/keep.pdf"}, store)

    assert removed == 1
    assert keep.exists()
    assert gitkeep.exists()  # never swept
    assert not orphan.exists()
