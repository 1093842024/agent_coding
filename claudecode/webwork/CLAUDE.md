# CLAUDE.md

本文件为 Claude Code 在本仓库中协作开发时提供项目说明与约定。

## 项目概述

本仓库是一个 **MCP 服务器**，用于在**智谱AI、千问、Kimi、MiniMax** 四个国内大模型网页平台上并行提问，并收集、对比展示回复。

- **推荐用法**：HTTP 模式。执行 `uv run python -m src.server 8000` 后：
  - 若本机已有在 CDP 端口 9222 上监听的浏览器，则**复用**其窗口与标签（按 URL 匹配四平台 + 对比页），缺的再开新 Tab。
  - 若无，则以**独立进程**启动 Chromium（`--user-data-dir` + `--remote-debugging-port=9222`），通过 CDP 连接后新建 4 个平台 Tab 与 1 个对比页 Tab。
  - 对比页地址：`http://localhost:8000/`，由同一服务提供静态 `frontend/index.html`。
- **前端能力**：输入问题、勾选平台 → 「发送问题」向各平台 Tab 发送；「获取回复并对比」从各 Tab 抓取最新一条模型回复，在对比页并排以 **Markdown** 展示；「打开未打开的模型网站」可补开缺失的平台 Tab。
- **退出行为**：Ctrl+C 仅结束本进程；**不**关闭浏览器与标签（不调用 `context.close()` / `playwright.stop()`），浏览器由独立进程或已有窗口保持运行，下次启动可继续复用。

## 常用命令

```bash
# 安装依赖（含测试）
uv sync --extra test

# 安装 Playwright 使用的 Chromium
uv run playwright install chromium

# 运行全部测试
uv run python -m pytest tests/ -v

# 运行单个测试文件
uv run python -m pytest tests/test_http_routes.py -v

# 启动 MCP 服务器（stdio 模式，仅工具调用）
uv run python -m src.server

# 启动 MCP 服务器（HTTP 模式，端口 8000，自动开/复用浏览器与对比页）
uv run python -m src.server 8000
```

## 项目结构

| 路径 | 说明 |
|------|------|
| `src/server.py` | 服务入口：MCP 定义、HTTP 路由、浏览器生命周期、各平台发问/抓取回复逻辑 |
| `frontend/index.html` | 对比页单页：问题输入、平台勾选、发送/拉取回复、并排展示（Markdown 渲染） |
| `tests/` | 单元与接口测试 |
| `pyproject.toml` | 项目与依赖配置、pytest 配置 |

## 技术栈

- **MCP**：FastMCP，提供工具与 HTTP 能力
- **Playwright**：浏览器自动化（访问各 LLM 网页、填表、抓取回复）
- **Pydantic**：请求/响应与配置模型
- **asyncio**：异步并发
- **前端**：单 HTML，使用 marked.js + DOMPurify 做 Markdown 渲染与安全过滤

## 支持的平台

| 平台 | 标识符 | 网页 URL |
|------|--------|----------|
| 智谱AI | zhipu | https://chatglm.cn/ |
| 千问 | qwen | https://www.qianwen.com/ |
| Kimi | kimi | https://www.kimi.com/ |
| MiniMax | minimax | https://agent.minimaxi.com/ |

## 运行模式

### stdio 模式（无端口参数）

- `uv run python -m src.server`
- 仅暴露 MCP 工具（如 `llm_compare`、`llm_query_single`、`llm_check_login`、`llm_save_session`），无 HTTP、不自动开浏览器。

### HTTP 模式（带端口参数）

- `uv run python -m src.server 8000`
- 启动时：
  1. 尝试 `connect_over_cdp("http://127.0.0.1:9222")` 连接已有浏览器；若有 context 且存在标签，则按 URL 识别四平台页与对比页，缺的再 `new_page()` 并 `goto`。
  2. 若未连接成功，则通过 `_launch_browser_detached()` 用 subprocess 以**独立进程**启动 Chromium（`--user-data-dir=~/.llm_comparison_cookies/browser_data`、`--remote-debugging-port=9222`），轮询 CDP 就绪后 `connect_over_cdp`，再创建 4 个平台 Tab + 1 个对比 Tab。
  3. 若独立启动失败（如找不到 Chromium），则回退到 `launch_persistent_context(..., args=["--remote-debugging-port=9222"])`，此时浏览器为子进程，Ctrl+C 会一并退出。
- 退出时：仅清理内存中的 `state` 与 `http_state`，**不**关闭 browser/context，浏览器窗口与标签保持打开。

## HTTP 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 对比页前端（`frontend/index.html`） |
| GET | `/health` | 健康检查，返回 `status`、`browser_ready` |
| POST | `/query` | 向选中平台 Tab 发送问题；body: `{ "question": "...", "platforms": ["zhipu", ...] }` |
| GET | `/status` | 当前各平台回复状态（供前端轮询） |
| POST | `/fetch-replies` | 从各平台 Tab 抓取最新一条模型回复，返回并排对比数据 |
| POST | `/open-platforms` | 为未打开或已关闭的平台新开 Tab；body 可选 `{ "platforms": [...] }` |

## 回复抓取逻辑（获取回复并对比）

- 各平台有独立选择器列表（如 `[data-role='assistant']`、`.markdown-body`、平台相关 class），在页面内合并候选节点、按文档顺序取**最后一段长度 ≥ 15 的文本**作为回复。
- MiniMax 额外有 `MINIMAX_FALLBACK_JS`：在主选择器未取到足够长文本时，在 `main` / 含 container、chat、conversation 的根下再找最后一段有效回复。
- 前端收到回复后使用 marked + DOMPurify 以 Markdown 形式渲染。

## Cookie 与用户数据

- Cookie 目录：`~/.llm_comparison_cookies/`，按平台存 `{platform}.json`。
- 浏览器持久化数据目录：`~/.llm_comparison_cookies/browser_data`（`launch_persistent_context` 或独立进程的 `--user-data-dir`）。
- 首次使用需在对应 Tab 内手动登录；登录态会随 Cookie/用户数据保留。

## 测试

- `tests/test_models.py`：数据模型与校验
- `tests/test_cookies.py`：Cookie 读写
- `tests/test_analyze.py`：响应分析逻辑
- `tests/test_http_routes.py`：HTTP 路由与回复抓取（含 /health、/query、/status、/fetch-replies、/、hello 场景）

运行：`uv run python -m pytest tests/ -v`

## 开发与排错注意

- 修改各平台网页选择器时，请同步看 `ZHIPU_REPLY_SELECTORS`、`QWEN_REPLY_SELECTORS`、`KIMI_REPLY_SELECTORS`、`MINIMAX_REPLY_SELECTORS` 及 `MINIMAX_FALLBACK_JS`。
- 保持「退出不关浏览器」依赖：不在 lifespan 的 `finally` 里调用 `context.close()` / `playwright.stop()`；新开浏览器时优先用 `_launch_browser_detached()` 以独立进程启动，便于 Ctrl+C 后窗口保留。
