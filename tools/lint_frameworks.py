#!/usr/bin/env python3
"""框架文件 schema 校验。用法: python3 tools/lint_frameworks.py [目录]
jury 模式: python3 tools/lint_frameworks.py --jury skill/jury"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REQUIRED = ["## 适用场景", "## 核心信条", "## 判断链",
            "## 关键信号（对应数据字段）", "## 操作纪律",
            "## 失效与纠错信号", "## 一句话口令"]
DISCLAIMER = "> 本框架为历史方法论蒸馏，不构成任何投资建议。"
BANNED = ["基本面良好", "前景广阔", "值得关注"]

REQUIRED_JURY = [
    "## 投资哲学",
    "## 关键指标（对应数据字段）",
    "## 排雷线（什么情况直接低分）",
    "## 打分 rubric（0-100：维度与权重，合计 100）",
    "## 口吻",
]
DISCLAIMER_JURY = "> 本档案为公开资料的学习性蒸馏，不代表本人观点，不构成任何投资建议。"

def check_text(text: str) -> list:
    errs = []
    for h in REQUIRED:
        if h not in text:
            errs.append(f"缺少章节: {h}")
    if DISCLAIMER not in text:
        errs.append("缺少免责行")
    for w in BANNED:
        if w in text:
            errs.append(f"出现禁用套话: {w}")
    return errs

def check_jury_text(text: str) -> list:
    errs = []
    for h in REQUIRED_JURY:
        if h not in text:
            errs.append(f"缺少章节: {h}")
    if DISCLAIMER_JURY not in text:
        errs.append("缺少免责行")
    for w in BANNED:
        if w in text:
            errs.append(f"出现禁用套话: {w}")
    # rubric weight check: only when rubric section exists
    rubric_header = "## 打分 rubric（0-100：维度与权重，合计 100）"
    if rubric_header in text:
        rubric_start = text.index(rubric_header) + len(rubric_header)
        # find next ## heading or end of text
        next_section = re.search(r"\n## ", text[rubric_start:])
        rubric_body = text[rubric_start: rubric_start + next_section.start()] if next_section else text[rubric_start:]
        # parse numbers in （XX 分）or (XX 分) brackets, or leading XX% on a line
        nums = [int(m) for m in re.findall(r"[（(](\d+)\s*分[）)]", rubric_body)]
        nums += [int(m) for m in re.findall(r"^\s*-[^(（\n]*?(\d+)\s*%", rubric_body, re.MULTILINE)]
        if nums:
            total = sum(nums)
            if total != 100:
                errs.append(f"rubric 权重和={total}，应为 100")
    return errs

def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--jury":
        root = Path(args[1]) if len(args) > 1 else Path("skill/jury")
        checker = check_jury_text
    else:
        root = Path(args[0]) if args else Path("skill/frameworks")
        checker = check_text
    bad = 0
    for f in sorted(root.glob("*.md")):
        if f.name.startswith("_"):
            continue
        errs = checker(f.read_text(encoding="utf-8"))
        if errs:
            bad += 1
            print(f"❌ {f.name}: " + "; ".join(errs))
        else:
            print(f"✅ {f.name}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
