"""HTTP 封装 + 统一结果协议 + 代码映射。"""
from __future__ import annotations
import datetime
import re
from typing import Any, Optional
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
TIMEOUT = 8

def http_get(url: str, params: Optional[dict] = None, encoding: Optional[str] = None) -> Optional[str]:
    try:
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        if encoding:
            r.encoding = encoding
        return r.text
    except requests.RequestException:
        return None

def http_get_json(url: str, params: Optional[dict] = None) -> Optional[Any]:
    try:
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        return r.json() if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None

def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def ok_result(source: str, data: Any) -> dict:
    return {"ok": True, "source": source, "data": data, "fetched_at": _now(), "hint": ""}

def missing_result(hint: str) -> dict:
    return {"ok": False, "source": "missing", "data": None, "fetched_at": _now(), "hint": hint}

_A_SHARE_RE = re.compile(r"^\d{6}$")
_SH_PREFIXES = ("60", "68")
_SZ_PREFIXES = ("00", "30")
_BJ_PREFIXES = ("43", "83", "87", "88", "92")

def validate_a_share_code(code: str) -> str:
    """校验并返回六位 A 股代码，覆盖沪深与北交所。"""
    code = str(code).strip()
    if not _A_SHARE_RE.fullmatch(code):
        raise ValueError("股票代码必须是 6 位数字")
    if not code.startswith(_SH_PREFIXES + _SZ_PREFIXES + _BJ_PREFIXES):
        raise ValueError("仅支持沪深北 A 股代码")
    return code

def code_to_market(code: str) -> str:
    code = validate_a_share_code(code)
    if code.startswith(_SH_PREFIXES):
        return "sh"
    if code.startswith(_BJ_PREFIXES):
        return "bj"
    return "sz"

def code_to_secid(code: str) -> str:
    """东财 secid：沪市=1，深市/北交所=0。"""
    code = validate_a_share_code(code)
    return ("1." if code.startswith(_SH_PREFIXES) else "0.") + code

def code_to_tencent(code: str) -> str:
    code = validate_a_share_code(code)
    return code_to_market(code) + code
