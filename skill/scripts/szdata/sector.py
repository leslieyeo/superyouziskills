"""市场情绪面板：今日涨停池统计 + 板块涨幅前 10。A 源 akshare（东财数据）。"""
from __future__ import annotations
import datetime
from .sources import ok_result, missing_result, http_get_json
from .cache import Cache

_cache = Cache()

def parse_em_boards(j) -> list:
    rows = (((j or {}).get("data") or {}).get("diff")) or []
    if isinstance(rows, dict):
        rows = list(rows.values())
    out = []
    for r in rows:
        try:
            out.append({"board": str(r["f14"]), "pct": float(r["f3"])})
        except (KeyError, ValueError, TypeError):
            continue
    return out

def summarize_zt(pool: list) -> dict:
    if not pool:
        return {"zt_count": 0, "max_lianban": 0, "lianban_ge2": 0}
    lbs = []
    for p in pool:
        try:
            lbs.append(int(p.get("lbc") or 1))
        except (ValueError, TypeError):
            lbs.append(1)
    return {"zt_count": len(pool), "max_lianban": max(lbs),
            "lianban_ge2": sum(1 for x in lbs if x >= 2)}

def fetch_market_panel() -> dict:
    today = datetime.date.today().strftime("%Y%m%d")
    cached = _cache.get("panel", today, ttl=600)
    if cached:
        return cached
    pool, top_boards = [], []
    pool_ok = boards_ok = False
    try:
        import akshare as ak
        try:
            zt = ak.stock_zt_pool_em(date=today)
            for _, r in zt.iterrows():
                try:
                    pool.append({"name": str(r["名称"]), "code": str(r["代码"]),
                                 "lbc": int(r["连板数"]), "industry": str(r.get("所属行业", ""))})
                except (ValueError, TypeError, KeyError):
                    continue
            pool_ok = True
        except Exception:
            pass
        try:
            boards = ak.stock_board_industry_name_em().sort_values(
                "涨跌幅", ascending=False).head(10)
            for _, r in boards.iterrows():
                try:
                    top_boards.append({"board": str(r["板块名称"]), "pct": float(r["涨跌幅"])})
                except (ValueError, TypeError, KeyError):
                    continue
            boards_ok = bool(top_boards)
        except Exception:
            pass
    except Exception:
        pass
    if not boards_ok:
        try:
            j = http_get_json("https://push2.eastmoney.com/api/qt/clist/get", params={
                "pn": "1", "pz": "10", "po": "1", "np": "1", "fltt": "2", "invt": "2",
                "fid": "f3", "fs": "m:90 t:2", "fields": "f3,f14"})
            eb = parse_em_boards(j)
            if eb:
                top_boards = eb
                boards_ok = True
        except Exception:
            pass
    if not pool_ok and not boards_ok:
        return missing_result("联网搜索「今日 A股 涨停家数 连板 最强板块」并标注来源")
    missing = []
    if not pool_ok:
        missing.append("涨停池")
    if not boards_ok:
        missing.append("板块涨幅榜")
    data = {"as_of": today,
            "note": "数据为最近交易日口径；盘前/休市时早于该日期" if pool_ok else "涨停池获取失败",
            "zt_summary": summarize_zt(pool) if pool_ok else None,
            "zt_pool_top": sorted(pool, key=lambda p: -p["lbc"])[:15],
            "top_boards": top_boards,
            "partial": bool(missing)}
    out = ok_result("akshare", data)
    if missing:
        out["partial"] = True
        out["hint"] = "缺失字段: " + ", ".join(missing) + "；联网搜索「今日 A股 涨停家数 连板 最强板块」补齐"
    _cache.set("panel", today, out)
    return out
