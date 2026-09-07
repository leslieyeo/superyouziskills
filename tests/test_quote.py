import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.quote import parse_tencent

FIXTURE = 'v_sh600519="1~贵州茅台~600519~1431.00~1420.00~1425.00~28560~14000~14560~' + "~".join([""]*21) + '~20260611150003~11.00~0.77~1448.00~1418.00~1431.00/28560/4080000000~28560~408000~0.23~22.50~~1448.00~1418.00~2.11~17973.50~17973.50~8.90~1562.00~1278.00~";'

def test_parse_tencent():
    d = parse_tencent(FIXTURE)
    assert d["name"] == "贵州茅台"
    assert d["price"] == 1431.0
    assert d["prev_close"] == 1420.0
    assert d["open"] == 1425.0
    assert d["change_pct"] == 0.77
    assert d["high"] == 1448.0
    assert d["low"] == 1418.0
    assert d["turnover_pct"] == 0.23
    assert d["pe_ttm"] == 22.5
    assert d["mcap_yi"] == 17973.5

def test_parse_tencent_garbage_returns_none():
    assert parse_tencent("") is None
    assert parse_tencent('v_pv_none="1";') is None
