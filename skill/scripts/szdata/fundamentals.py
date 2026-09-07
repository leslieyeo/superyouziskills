"""基础面快照：名称/行业/市值/上市时间 + 最近一期营收净利。短线够用即可。"""
from __future__ import annotations
from .sources import ok_result, missing_result, validate_a_share_code
from .cache import Cache

_cache = Cache()

def pick_info(kv: dict) -> dict:
    def _yi(v):
        try:
            return round(float(v) / 1e8, 1)
        except (TypeError, ValueError):
            return None
    return {"name": str(kv.get("股票简称", "")), "industry": str(kv.get("行业", "")),
            "mcap_yi": _yi(kv.get("总市值")),
            "float_mcap_yi": _yi(kv.get("流通市值")),
            "list_date": str(kv.get("上市时间", ""))}

def fetch_fundamentals(code: str) -> dict:
    code = validate_a_share_code(code)
    cached = _cache.get("fund", code, ttl=86400)
    if cached:
        return cached
    try:
        import akshare as ak
        info = ak.stock_individual_info_em(symbol=code)
        kv = dict(zip(info["item"], info["value"]))
        data = pick_info(kv)
        try:
            ab = ak.stock_financial_abstract(symbol=code)
            rev = ab[ab["指标"] == "营业总收入"].iloc[0]
            data["latest_revenue"] = {str(k): str(v) for k, v in list(rev.items())[-2:]}
        except Exception:
            data["latest_revenue"] = None
        out = ok_result("akshare", data)
        _cache.set("fund", code, out)
        return out
    except Exception:
        pass
    try:
        from .quote import fetch_quote
        q = fetch_quote(code)
        if q.get("ok") and q.get("data"):
            d = q["data"]
            if not d.get("name") or d.get("mcap_yi") is None:
                pass  # 兜底数据关键字段仍空，不发 ok_result，落到 missing_result
            else:
                data = {"name": d.get("name", ""), "industry": None,
                        "mcap_yi": d.get("mcap_yi"), "float_mcap_yi": None,
                        "list_date": None, "latest_revenue": None,
                        "note": "行业/流通市值/财务摘要缺失，请联网搜索补充"}
                out = ok_result("tencent-quote", data)
                out["partial"] = True
                out["hint"] = data["note"]
                _cache.set("fund", code, out)
                return out
    except Exception:
        pass
    return missing_result(f"联网搜索「{code} 市值 行业 最新财报 营收」并标注来源")
