import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.sector import parse_em_boards
from szdata.flow import parse_em_fflow

def test_parse_em_boards():
    j = {"data": {"diff": [{"f14": "半导体", "f3": 4.39}, {"f14": "PCB", "f3": "-"}]}}
    assert parse_em_boards(j) == [{"board": "半导体", "pct": 4.39}]

def test_parse_em_boards_null():
    assert parse_em_boards(None) == []
    assert parse_em_boards({"data": None}) == []

def test_parse_em_fflow():
    rows = parse_em_fflow(["2026-06-11,85000000,1,2,3,4,6.2", "bad"])
    assert rows == [{"date": "2026-06-11", "main_net_wan": 8500.0, "main_net_pct": 6.2}]
