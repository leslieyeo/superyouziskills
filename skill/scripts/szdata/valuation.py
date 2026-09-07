"""估值分位：PE/PB 近 5 年百分位。
A 源 akshare stock_zh_valuation_baidu。"""
from __future__ import annotations
from .sources import ok_result, missing_result, validate_a_share_code
from .cache import Cache

_cache = Cache()


def percentile(series: list, current: float | None) -> float | None:
    """计算 current 在 series 中的百分位（≤ current 的比例）。

    空序列或 current 为 None 返回 None；结果 round 1 位小数。
    """
    if not series or current is None:
        return None
    count = sum(1 for v in series if v <= current)
    return round(count / len(series) * 100, 1)

def extract_values(df) -> list[float]:
    """从 AkShare 估值表提取有效数值，并按原日期顺序保留。"""
    if df is None or "value" not in df.columns:
        return []
    values = []
    for value in df["value"]:
        try:
            number = float(value)
            if number > 0:
                values.append(number)
        except (TypeError, ValueError):
            continue
    return values

def fetch_valuation(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("val", code, ttl=86400)
    if cached:
        return cached
    try:
        import akshare as ak
        fetch_fn = getattr(ak, "stock_zh_valuation_baidu", None)
        if fetch_fn is None:
            raise AttributeError("stock_zh_valuation_baidu not found")
        pe_df = fetch_fn(symbol=code, indicator="市盈率(TTM)", period="近五年")
        pb_df = fetch_fn(symbol=code, indicator="市净率", period="近五年")
        pe_series = extract_values(pe_df)
        pb_series = extract_values(pb_df)
        if not pe_series or not pb_series:
            raise ValueError("缺少 pe/pb 历史数据")

        pe_cur = pe_series[-1] if pe_series else None
        pb_cur = pb_series[-1] if pb_series else None

        data = {
            "pe": pe_cur,
            "pb": pb_cur,
            "pe_percentile_5y": percentile(pe_series, pe_cur),
            "pb_percentile_5y": percentile(pb_series, pb_cur),
            "sample_count": {"pe": len(pe_series), "pb": len(pb_series)},
        }
        out = ok_result("akshare-baidu", data)
        _cache.set("val", code, out)
        return out
    except Exception:
        pass
    return missing_result(
        f"联网搜索「{code} 市盈率 历史分位」并标注来源")
