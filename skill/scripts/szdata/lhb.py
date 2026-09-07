"""个股龙虎榜近 N 条。东财 datacenter API 为 A 源（akshare 底层同源），失败标 missing。"""
from __future__ import annotations
from .sources import (
    http_get_json, ok_result, missing_result, validate_a_share_code,
)
from .cache import Cache

_cache = Cache()
_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0

def normalize_rows(raw: list) -> list:
    rows = []
    for r in raw:
        rows.append({"date": str(r.get("TRADE_DATE", ""))[:10],
                     "reason": r.get("EXPLANATION", ""),
                     "buy_wan": round(_num(r.get("BILLBOARD_BUY_AMT")) / 1e4, 1),
                     "sell_wan": round(_num(r.get("BILLBOARD_SELL_AMT")) / 1e4, 1),
                     "net_buy_wan": round(_num(r.get("BILLBOARD_NET_AMT")) / 1e4, 1),
                     "turnover_pct": _num(r.get("TURNOVERRATE"))})
    return rows

def fetch_lhb(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("lhb", code, ttl=3600)
    if cached:
        return cached
    try:
        j = http_get_json(_URL, params={
            "reportName": "RPT_DAILYBILLBOARD_DETAILS", "columns": "ALL",
            "filter": f'(SECURITY_CODE="{code}")', "sortColumns": "TRADE_DATE",
            "sortTypes": "-1", "pageSize": "10", "pageNumber": "1"})
        success = isinstance(j, dict) and j.get("success") is True
        rows = ((j or {}).get("result") or {}).get("data")
        if rows:
            out = ok_result("eastmoney", normalize_rows(rows))
            _cache.set("lhb", code, out)
            return out
        if success:   # 接口明确成功但无记录 = 近期没上过榜
            out = ok_result("eastmoney", [])
            _cache.set("lhb", code, out)
            return out
    except Exception:
        pass
    return missing_result(f"联网搜索「{code} 龙虎榜 最近」并标注来源")
