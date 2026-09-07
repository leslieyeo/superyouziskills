#!/usr/bin/env python3
"""superyouzi 数据入口。用法：
  python3 fetch.py quote|kline|lhb|flow|sentiment|fund 600519
  python3 fetch.py finhist|val|holders 600519
  python3 fetch.py panel            # 全市场情绪面板（不带代码）
  python3 fetch.py all 600519       # 聚合个股全维度
输出：统一协议 JSON（ok/source/data/fetched_at/hint），永不抛异常。
注意：all 为串行聚合，弱网环境最坏可达约 1 分钟。
dcf 不走本脚本，请直接调用 szdata.dcf.run_dcf（需显式假设）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def _is_partial_result(value: dict) -> bool:
    data = value.get("data") if isinstance(value, dict) else None
    return bool(value.get("partial") or (isinstance(data, dict) and data.get("partial")))

def _fill_hint(kind: str, value: dict) -> str:
    data = value.get("data") if isinstance(value, dict) else None
    hint = value.get("hint") or (data.get("note") if isinstance(data, dict) else "")
    return f"{kind}: {hint or '请检查该维度缺失字段并联网补充'}"

def main() -> int:
    args = sys.argv[1:]
    kinds_with_code = {"quote", "kline", "lhb", "flow", "sentiment", "fund",
                       "finhist", "val", "holders", "all"}

    # dcf 特殊处理：不提供 CLI，直接报错 exit 2
    if args and args[0] == "dcf":
        print("dcf 由分析端调用 szdata.dcf.run_dcf（需显式假设），不提供 CLI",
              file=sys.stderr)
        return 2

    if not args or (args[0] in kinds_with_code and len(args) < 2) or \
       (args[0] not in kinds_with_code and args[0] != "panel"):
        print("用法: fetch.py quote|kline|lhb|flow|sentiment|fund|finhist|val|holders|all"
              " <6位代码> | fetch.py panel",
              file=sys.stderr)
        return 2
    kind = args[0]
    try:
        if kind == "panel":
            from szdata.sector import fetch_market_panel
            out = fetch_market_panel()
        else:
            from szdata.sources import validate_a_share_code
            try:
                code = validate_a_share_code(args[1])
            except ValueError as e:
                print(f"无效股票代码: {e}", file=sys.stderr)
                return 2
            from szdata.quote import fetch_quote
            from szdata.kline import fetch_kline
            from szdata.lhb import fetch_lhb
            from szdata.flow import fetch_flow
            from szdata.sentiment import fetch_sentiment
            from szdata.fundamentals import fetch_fundamentals
            from szdata.finhist import fetch_finhist
            from szdata.valuation import fetch_valuation
            from szdata.holders import fetch_holders
            table = {"quote": fetch_quote, "kline": fetch_kline, "lhb": fetch_lhb,
                     "flow": fetch_flow, "sentiment": fetch_sentiment,
                     "fund": fetch_fundamentals, "finhist": fetch_finhist,
                     "val": fetch_valuation, "holders": fetch_holders}
            if kind == "all":
                import datetime as _dt
                data = {k: f(code) for k, f in table.items()}
                failed = [k for k, value in data.items() if not value.get("ok")]
                partial = [k for k, value in data.items()
                           if value.get("ok") and _is_partial_result(value)]
                succeeded = len(data) - len(failed)
                hint_parts = []
                if failed:
                    hint_parts.append("缺失维度: " + ", ".join(
                        _fill_hint(k, data[k]) for k in failed))
                if partial:
                    hint_parts.append("部分维度需补充: " + ", ".join(
                        _fill_hint(k, data[k]) for k in partial))
                out = {"ok": succeeded > 0, "source": "aggregate",
                       "data": data,
                       "fetched_at": _dt.datetime.now().isoformat(timespec="seconds"),
                       "hint": "；".join(hint_parts)}
                if failed or partial:
                    out["partial"] = True
            else:
                out = table[kind](code)
    except Exception as e:  # 兜底：任何意外都输出 missing 协议而不是堆栈
        out = {"ok": False, "source": "missing", "data": None,
               "fetched_at": "", "hint": f"脚本异常({type(e).__name__})，请联网搜索补数"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
