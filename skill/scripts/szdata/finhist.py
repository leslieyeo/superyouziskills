"""财务历史：近 5 年 ROE / 营收增速 / 净利增速 / 资产负债率。
A 源 akshare stock_financial_analysis_indicator。"""
from __future__ import annotations
from .sources import ok_result, missing_result, validate_a_share_code
from .cache import Cache

_cache = Cache()


def _to_float(v) -> float | None:
    """把字符串转 float；"-"、空串、None → None。"""
    if v is None:
        return None
    s = str(v).strip()
    if s in ("-", "", "nan", "None"):
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def pick_years(rows: list) -> dict:
    """纯函数：从 rows 提取财务历史摘要。

    rows 元素格式::
        {"year": "2024", "roe": "15.3", "revenue_yoy": "8.2",
         "profit_yoy": "-3.1", "debt_ratio": "45.0"}

    字段值可为 "-" 或空字符串（跳过该值，不计入序列）。
    输出 keys: roe_5y, roe_5y_avg, revenue_yoy, profit_yoy, debt_ratio, years。
    """
    if not rows:
        return {"roe_5y": [], "roe_5y_avg": None,
                "revenue_yoy": None, "profit_yoy": None,
                "debt_ratio": None, "years": []}

    # rows 按年份升序排列（调用方保证）；增速/负债率取「最近一个有值的年份」，缺值年份自动回退
    roe_5y: list[float] = []
    years: list[str] = []
    latest_rev = latest_prof = latest_debt = None

    for row in rows:
        roe_val = _to_float(row.get("roe"))
        if roe_val is not None:
            roe_5y.append(roe_val)
            years.append(str(row.get("year", "")))
        rev = _to_float(row.get("revenue_yoy"))
        if rev is not None:
            latest_rev = rev
        prof = _to_float(row.get("profit_yoy"))
        if prof is not None:
            latest_prof = prof
        debt = _to_float(row.get("debt_ratio"))
        if debt is not None:
            latest_debt = debt

    roe_5y = roe_5y[-5:]          # 严格只保留最近 5 年，防止 start_year 漂移成 6 年序列
    years = years[-5:]
    roe_avg = round(sum(roe_5y) / len(roe_5y), 1) if roe_5y else None

    return {"roe_5y": roe_5y, "roe_5y_avg": roe_avg,
            "revenue_yoy": latest_rev, "profit_yoy": latest_prof,
            "debt_ratio": latest_debt, "years": years}


def _only_annual(dates_rows: list[dict]) -> list[dict]:
    """过滤掉非年报行（日期字段不以 '12-31' 结尾的行）。

    Args:
        dates_rows: 每个元素须含 "date" 字段（YYYY-MM-DD 格式字符串）。
    Returns:
        仅保留年报行（12-31 结尾）的列表，顺序不变。
    """
    return [r for r in dates_rows if str(r.get("date", "")).endswith("12-31")]


def fetch_finhist(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("finhist", code, ttl=86400)
    if cached:
        return cached
    try:
        import akshare as ak
        import datetime as _dt
        _start = str(_dt.date.today().year - 5)
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year=_start)
        # 列名映射（akshare 版本间可能略有差异，防御式取列）
        col_date = "日期"
        col_roe = next((c for c in df.columns if "加权净资产收益率" in c), None)
        col_rev = next((c for c in df.columns if "主营业务收入增长率" in c
                        or "营业总收入同比增长率" in c or "营收" in c), None)
        col_prof = next((c for c in df.columns if "净利润增长率" in c
                         or "归母净利" in c), None)
        col_debt = next((c for c in df.columns if "资产负债率" in c), None)

        if col_date not in df.columns:
            raise ValueError("缺少日期列")

        # 只保留年报行（12-31 结尾），过滤中报/季报
        df[col_date] = df[col_date].astype(str)
        df = df[df[col_date].str.endswith("12-31")]

        df["_year"] = df[col_date].str[:4]
        rows = []
        for year, grp in df.groupby("_year"):
            latest = grp.loc[grp[col_date].idxmax()]
            rows.append({
                "year": year,
                "roe": str(latest[col_roe]) if col_roe else "-",
                "revenue_yoy": str(latest[col_rev]) if col_rev else "-",
                "profit_yoy": str(latest[col_prof]) if col_prof else "-",
                "debt_ratio": str(latest[col_debt]) if col_debt else "-",
            })
        rows.sort(key=lambda r: r["year"])
        data = pick_years(rows)
        out = ok_result("akshare", data)
        _cache.set("finhist", code, out)
        return out
    except Exception:
        pass
    return missing_result(
        f"联网搜索「{code} 近5年 ROE 营收增速 净利增速 资产负债率」并标注来源")
