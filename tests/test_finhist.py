"""离线测试 finhist.pick_years / _only_annual — 纯函数，无网络。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))

from szdata.finhist import pick_years, _only_annual


def _row(year, roe, rev, prof, debt):
    return {"year": year, "roe": roe, "revenue_yoy": rev,
            "profit_yoy": prof, "debt_ratio": debt}


def test_pick_years_normal_5():
    rows = [
        _row("2020", "10.1", "5.0", "8.0", "40.0"),
        _row("2021", "11.2", "6.1", "9.1", "41.0"),
        _row("2022", "12.3", "7.2", "10.2", "42.0"),
        _row("2023", "13.4", "8.3", "11.3", "43.0"),
        _row("2024", "14.5", "9.4", "12.4", "44.0"),
    ]
    out = pick_years(rows)
    assert out["roe_5y"] == [10.1, 11.2, 12.3, 13.4, 14.5]
    assert out["roe_5y_avg"] == round((10.1 + 11.2 + 12.3 + 13.4 + 14.5) / 5, 1)
    assert out["revenue_yoy"] == 9.4
    assert out["profit_yoy"] == 12.4
    assert out["debt_ratio"] == 44.0
    assert out["years"] == ["2020", "2021", "2022", "2023", "2024"]


def test_pick_years_skip_dash_values():
    rows = [
        _row("2020", "-", "-", "-", "40.0"),
        _row("2021", "11.2", "6.1", "-", "41.0"),
        _row("2022", "", "7.2", "10.2", "42.0"),
    ]
    out = pick_years(rows)
    # roe_5y: only 2021 has valid roe (2022 is "")
    assert 11.2 in out["roe_5y"]
    # revenue_yoy: latest with valid value is 2022
    assert out["revenue_yoy"] == 7.2
    # profit_yoy: 2021 has "-", 2022 has valid
    assert out["profit_yoy"] == 10.2


def test_pick_years_empty_list():
    out = pick_years([])
    assert out["roe_5y"] == []
    assert out["roe_5y_avg"] is None
    assert out["revenue_yoy"] is None
    assert out["profit_yoy"] is None
    assert out["debt_ratio"] is None
    assert out["years"] == []


def test_pick_years_truncates_to_5():
    """6 年年报行输入，pick_years 严格只保留最近 5 年。"""
    rows = [
        _row("2019", "9.0", "4.0", "7.0", "39.0"),
        _row("2020", "10.1", "5.0", "8.0", "40.0"),
        _row("2021", "11.2", "6.1", "9.1", "41.0"),
        _row("2022", "12.3", "7.2", "10.2", "42.0"),
        _row("2023", "13.4", "8.3", "11.3", "43.0"),
        _row("2024", "14.5", "9.4", "12.4", "44.0"),
    ]
    out = pick_years(rows)
    assert len(out["roe_5y"]) == 5
    assert len(out["years"]) == 5
    # 最近 5 年：2020-2024
    assert out["years"] == ["2020", "2021", "2022", "2023", "2024"]


def test_only_annual_filters_non_annual():
    """_only_annual 应剔除非 12-31 结尾的行（季报/中报），保留年报。"""
    rows = [
        {"date": "2024-03-31", "roe": "10.0"},
        {"date": "2024-06-30", "roe": "11.0"},
        {"date": "2024-09-30", "roe": "12.0"},
        {"date": "2024-12-31", "roe": "13.0"},
        {"date": "2023-12-31", "roe": "9.0"},
    ]
    result = _only_annual(rows)
    assert len(result) == 2
    dates = [r["date"] for r in result]
    assert "2024-12-31" in dates
    assert "2023-12-31" in dates
    # 非年报行全部剔除
    assert not any(d.endswith(("03-31", "06-30", "09-30")) for d in dates)


def test_only_annual_empty():
    assert _only_annual([]) == []


def test_only_annual_all_non_annual():
    rows = [
        {"date": "2024-09-30", "roe": "12.0"},
        {"date": "2024-06-30", "roe": "11.0"},
    ]
    assert _only_annual(rows) == []
