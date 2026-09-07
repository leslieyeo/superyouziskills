"""行情快照。A 源 akshare（全市场表过滤）→ B 源腾讯 qt.gtimg.cn 单票直连。"""
from __future__ import annotations
from typing import Optional
from .sources import (
    http_get, ok_result, missing_result, code_to_tencent,
    validate_a_share_code,
)
from .cache import Cache

_cache = Cache()

def _f(v: str) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def parse_tencent(text: str) -> Optional[dict]:
    """腾讯行情文本按 ~ 分隔，索引为 0-based（fields[0] 是 'v_shXXXXXX="1' 前缀）：
    1 名称 2 代码 3 现价 4 昨收 5 今开 31 涨跌 32 涨跌% 33 最高
    34 最低 38 换手% 39 PE 45 总市值(亿) 46 PB 47 涨停价 48 跌停价"""
    if not text or "~" not in text:
        return None
    fields = text.split("~")
    if len(fields) < 49:
        return None
    return {
        "name": fields[1], "code": fields[2],
        "price": _f(fields[3]), "prev_close": _f(fields[4]), "open": _f(fields[5]),
        "change": _f(fields[31]), "change_pct": _f(fields[32]),
        "high": _f(fields[33]), "low": _f(fields[34]),
        "turnover_pct": _f(fields[38]), "pe_ttm": _f(fields[39]),
        "mcap_yi": _f(fields[45]), "pb": _f(fields[46]),
        "limit_up": _f(fields[47]), "limit_down": _f(fields[48]),
    }

def fetch_quote(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("quote", code, ttl=60)
    if cached:
        return cached
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        row = df[df["代码"] == code]
        if len(row):
            r = row.iloc[0]
            data = {"name": str(r["名称"]), "code": code,
                    "price": _f(r["最新价"]), "change_pct": _f(r["涨跌幅"]),
                    "turnover_pct": _f(r["换手率"]), "pe_ttm": _f(r["市盈率-动态"]),
                    "mcap_yi": round(_f(r["总市值"]) / 1e8, 2) if _f(r["总市值"]) else None,
                    "pb": _f(r["市净率"]),
                    "high": _f(r["最高"]), "low": _f(r["最低"]),
                    "open": _f(r["今开"]), "prev_close": _f(r["昨收"])}
            if data["price"] is None:
                raise ValueError("no price")
            out = ok_result("akshare", data)
            _cache.set("quote", code, out)
            return out
    except Exception:
        pass
    text = http_get(f"https://qt.gtimg.cn/q={code_to_tencent(code)}", encoding="gbk")
    parsed = parse_tencent(text or "")
    if parsed:
        out = ok_result("tencent", parsed)
        _cache.set("quote", code, out)
        return out
    return missing_result(f"联网搜索「{code} 今日股价 涨跌幅 换手率」并标注来源")
