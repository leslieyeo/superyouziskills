import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
import pytest
from szdata.sources import (
    ok_result, missing_result, code_to_secid, code_to_tencent,
    validate_a_share_code,
)

def test_ok_result_shape():
    r = ok_result("eastmoney", {"a": 1})
    assert r["ok"] is True and r["source"] == "eastmoney" and r["data"] == {"a": 1}
    assert "fetched_at" in r

def test_missing_result():
    r = missing_result("搜索 600519 今日行情")
    assert r["ok"] is False and r["source"] == "missing" and r["data"] is None
    assert r["hint"] == "搜索 600519 今日行情"

def test_code_mapping():
    assert code_to_secid("600519") == "1.600519"
    assert code_to_secid("000001") == "0.000001"
    assert code_to_secid("300750") == "0.300750"
    assert code_to_secid("688041") == "1.688041"
    assert code_to_secid("920002") == "0.920002"
    assert code_to_tencent("600519") == "sh600519"
    assert code_to_tencent("002217") == "sz002217"
    assert code_to_tencent("920002") == "bj920002"

def test_code_validation_rejects_invalid_or_unsupported_codes():
    for code in ("not-a-code", "../600519", "123", "200001", "900901"):
        with pytest.raises(ValueError):
            validate_a_share_code(code)
