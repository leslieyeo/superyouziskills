import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.kline import parse_em_klines, summarize

RAW = [
    "2026-06-08,98.0,100.0,101.0,97.0,400000,1,4.0,2.0,2.0,4.1",
    "2026-06-09,100.0,103.0,104.0,99.0,500000,1,5.0,3.0,3.0,5.1",
    "2026-06-10,103.5,113.3,113.3,103.0,800000,1,10.0,10.0,10.3,8.2",
    "2026-06-11,114.0,110.0,116.0,109.0,900000,1,6.2,-2.9,-3.3,9.0",
]

def test_parse_em_klines():
    rows = parse_em_klines(RAW)
    assert len(rows) == 4
    assert rows[2] == {"date": "2026-06-10", "open": 103.5, "close": 113.3,
                       "high": 113.3, "low": 103.0, "vol": 800000, "turnover_pct": 8.2}

def test_parse_em_klines_with_dash():
    rows = parse_em_klines(["2026-06-09,-,-,-,-,-,-,-,-,-,-"])
    assert rows == []

def test_summarize():
    s = summarize(parse_em_klines(RAW))
    assert s["last_close"] == 110.0
    assert s["n"] == 4
    assert s["pct_3d"] == round((110.0 / 100.0 - 1) * 100, 2)
    assert s["max_high"] == 116.0

def test_eastmoney_turnover_uses_f61_not_amplitude_f58():
    row = parse_em_klines([
        "2026-06-12,1271.18,1291.91,1295,1265.01,50495,1,2.34,1.01,12.91,0.40"
    ])[0]
    assert row["turnover_pct"] == 0.40


def test_fetch_kline_missing_when_fallback_rows_parse_empty(monkeypatch, tmp_path):
    import builtins
    import szdata.cache as cache_mod
    import szdata.kline as kline

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "akshare":
            raise ImportError("akshare unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(kline, "_cache", cache_mod.Cache(root=tmp_path))
    monkeypatch.setattr(kline, "http_get_json", lambda *args, **kwargs: {
        "data": {"klines": ["2026-06-09,-,-,-,-,-,-,-,-,-,-"]}
    })

    out = kline.fetch_kline("600519")
    assert out["ok"] is False
    assert "K线" in out["hint"]
