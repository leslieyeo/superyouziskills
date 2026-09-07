"""单测 dcf.run_dcf — 纯数学，无网络，手算期望值。"""
from __future__ import annotations
import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))

from szdata.dcf import run_dcf


def _hand_compute(fcf0, growth_5y, terminal_g, wacc, net_debt, shares, price):
    """独立实现，与 run_dcf 无共用代码，只是数学公式。"""
    pv1 = sum(fcf0 * (1 + growth_5y) ** t / (1 + wacc) ** t for t in range(1, 6))
    fcf5 = fcf0 * (1 + growth_5y) ** 5
    tv = fcf5 * (1 + terminal_g) / (wacc - terminal_g)
    pv2 = tv / (1 + wacc) ** 5
    ev = pv1 + pv2
    equity = ev - net_debt
    per_share = equity / shares if shares else None
    safety = (per_share / price - 1) * 100 if (per_share is not None and price) else None
    return ev, equity, per_share, safety


def test_run_dcf_basic():
    fcf0, g, tg, wacc, nd, sh, p = 100, 0.05, 0.025, 0.10, 0.0, 100, 10.0
    exp_ev, exp_eq, exp_ps, exp_sm = _hand_compute(fcf0, g, tg, wacc, nd, sh, p)
    out = run_dcf(fcf0=fcf0, growth_5y=g, terminal_g=tg,
                  wacc=wacc, net_debt=nd, shares=sh, price=p)
    assert out["ok"] is True
    assert math.isclose(out["ev"], exp_ev, rel_tol=1e-6)
    assert math.isclose(out["equity_value"], exp_eq, rel_tol=1e-6)
    assert math.isclose(out["per_share"], exp_ps, rel_tol=1e-6)
    assert math.isclose(out["safety_margin_pct"], exp_sm, rel_tol=1e-6)


def test_run_dcf_wacc_lte_terminal_g_error():
    out = run_dcf(fcf0=100, growth_5y=0.05, terminal_g=0.09, wacc=0.09)
    assert out["ok"] is False
    assert "wacc" in out["error"]


def test_run_dcf_no_shares_no_per_share():
    out = run_dcf(fcf0=100, growth_5y=0.05)
    assert out["ok"] is True
    assert out["per_share"] is None
    assert out["safety_margin_pct"] is None


def test_run_dcf_sensitivity_shape():
    out = run_dcf(fcf0=100, growth_5y=0.05, wacc=0.10, terminal_g=0.025,
                  shares=100, price=10)
    sens = out["sensitivity"]
    assert "wacc_axis" in sens
    assert "growth_axis" in sens
    assert "rows" in sens
    assert len(sens["wacc_axis"]) == 3
    assert len(sens["growth_axis"]) == 3
    assert len(sens["rows"]) == 3
    assert len(sens["rows"][0]) == 3


def test_run_dcf_negative_fcf0_allowed():
    out = run_dcf(fcf0=-50, growth_5y=0.05, wacc=0.10, terminal_g=0.025)
    assert out["ok"] is True
    assert out["ev"] < 0


def test_run_dcf_magnitude_warning_when_ratio_too_large():
    """fcf0 误传万元量级时 per_share >> price，应触发 warning。"""
    # 正常单位：fcf0=100亿元, shares=100亿股 → per_share≈10-20元
    # 误传：fcf0=100万元（= 0.000001 亿元），但 price=10 元 → per_share≈0，ratio<0.02
    # 反向：fcf0 夸大 10000 倍，per_share≈10万，ratio>>50
    out = run_dcf(fcf0=1_000_000, growth_5y=0.05, wacc=0.10, terminal_g=0.025,
                  net_debt=0.0, shares=100, price=10.0)
    assert out["ok"] is True
    assert "warning" in out


def test_run_dcf_no_warning_for_normal_inputs():
    """正常量级输入不应触发 warning。"""
    out = run_dcf(fcf0=100, growth_5y=0.05, wacc=0.10, terminal_g=0.025,
                  net_debt=0.0, shares=100, price=10.0)
    assert out["ok"] is True
    assert "warning" not in out


def test_run_dcf_rejects_invalid_shares_and_price():
    assert run_dcf(fcf0=100, growth_5y=0.05, shares=0)["ok"] is False
    assert run_dcf(fcf0=100, growth_5y=0.05, shares=-10)["ok"] is False
    assert run_dcf(fcf0=100, growth_5y=0.05, price=0)["ok"] is False
    assert run_dcf(fcf0=100, growth_5y=0.05, price=-10)["ok"] is False


def test_run_dcf_rejects_rates_at_or_below_minus_100_percent():
    out = run_dcf(fcf0=100, growth_5y=0.05, wacc=-1, terminal_g=-2)
    assert out["ok"] is False
    assert "-100%" in out["error"]
