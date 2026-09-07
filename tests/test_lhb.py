import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.lhb import normalize_rows

RAW = [{"TRADE_DATE": "2026-06-10 00:00:00", "EXPLANATION": "日涨幅偏离值达7%",
        "BILLBOARD_NET_AMT": 12345678.0, "BILLBOARD_BUY_AMT": 50000000.0,
        "BILLBOARD_SELL_AMT": 37654322.0, "TURNOVERRATE": 12.3}]

def test_normalize_rows():
    rows = normalize_rows(RAW)
    assert rows[0]["date"] == "2026-06-10"
    assert rows[0]["reason"] == "日涨幅偏离值达7%"
    assert rows[0]["net_buy_wan"] == round(12345678.0 / 1e4, 1)
    assert rows[0]["buy_wan"] == 5000.0

def test_normalize_empty():
    assert normalize_rows([]) == []

def test_api_error_is_not_reported_as_valid_empty_result(monkeypatch, tmp_path):
    import szdata.lhb as lhb
    from szdata.cache import Cache
    monkeypatch.setattr(lhb, "_cache", Cache(root=tmp_path))
    monkeypatch.setattr(
        lhb, "http_get_json",
        lambda *args, **kwargs: {"success": False, "code": 9201},
    )
    out = lhb.fetch_lhb("600519")
    assert out["ok"] is False

def test_successful_empty_response_is_valid(monkeypatch, tmp_path):
    import szdata.lhb as lhb
    from szdata.cache import Cache
    monkeypatch.setattr(lhb, "_cache", Cache(root=tmp_path))
    monkeypatch.setattr(
        lhb, "http_get_json",
        lambda *args, **kwargs: {"success": True, "result": {"data": []}},
    )
    out = lhb.fetch_lhb("600519")
    assert out["ok"] is True
    assert out["data"] == []
