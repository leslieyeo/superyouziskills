import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.fundamentals import pick_info

RAW = {"股票简称": "贵州茅台", "行业": "白酒", "总市值": 1797350000000.0,
       "流通市值": 1797350000000.0, "上市时间": 20010827}

def test_pick_info():
    d = pick_info(RAW)
    assert d["name"] == "贵州茅台"
    assert d["industry"] == "白酒"
    assert d["mcap_yi"] == round(1797350000000.0 / 1e8, 1)
    assert d["list_date"] == "20010827"


def _make_fake_akshare(monkeypatch):
    """让 akshare import 失败，迫使 fetch_fundamentals 进入 tencent-quote 兜底分支。"""
    import builtins
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "akshare":
            raise ImportError("akshare mocked away")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)


def test_tencent_fallback_empty_name_returns_missing(monkeypatch, tmp_path):
    """tencent-quote 兜底若 name 为空，不发 ok，落到 missing_result。"""
    import szdata.fundamentals as fm
    import szdata.cache as cache_mod
    import szdata.quote as quote_mod
    monkeypatch.setattr(fm, "_cache", cache_mod.Cache(root=tmp_path))
    _make_fake_akshare(monkeypatch)

    fake_quote = {"ok": True, "data": {"name": "", "mcap_yi": 100.0}}
    monkeypatch.setattr(quote_mod, "fetch_quote", lambda code: fake_quote)

    out = fm.fetch_fundamentals("000001")
    assert out["ok"] is False


def test_tencent_fallback_none_mcap_returns_missing(monkeypatch, tmp_path):
    """tencent-quote 兜底若 mcap_yi 为 None，不发 ok，落到 missing_result。"""
    import szdata.fundamentals as fm
    import szdata.cache as cache_mod
    import szdata.quote as quote_mod
    monkeypatch.setattr(fm, "_cache", cache_mod.Cache(root=tmp_path))
    _make_fake_akshare(monkeypatch)

    fake_quote = {"ok": True, "data": {"name": "某股票", "mcap_yi": None}}
    monkeypatch.setattr(quote_mod, "fetch_quote", lambda code: fake_quote)

    out = fm.fetch_fundamentals("000001")
    assert out["ok"] is False


def test_tencent_fallback_valid_sets_partial(monkeypatch, tmp_path):
    """tencent-quote 兜底成功时 partial=True 且 ok=True。"""
    import szdata.fundamentals as fm
    import szdata.cache as cache_mod
    import szdata.quote as quote_mod
    monkeypatch.setattr(fm, "_cache", cache_mod.Cache(root=tmp_path))
    _make_fake_akshare(monkeypatch)

    fake_quote = {"ok": True, "data": {"name": "某股票", "mcap_yi": 200.0}}
    monkeypatch.setattr(quote_mod, "fetch_quote", lambda code: fake_quote)

    out = fm.fetch_fundamentals("000001")
    assert out["ok"] is True
    assert out.get("partial") is True
