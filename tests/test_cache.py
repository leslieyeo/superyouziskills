import sys, time
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.cache import Cache

def test_set_get(tmp_path):
    c = Cache(root=tmp_path)
    c.set("quote", "600519", {"price": 1431.0})
    assert c.get("quote", "600519", ttl=60) == {"price": 1431.0}

def test_expired_returns_none(tmp_path):
    c = Cache(root=tmp_path)
    c.set("quote", "600519", {"price": 1431.0})
    p = c._path("quote", "600519")
    old = time.time() - 999
    import os; os.utime(p, (old, old))
    assert c.get("quote", "600519", ttl=60) is None

def test_miss_returns_none(tmp_path):
    assert Cache(root=tmp_path).get("quote", "000000", ttl=60) is None

def test_path_traversal_is_rejected(tmp_path):
    c = Cache(root=tmp_path / "cache")
    with pytest.raises(ValueError):
        c.set("quote", "../../escaped", {"owned": True})
    assert not (tmp_path / "escaped.json").exists()

def test_set_is_atomic_and_leaves_no_temp_file(tmp_path):
    c = Cache(root=tmp_path)
    c.set("quote", "600519", {"price": 1})
    assert c.get("quote", "600519", ttl=60) == {"price": 1}
    assert not list(tmp_path.rglob("*.tmp"))
