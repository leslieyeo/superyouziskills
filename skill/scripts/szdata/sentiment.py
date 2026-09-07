"""个股人气：东财人气榜排名。A 源 akshare stock_hot_rank_em。"""
from __future__ import annotations
from typing import Optional
from .sources import ok_result, missing_result, validate_a_share_code
from .cache import Cache

_cache = Cache()

def grade_rank(rank: Optional[int]) -> str:
    if rank is None:
        return "未知"
    if rank <= 20:
        return "极热"
    if rank <= 100:
        return "热"
    if rank <= 1000:
        return "温"
    return "冷"

def fetch_sentiment(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("sentiment", code, ttl=1800)
    if cached:
        return cached
    try:
        import akshare as ak
        df = ak.stock_hot_rank_em()
        codes = df["代码"].astype(str).str.extract(
            r"(?<!\d)(\d{6})(?!\d)", expand=False
        )
        row = df[codes == code]
        rank = int(row.iloc[0]["当前排名"]) if len(row) else None
        data = {"rank": rank, "grade": grade_rank(rank),
                "note": "未进人气榜前100" if rank is None else f"人气榜第{rank}名"}
        out = ok_result("akshare", data)
        _cache.set("sentiment", code, out)
        return out
    except Exception:
        pass
    return missing_result(f"联网搜索「{code} 股吧 讨论热度」并概括，标注来源")
