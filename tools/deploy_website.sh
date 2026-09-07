#!/usr/bin/env bash
# 从统一仓库发布网站到现有 Cloudflare Pages 项目。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
command -v npx >/dev/null || { echo '需要 Node.js/npm（npx）'; exit 1; }
git -C "$ROOT" diff HEAD --quiet -- website tools/deploy_website.sh LICENSE || {
  echo '请先提交网站、部署脚本和许可文件的修改，再发布。'; exit 1;
}
if [ -n "$(git -C "$ROOT" ls-files --others --exclude-standard -- website)" ]; then
  echo 'website/ 存在未提交的新文件，请先提交。'; exit 1
fi
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/superyouzi-website.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
cp "$ROOT/website/index.html" "$STAGE/index.html"
cp -R "$ROOT/website/assets" "$STAGE/assets"
cp -R "$ROOT/website/sales" "$STAGE/sales"
cp "$ROOT/LICENSE" "$STAGE/LICENSE"
REV="$(git -C "$ROOT" rev-parse HEAD)"
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-c79bf3a1f8da6ab04eac8926eaca969b}"
cd "$STAGE"
npx --yes wrangler@4.129.0 pages deploy "$STAGE" \
  --project-name superyouziskill --branch main \
  --commit-hash "$REV" --commit-message "发布 superyouziskills website: $REV"
