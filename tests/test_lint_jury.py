import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lint_frameworks import check_jury_text

GOOD_JURY = (
    "# 巴菲特 · A · 护城河\n"
    "## 投资哲学\nx\n"
    "## 关键指标（对应数据字段）\nx\n"
    "## 排雷线（什么情况直接低分）\nx\n"
    "## 打分 rubric（0-100：维度与权重，合计 100）\n"
    "- ROE 持续性（40 分）：高则好\n"
    "- 自由现金流（35 分）：充裕则好\n"
    "- 估值安全边际（25 分）：低则好\n"
    "## 口吻\nx\n"
    "> 本档案为公开资料的学习性蒸馏，不代表本人观点，不构成任何投资建议。\n"
)


def test_good_passes():
    assert check_jury_text(GOOD_JURY) == []


def test_missing_section_fails():
    text = GOOD_JURY.replace("## 排雷线（什么情况直接低分）\nx\n", "")
    errs = check_jury_text(text)
    assert any("排雷线" in e for e in errs)


def test_rubric_weights_not_100_fails():
    # Replace rubric lines so weights sum to 99
    text = GOOD_JURY.replace(
        "- ROE 持续性（40 分）：高则好\n"
        "- 自由现金流（35 分）：充裕则好\n"
        "- 估值安全边际（25 分）：低则好\n",
        "- ROE 持续性（40 分）：高则好\n"
        "- 自由现金流（35 分）：充裕则好\n"
        "- 估值安全边际（24 分）：低则好\n",
    )
    errs = check_jury_text(text)
    assert any("rubric 权重和=99" in e for e in errs)


def test_missing_disclaimer_fails():
    text = GOOD_JURY.replace(
        "> 本档案为公开资料的学习性蒸馏，不代表本人观点，不构成任何投资建议。\n", ""
    )
    errs = check_jury_text(text)
    assert any("免责" in e for e in errs)
