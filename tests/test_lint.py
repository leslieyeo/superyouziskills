import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lint_frameworks import check_text

GOOD = ("# 测试 · 定位\n## 适用场景\nx\n## 核心信条\nx\n## 判断链\nx\n"
        "## 关键信号（对应数据字段）\nx\n## 操作纪律\nx\n## 失效与纠错信号\nx\n"
        "## 一句话口令\nx\n> 本框架为历史方法论蒸馏，不构成任何投资建议。\n")

def test_good_passes():
    assert check_text(GOOD) == []

def test_missing_section_fails():
    errs = check_text(GOOD.replace("## 操作纪律\nx\n", ""))
    assert any("操作纪律" in e for e in errs)

def test_missing_disclaimer_fails():
    errs = check_text(GOOD.replace("> 本框架为历史方法论蒸馏，不构成任何投资建议。\n", ""))
    assert any("免责" in e for e in errs)

def test_banned_words_fail():
    errs = check_text(GOOD + "\n基本面良好\n")
    assert any("套话" in e for e in errs)
