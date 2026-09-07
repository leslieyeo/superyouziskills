"""简化两段式 DCF — 纯数学，零网络，零缓存。

由分析端（agent）显式传入假设后调用；不进 fetch.py 子命令。
"""
from __future__ import annotations
import math


def run_dcf(
    fcf0: float,
    growth_5y: float,
    terminal_g: float = 0.025,
    wacc: float = 0.09,
    net_debt: float = 0.0,
    shares: float | None = None,
    price: float | None = None,
) -> dict:
    """两段式 DCF 估值。

    单位约定（必须严格遵守，否则每股估值量级错误）：
        fcf0     — 亿元（自由现金流基期值）
        net_debt — 亿元（净债务，正值表示债务 > 现金）
        shares   — 亿股（总股本）
        price    — 元/股（当前市价）
        equity   — 亿元（= EV − net_debt）
        per_share— 元/股（= equity 亿元 ÷ shares 亿股，量纲自洽）

    Args:
        fcf0: 当期自由现金流（基期），单位亿元
        growth_5y: 第一阶段年增速（如 0.10 = 10%）
        terminal_g: 永续增速（默认 2.5%）
        wacc: 加权平均资本成本（默认 9%）
        net_debt: 净债务（正=债务多于现金），单位亿元，默认 0
        shares: 总股本，单位亿股；None → 不输出每股价值
        price: 当前股价，单位元/股；None → 不输出安全边际

    Returns:
        ok=True 的结果字典，或参数不合法时 ok=False 的错误字典。
        若 per_share/price 量级异常（>50x 或 <0.02x），结果含 "warning" 字段。
    """
    values = {
        "fcf0": fcf0, "growth_5y": growth_5y, "terminal_g": terminal_g,
        "wacc": wacc, "net_debt": net_debt,
    }
    if any(not isinstance(v, (int, float)) or not math.isfinite(v)
           for v in values.values()):
        return {"ok": False, "error": "DCF 参数必须是有限数字"}
    if growth_5y <= -1 or terminal_g <= -1 or wacc <= -1:
        return {"ok": False, "error": "增长率与折现率必须大于 -100%"}
    if wacc <= terminal_g:
        return {"ok": False, "error": "wacc 必须大于永续增长率"}
    if shares is not None and (
        not isinstance(shares, (int, float)) or not math.isfinite(shares)
        or shares <= 0
    ):
        return {"ok": False, "error": "shares 必须是正数"}
    if price is not None and (
        not isinstance(price, (int, float)) or not math.isfinite(price)
        or price <= 0
    ):
        return {"ok": False, "error": "price 必须是正数"}

    # Stage 1: 第 1-5 年 FCF 折现
    stage1_pv = sum(
        fcf0 * (1 + growth_5y) ** t / (1 + wacc) ** t
        for t in range(1, 6)
    )

    # Stage 2: 终值折现
    fcf5 = fcf0 * (1 + growth_5y) ** 5
    terminal_value = fcf5 * (1 + terminal_g) / (wacc - terminal_g)
    stage2_pv = terminal_value / (1 + wacc) ** 5

    ev = stage1_pv + stage2_pv
    equity = ev - net_debt

    per_share = equity / shares if shares is not None else None
    safety_margin_pct = (
        (per_share / price - 1) * 100
        if (per_share is not None and price is not None)
        else None
    )

    sensitivity = _sensitivity(fcf0, growth_5y, terminal_g, wacc,
                                net_debt, shares)

    out: dict = {
        "ok": True,
        "ev": ev,
        "equity_value": equity,
        "per_share": per_share,
        "safety_margin_pct": safety_margin_pct,
        "assumptions": {
            "fcf0": fcf0,
            "growth_5y": growth_5y,
            "terminal_g": terminal_g,
            "wacc": wacc,
            "net_debt": net_debt,
            "shares": shares,
            "price": price,
        },
        "sensitivity": sensitivity,
    }

    if per_share is not None and price is not None:
        ratio = per_share / price
        if ratio is not None and (ratio > 50 or ratio < 0.02):
            out["warning"] = "估值与现价量级差异异常（>50x 或 <0.02x），请检查单位约定与 price 来源是否正确"

    return out


def _sensitivity(fcf0, growth_5y, terminal_g, wacc, net_debt, shares) -> dict:
    """3×3 敏感性表：wacc±1pp × growth±2pp。"""
    wacc_axis = [round(wacc - 0.01, 4), round(wacc, 4), round(wacc + 0.01, 4)]
    growth_axis = [round(growth_5y - 0.02, 4), round(growth_5y, 4),
                   round(growth_5y + 0.02, 4)]

    rows = []
    for w in wacc_axis:
        row = []
        for g in growth_axis:
            if w <= terminal_g:
                row.append(None)
                continue
            pv1 = sum(fcf0 * (1 + g) ** t / (1 + w) ** t for t in range(1, 6))
            fcf5 = fcf0 * (1 + g) ** 5
            tv = fcf5 * (1 + terminal_g) / (w - terminal_g)
            ev = pv1 + tv / (1 + w) ** 5
            equity = ev - net_debt
            ps = equity / shares if shares is not None else None
            row.append(ps)
        rows.append(row)

    return {"wacc_axis": wacc_axis, "growth_axis": growth_axis, "rows": rows}
