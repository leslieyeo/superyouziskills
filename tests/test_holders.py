"""离线测试 holders.summarize_holders — 纯函数，无网络。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))

from szdata.holders import summarize_holders


def test_summarize_holders_normal():
    out = summarize_holders([5.1, 4.2])
    assert out["top10_ratio"] == 9.3
    assert out["n"] == 2


def test_summarize_holders_empty():
    out = summarize_holders([])
    assert out["top10_ratio"] is None
    assert out["n"] == 0


def test_summarize_holders_ten():
    ratios = [5.0, 4.0, 3.5, 3.0, 2.5, 2.0, 1.8, 1.6, 1.4, 1.2]
    out = summarize_holders(ratios)
    assert out["top10_ratio"] == round(sum(ratios), 2)
    assert out["n"] == 10
