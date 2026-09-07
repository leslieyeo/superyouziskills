import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.flow import summarize_flow

ROWS = [{"date": "2026-06-10", "main_net_wan": -3200.0, "main_net_pct": -4.1},
        {"date": "2026-06-11", "main_net_wan": 8500.0, "main_net_pct": 6.2}]

def test_summarize_flow():
    s = summarize_flow(ROWS)
    assert s["last_main_net_wan"] == 8500.0
    assert s["net_3d_wan"] == 5300.0
    assert s["days_in"] == 1 and s["days_out"] == 1

def test_summarize_empty():
    assert summarize_flow([]) == {}
