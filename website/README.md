# 项目网站

superyouziskills 的静态介绍页，与 Skill 在同一个仓库维护。

- `index.html`：首页、安装说明与 GitHub 入口。
- `assets/`：本地头像、网页字体及字体许可说明。
- `sales/样报/`：三份 HTML 样报和预览图；保留目录名称以兼容已有链接。
- `scripts/build_font.py`：按当前页面内容重新生成网页字体子集。

## 本地预览

在仓库根目录执行：

```bash
python3 -m http.server 8000 --directory website
```

打开 http://localhost:8000 。网页字体采用 OFL 1.1，来源见 [字体说明](assets/fonts/README.md)。修改文字后，用 fonttools 和 brotli 重新生成子集：

```bash
python3 website/scripts/build_font.py skill/report/fonts/LXGWWenKaiScreen.ttf
```

## 部署

网站复用 Cloudflare Pages 项目 `superyouziskill`，生产分支标识为 `main`，域名保持：

- https://superyouziskill.store
- https://www.superyouziskill.store
- https://superyouziskill.pages.dev

该项目采用直接上传，GitHub push 不会自动部署。完成修改、验证并提交后，在仓库根目录执行：

```bash
bash tools/deploy_website.sh
```

需要 Node.js/npm，以及具备该账户 Pages 编辑权限的 `CLOUDFLARE_API_TOKEN`（或已登录 Wrangler）。脚本使用 Wrangler 4.129.0，只上传首页、静态资源、样报和许可文件；临时发布目录在系统临时目录创建并在结束后移除，不上传 Skill、测试、开发脚本或本地凭据。

Skill 安装包不包含 `website/`。网站许可遵循仓库根目录 [使用许可](../README.md#使用许可)；字体与第三方素材保留各自权利。旧落地页仓库仅作为历史档案，不再用于发布。
