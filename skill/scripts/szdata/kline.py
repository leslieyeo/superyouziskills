"""日 K。A 源 akshare stock_zh_a_hist → B 源东财 push2his kline API。"""
from __future__ import annotations
from typing import Optional
from .sources import (
    http_get_json, ok_result, missing_result, code_to_secid,
    validate_a_share_code,
)
from .cache import Cache

_cache = Cache()

def parse_em_klines(klines: list) -> list:
    rows = []
    for line in klines:
        p = line.split(",")
        if len(p) < 11:
            continue
        try:
            rows.append({"date": p[0], "open": float(p[1]), "close": float(p[2]),
                         "high": float(p[3]), "low": float(p[4]),
                         "vol": int(float(p[5])), "turnover_pct": float(p[10])})
        except (ValueError, TypeError):
            continue
    return rows

def summarize(rows: list) -> dict:
    if not rows:
        return {"n": 0}
    closes = [r["close"] for r in rows]
    return {"n": len(rows), "last_date": rows[-1]["date"], "last_close": closes[-1],
            "pct_3d": round((closes[-1] / closes[-4] - 1) * 100, 2) if len(rows) >= 4 else None,
            "max_high": max(r["high"] for r in rows),
            "min_low": min(r["low"] for r in rows),
            "avg_turnover_pct": round(sum(r["turnover_pct"] for r in rows) / len(rows), 2)}

def fetch_kline(code: str, days: int = 30) -> dict:
    code = validate_a_share_code(code)
    key = f"{code}_{days}"
    cached = _cache.get("kline", key, ttl=3600)
    if cached:
        return cached
    try:
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq").tail(days)
        rows = []
        for _, r in df.iterrows():
            try:
                rows.append({"date": str(r["日期"]), "open": float(r["开盘"]), "close": float(r["收盘"]),
                             "high": float(r["最高"]), "low": float(r["最低"]),
                             "vol": int(r["成交量"]), "turnover_pct": float(r["换手率"])})
            except (ValueError, TypeError):
                continue
        if rows:
            out = ok_result("akshare", {"rows": rows, "summary": summarize(rows)})
            _cache.set("kline", key, out)
            return out
    except Exception:
        pass
    try:
        j = http_get_json("https://push2his.eastmoney.com/api/qt/stock/kline/get", params={
            "secid": code_to_secid(code), "klt": "101", "fqt": "1",
            "fields1": "f1,f2,f3",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "end": "20500101", "lmt": str(days)})
        klines = ((j or {}).get("data") or {}).get("klines")
        if klines:
            rows = parse_em_klines(klines)
            if rows:
                out = ok_result("eastmoney", {"rows": rows, "summary": summarize(rows)})
                _cache.set("kline", key, out)
                return out
    except Exception:
        pass
    return missing_result(f"联网搜索「{code} 最近{days}日 K线 走势」并标注来源")
