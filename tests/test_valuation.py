"""离线测试 valuation.percentile — 纯函数，无网络。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))

import pandas as pd
from szdata.valuation import percentile, extract_values


def test_percentile_empty_series():
    assert percentile([], 5.0) is None


def test_percentile_current_none():
    assert percentile([1, 2, 3, 4], None) is None


def test_percentile_normal():
    # [1,2,3,4]: values <= 2 → 1,2 → 2/4 = 50.0
    assert percentile([1, 2, 3, 4], 2) == 50.0


def test_percentile_max():
    # all values <= 4 → 100.0
    assert percentile([1, 2, 3, 4], 4) == 100.0


def test_percentile_single():
    assert percentile([5], 5) == 100.0


def test_percentile_below_all():
    assert percentile([5, 10, 15], 1) == 0.0

def test_extract_values_filters_invalid_and_non_positive():
    df = pd.DataFrame({"date": ["a", "b", "c", "d"],
                       "value": ["19.5", None, -2, "bad"]})
    assert extract_values(df) == [19.5]

def test_fetch_valuation_uses_current_akshare_api(monkeypatch, tmp_path):
    import akshare as ak
    import szdata.valuation as valuation
    from szdata.cache import Cache
    calls = []

    def fake_fetch(symbol, indicator, period):
        calls.append((symbol, indicator, period))
        values = [10.0, 20.0] if "市盈率" in indicator else [2.0, 3.0]
        return pd.DataFrame({"date": ["2025-01-01", "2026-01-01"],
                             "value": values})

    monkeypatch.setattr(valuation, "_cache", Cache(root=tmp_path))
    monkeypatch.setattr(ak, "stock_zh_valuation_baidu", fake_fetch)
    out = valuation.fetch_valuation("600519")

    assert out["ok"] is True
    assert out["source"] == "akshare-baidu"
    assert out["data"]["pe"] == 20.0
    assert out["data"]["pb"] == 3.0
    assert calls == [
        ("600519", "市盈率(TTM)", "近五年"),
        ("600519", "市净率", "近五年"),
    ]
