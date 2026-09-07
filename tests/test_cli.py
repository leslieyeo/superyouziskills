import json, os, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skill" / "scripts" / "fetch.py"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))

ENV = {**os.environ, "SUPERYOUZI_CACHE": tempfile.mkdtemp(prefix="szcache-test-")}

def test_cli_unknown_kind_exits_with_usage():
    p = subprocess.run([sys.executable, str(SCRIPT), "nope", "600519"],
                       capture_output=True, text=True, env=ENV)
    assert p.returncode == 2
    assert "用法" in p.stderr

def test_cli_dcf_exits_2_with_message():
    p = subprocess.run([sys.executable, str(SCRIPT), "dcf", "600519"],
                       capture_output=True, text=True, env=ENV)
    assert p.returncode == 2
    assert "dcf" in p.stderr
    assert "szdata.dcf.run_dcf" in p.stderr

def test_cli_invalid_code_exits_2_before_network_access():
    p = subprocess.run([sys.executable, str(SCRIPT), "all", "../../escaped"],
                       capture_output=True, text=True, env=ENV)
    assert p.returncode == 2
    assert "无效股票代码" in p.stderr


def test_cli_outputs_json_offline_via_cache():
    from szdata.cache import Cache
    cache_dir = Path(ENV["SUPERYOUZI_CACHE"])
    Cache(root=cache_dir).set("quote", "600519",
                {"ok": True, "source": "cache-fixture", "data": {"price": 1.0},
                 "fetched_at": "2026-06-12T00:00:00", "hint": ""})
    p = subprocess.run([sys.executable, str(SCRIPT), "quote", "600519"],
                       capture_output=True, text=True, timeout=30, env=ENV)
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["ok"] is True and out["source"] == "cache-fixture"


def test_cache_env_isolation():
    """SUPERYOUZI_CACHE 环境变量生效时，Cache() 的 root 指向该目录。"""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="szcache-iso-")
    old = os.environ.pop("SUPERYOUZI_CACHE", None)
    try:
        os.environ["SUPERYOUZI_CACHE"] = tmp
        # Re-import to pick up env — import inside function to avoid module-level caching
        import importlib
        import szdata.cache as cache_mod
        importlib.reload(cache_mod)
        c = cache_mod.Cache()
        assert str(c.root) == tmp
    finally:
        if old is None:
            os.environ.pop("SUPERYOUZI_CACHE", None)
        else:
            os.environ["SUPERYOUZI_CACHE"] = old
        import importlib
        import szdata.cache as cache_mod
        importlib.reload(cache_mod)

def test_all_reports_failure_when_every_dimension_is_missing(tmp_path):
    from szdata.cache import Cache
    env = {**os.environ, "SUPERYOUZI_CACHE": str(tmp_path)}
    missing = {"ok": False, "source": "missing", "data": None,
               "fetched_at": "2026-06-13T00:00:00", "hint": "fixture"}
    cache = Cache(root=tmp_path)
    for kind in ("quote", "lhb", "flow", "sentiment", "fund",
                 "finhist", "val", "holders"):
        cache.set(kind, "600519", missing)
    cache.set("kline", "600519_30", missing)

    p = subprocess.run([sys.executable, str(SCRIPT), "all", "600519"],
                       capture_output=True, text=True, timeout=30, env=env)
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["ok"] is False
    assert out["partial"] is True
    assert "quote" in out["hint"]


def test_all_promotes_child_partial_to_top_level(tmp_path):
    from szdata.cache import Cache
    env = {**os.environ, "SUPERYOUZI_CACHE": str(tmp_path)}
    ok = {"ok": True, "source": "fixture", "data": {"value": 1},
          "fetched_at": "2026-06-13T00:00:00", "hint": ""}
    partial = {"ok": True, "source": "fixture", "data": {"value": 1},
               "fetched_at": "2026-06-13T00:00:00",
               "partial": True, "hint": "行业/流通市值缺失"}
    cache = Cache(root=tmp_path)
    for kind in ("quote", "lhb", "flow", "sentiment", "fund",
                 "finhist", "val", "holders"):
        cache.set(kind, "600519", partial if kind == "fund" else ok)
    cache.set("kline", "600519_30", ok)

    p = subprocess.run([sys.executable, str(SCRIPT), "all", "600519"],
                       capture_output=True, text=True, timeout=30, env=env)
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["ok"] is True
    assert out["partial"] is True
    assert "部分维度需补充" in out["hint"]
    assert "fund" in out["hint"]
