#!/usr/bin/env bash
# superyouzi 一键安装：把 skill 装进 Claude Code（或用第一个参数指定目录）
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/skill"; [ -d "$SRC" ] || SRC="$DIR/../skill"
[ -d "$SRC" ] || { echo "❌ 找不到 skill/ 目录，请确认 zip 已完整解压"; exit 1; }
TARGET="${1:-$HOME/.claude/skills/superyouzi}"
case "$TARGET" in
  ""|"/"|"$HOME") echo "❌ 拒绝安装到危险目录: $TARGET"; exit 1 ;;
esac
echo "→ 安装到: $TARGET"
PARENT="$(dirname "$TARGET")"
mkdir -p "$PARENT"
STAGE="$(mktemp -d "$PARENT/.superyouzi-install.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$SRC/." "$STAGE/"
rm -rf "$TARGET"
mv "$STAGE" "$TARGET"
trap - EXIT
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
echo ""
echo "→ 安装数据依赖（失败不影响使用，会自动降级联网取数）"
"$PY" -m pip install -r "$TARGET/scripts/requirements.txt" --quiet 2>/dev/null || echo "  ⚠️ 依赖未装全，跳过"
if OUT=$("$PY" "$TARGET/scripts/fetch.py" quote 600519 2>/dev/null) && \
   printf '%s' "$OUT" | "$PY" -c \
     'import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if d.get("ok") and d.get("data") else 1)'
then
  echo "✅ 数据脚本自检通过"
else
  echo "⚠️ 数据自检未通过（可能离线或缺依赖），框架功能不受影响"
fi
echo ""
echo "✅ 安装完成。下一步：新开一个 AI 会话，直接问："
echo "   「今天市场情绪怎么样，短线能做吗？」"
