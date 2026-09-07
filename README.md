# superyouziskills · 游资短线投研助手

免费完整版，无需激活码。包含 15 套交易框架、1 套风险框架、28 位深研评审档案、本地数据脚本和 HTML 报告模板。

用于 A 股市场复盘、题材梳理、个股研究和风险排查。数据脚本取数，AI 按框架分析，用户独立决策。人物档案是本项目整理的方法论，不代表本人参与、认可或背书；评分和阈值须结合各档案的来源与诚实声明理解。

## 安装

需要支持本地 Skill 的 AI 助手。数据脚本需要 Python 3.9+；依赖见 `skill/scripts/requirements.txt`。本项目不提供模型服务，所用 AI 平台和数据源遵循各自的使用规则与费用安排。

从源码仓库安装：

```bash
git clone https://github.com/leslieyeo/superyouziskills.git
cd superyouziskills
bash installer/install.sh
```

默认安装到 `~/.claude/skills/superyouzi`，可用第一个参数指定助手使用的 Skill 目录：

```bash
bash installer/install.sh /你的技能目录/superyouzi
```

安装会替换目标目录的旧版本，包括目录内自行修改的文件；有自定义内容请先备份。安装脚本会安装 Python 依赖，并请求一次行情检查数据通路。自检失败会显示提示，不会伪报数据可用。

下载 ZIP 后完整解压：macOS 可双击 `install.command`，Windows 可运行 `install.bat`；也可在解压目录执行 `bash install.sh`。

## 使用

安装后新开 AI 会话，尝试：

- 今天市场情绪怎么样，短线能做吗？
- 分析一下某只股票，给出情景预案和证伪条件。
- 给某代码做个深度体检，说明数据缺失和评审分歧。

更多例子见 [上手指南](skill/上手指南.md) 和 [提问模板](skill/提问模板.md)。历史样报在 `docs/examples/`，仅作格式参考，数据与判断不代表当前行情。

手动检查数据脚本：

```bash
python3 -m pip install -r skill/scripts/requirements.txt
python3 skill/scripts/fetch.py panel
python3 skill/scripts/fetch.py quote 600519
```

数据源可能不可用或只返回部分字段，以 JSON 的 `ok`、`partial`、`hint` 为准。缺数据时按 Skill 规则联网补充或注明依据不足。无法运行脚本的环境需要 AI 助手自身具备联网检索能力。

## 开发与打包

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -q
bash tools/package.sh /你的输出目录
```

打包先运行测试与框架校验，通过后生成唯一的 `superyouzi-free.zip`，内含完整 Skill、安装脚本和本说明。

## 边界

所有输出仅供研究与复盘，不构成投资建议，不保证收益。引用材料与第三方数据的权利归各自权利人；现有资料的引用不代表本项目取得其再授权。本项目原创代码与原创文档采用 [MIT 许可证](LICENSE)，第三方引用、素材和数据不在本项目的再授权范围内。
