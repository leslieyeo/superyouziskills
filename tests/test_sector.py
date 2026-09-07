import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.sector import summarize_zt

ZT = [{"name": "A", "lbc": 1}, {"name": "B", "lbc": 3}, {"name": "C", "lbc": 1},
      {"name": "D", "lbc": 5}]

def test_summarize_zt():
    s = summarize_zt(ZT)
    assert s["zt_count"] == 4
    assert s["max_lianban"] == 5
    assert s["lianban_ge2"] == 2

def test_summarize_zt_empty():
    s = summarize_zt([])
    assert s == {"zt_count": 0, "max_lianban": 0, "lianban_ge2": 0}


def test_panel_partial_promotes_hint_when_boards_missing(monkeypatch, tmp_path):
    import builtins
    import szdata.cache as cache_mod
    import szdata.sector as sector

    real_import = builtins.__import__

    class FakeAkshare:
        @staticmethod
        def stock_zt_pool_em(date):
            return pd.DataFrame([{"名称": "A", "代码": "000001", "连板数": 2,
                                  "所属行业": "银行"}])

        @staticmethod
        def stock_board_industry_name_em():
            return pd.DataFrame(columns=["板块名称", "涨跌幅"])

    def fake_import(name, *args, **kwargs):
        if name == "akshare":
            return FakeAkshare
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(sector, "_cache", cache_mod.Cache(root=tmp_path))
    monkeypatch.setattr(sector, "http_get_json", lambda *args, **kwargs: None)

    out = sector.fetch_market_panel()
    assert out["ok"] is True
    assert out["partial"] is True
    assert out["data"]["partial"] is True
    assert out["data"]["top_boards"] == []
    assert "板块涨幅榜" in out["hint"]
