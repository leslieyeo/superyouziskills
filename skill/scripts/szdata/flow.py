"""主力资金流（近 10 日）。A 源 akshare stock_individual_fund_flow（东财数据）。"""
from __future__ import annotations
from .sources import (
    ok_result, missing_result, http_get_json, code_to_secid, code_to_market,
    validate_a_share_code,
)
from .cache import Cache

_cache = Cache()

def parse_em_fflow(klines: list) -> list:
    rows = []
    for line in klines:
        p = line.split(",")
        if len(p) < 7:
            continue
        try:
            rows.append({"date": p[0],
                         "main_net_wan": round(float(p[1]) / 1e4, 1),
                         "main_net_pct": float(p[6])})
        except (ValueError, TypeError):
            continue
    return rows

def summarize_flow(rows: list) -> dict:
    if not rows:
        return {}
    last3 = rows[-3:]
    return {"last_date": rows[-1]["date"],
            "last_main_net_wan": rows[-1]["main_net_wan"],
            "net_3d_wan": round(sum(r["main_net_wan"] for r in last3), 1),
            "net_3d_days": len(last3),
            "days_in": sum(1 for r in rows if r["main_net_wan"] > 0),
            "days_out": sum(1 for r in rows if r["main_net_wan"] <= 0)}

def fetch_flow(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("flow", code, ttl=3600)
    if cached:
        return cached
    try:
        import akshare as ak
        market = code_to_market(code)
        df = ak.stock_individual_fund_flow(stock=code, market=market).tail(10)
        rows = []
        for _, r in df.iterrows():
            try:
                rows.append({"date": str(r["日期"]),
                             "main_net_wan": round(float(r["主力净流入-净额"]) / 1e4, 1),
                             "main_net_pct": float(r["主力净流入-净占比"])})
            except (ValueError, TypeError):
                continue
        if rows:
            out = ok_result("akshare", {"rows": rows, "summary": summarize_flow(rows)})
            _cache.set("flow", code, out)
            return out
    except Exception:
        pass
    try:
        j = http_get_json("https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get", params={
            "lmt": "10", "klt": "101", "secid": code_to_secid(code),
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"})
        klines = ((j or {}).get("data") or {}).get("klines")
        if klines:
            rows = parse_em_fflow(klines)
            if rows:
                out = ok_result("eastmoney", {"rows": rows, "summary": summarize_flow(rows)})
                _cache.set("flow", code, out)
                return out
    except Exception:
        pass
    return missing_result(f"联网搜索「{code} 主力资金流向 近日」并标注来源")
