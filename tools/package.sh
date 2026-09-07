#!/usr/bin/env bash
# 构建免费完整版；输出目录由调用方指定，避免在源码库产生任务产物。
set -euo pipefail
OUT="${1:?用法: bash tools/package.sh <输出目录>}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python3 -m pytest tests/ -q -p no:cacheprovider
python3 tools/lint_frameworks.py skill/frameworks
python3 tools/lint_frameworks.py skill/meta
python3 tools/lint_frameworks.py skill/risk
python3 tools/lint_frameworks.py --jury skill/jury
test "$(find skill/frameworks -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')" = "13"
test "$(find skill/meta -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')" = "2"
test "$(find skill/risk -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')" = "1"
test "$(find skill/jury -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')" = "28"
python3 - "$OUT" <<'PY'
import sys
import zipfile
from pathlib import Path

output = Path(sys.argv[1]) / 'superyouzi-free.zip'
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(Path('skill').rglob('*')):
        if p.is_file() and not any(x in p.parts for x in ('__pycache__', '.cache', '.DS_Store')):
            z.write(p, p.as_posix())
    for name in ('install.sh', 'install.command', 'install.bat'):
        z.write(Path('installer') / name, name)
    for folder in ('docs/examples', 'docs/images'):
        for p in sorted(Path(folder).rglob('*')):
            if p.is_file() and p.name != '.DS_Store':
                z.write(p, p.as_posix())
    z.write('README.md', 'README.md')
    if Path('LICENSE').exists():
        z.write('LICENSE', 'LICENSE')
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
print(f'免费完整版已生成：{output}')
PY
