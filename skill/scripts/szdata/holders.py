"""股东结构：前十大流通股东占比。
A 源 akshare stock_gdfx_top_10_em（东财十大流通股东）。"""
from __future__ import annotations
from .sources import ok_result, missing_result, code_to_market, validate_a_share_code
from .cache import Cache

_cache = Cache()


def summarize_holders(top10_ratios: list) -> dict:
    """纯函数：汇总前十大股东占比列表。

    空列表 → top10_ratio=None, n=0。
    """
    if not top10_ratios:
        return {"top10_ratio": None, "n": 0}
    total = round(sum(top10_ratios), 2)
    return {"top10_ratio": total, "n": len(top10_ratios)}


def fetch_holders(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("holders", code, ttl=86400)
    if cached:
        return cached
    try:
        import akshare as ak
        market = code_to_market(code)
        symbol = market + code
        # 东财十大流通股东
        fetch_fn = getattr(ak, "stock_gdfx_top_10_em", None)
        if fetch_fn is None:
            raise AttributeError("stock_gdfx_top_10_em not found")
        df = fetch_fn(symbol=symbol)
        # 防御式取持股比例列
        ratio_col = next(
            (c for c in df.columns if "持股比例" in c or "占总股本" in c), None
        )
        if ratio_col is None:
            raise ValueError("缺少持股比例列")
        ratios = []
        for v in df[ratio_col]:
            try:
                ratios.append(float(str(v).replace("%", "").strip()))
            except (ValueError, TypeError):
                continue
        summary = summarize_holders(ratios)
        data = {
            "top10_ratio": summary["top10_ratio"],
            "n": summary["n"],
            "fund_count": None,
            "note": "机构家数请联网搜索补充",
        }
        out = ok_result("akshare", data)
        _cache.set("holders", code, out)
        return out
    except Exception:
        pass
    return missing_result(
        f"联网搜索「{code} 前十大股东 机构持仓」并标注来源")
