# LLM Comparison MCP Server

在**智谱AI、千问、Kimi、MiniMax** 四个大模型网页上同时提问，并在一个对比页中并排查看回复的 MCP 服务器。

## 功能概览

- **多平台并行**：一次向 4 个 LLM 网页发送同一问题，勾选即可选择参与平台。
- **网页对比界面**：HTTP 模式启动后自动打开/复用浏览器，提供对比页（`http://localhost:8000/`），支持「发送问题」「获取回复并对比」；回复以 **Markdown** 展示。
- **浏览器常驻**：用 Ctrl+C 结束程序时**不会**关闭浏览器和已打开的标签，下次启动会优先复用已有窗口并只补开缺失的 Tab。
- **Cookie / 用户数据**：登录态保存在 `~/.llm_comparison_cookies/`，再次启动可沿用。
- **双模式**：支持 **stdio**（仅 MCP 工具调用）与 **HTTP**（Web 界面 + 同上能力）。

## 支持的平台

| 平台   | 标识符  | 网址 |
|--------|---------|------|
| 智谱AI | zhipu   | https://chatglm.cn/ |
| 千问   | qwen    | https://www.qianwen.com/ |
| Kimi   | kimi    | https://www.kimi.com/ |
| MiniMax| minimax | https://agent.minimaxi.com/ |

## 安装

```bash
# 使用 uv 安装依赖（推荐）
uv sync --extra test

# 安装 Playwright 使用的 Chromium
uv run playwright install chromium
```

要求：Python ≥3.11。

## 使用方式

### 方式一：HTTP 模式（推荐，带对比页）

```bash
uv run python -m src.server 8000
```

- 若本机已有在 9222 端口开启调试的浏览器，会**复用**其窗口与标签（自动识别四平台页和对比页），缺的再开新 Tab。
- 否则会以**独立进程**启动一个 Chromium，并打开 4 个平台 Tab + 1 个对比页 Tab。
- 在浏览器中打开 **http://localhost:8000/** 即可使用对比页：
  - 输入问题 → 选择平台 → 点击「发送问题」向各平台发送；
  - 再点击「获取回复并对比」拉取各平台最新一条回复并排展示（Markdown 渲染）。
- 使用 **Ctrl+C** 结束程序时，浏览器和所有标签会**保持打开**，下次启动可继续用同一窗口。

### 方式二：MCP 工具调用（stdio）

在支持 MCP 的客户端中配置本服务器后，可调用工具，例如：

- **llm_compare**：向多个平台发问并对比结果  
  `{ "question": "你的问题", "platforms": ["zhipu", "qwen", "kimi", "minimax"], "response_format": "markdown" }`
- **llm_query_single**：仅向一个平台发问  
  `{ "platform": "zhipu", "question": "你的问题" }`
- **llm_check_login**：检查各平台登录状态  
  `{ "platform": "zhipu" }` 或不传 platform 检查全部
- **llm_save_session**：保存当前浏览器会话 Cookie  
  `{ "platform": "zhipu" }`

启动命令：

```bash
uv run python -m src.server
```

## 登录与 Cookie

- 首次使用需在自动打开的对应平台 Tab 中**手动登录**。
- 登录信息保存在 `~/.llm_comparison_cookies/`（各平台一个 JSON），以及浏览器的用户数据目录，下次启动会自动加载。
- 若某平台未登录或 Cookie 失效，在对比页操作时该平台会报错，可在对应 Tab 重新登录后再试。

## HTTP 接口说明（供前端或脚本调用）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/` | 对比页 HTML |
| GET  | `/health` | 健康检查 |
| POST | `/query` | 发送问题到选中平台，body: `{ "question": "...", "platforms": ["zhipu", ...] }` |
| GET  | `/status` | 各平台当前回复状态（可轮询） |
| POST | `/fetch-replies` | 拉取各平台最新回复，用于并排对比 |
| POST | `/open-platforms` | 为未打开的平台新开 Tab，body 可选 `{ "platforms": ["zhipu", ...] }` |

## 技术栈

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)（包管理）
- [MCP](https://modelcontextprotocol.io/)（FastMCP）
- [Playwright](https://playwright.dev/python/)（浏览器自动化）
- Pydantic（数据校验）
- 前端：单页 HTML + marked.js + DOMPurify（Markdown 展示与安全）

## 测试

```bash
# 运行全部测试
uv run python -m pytest tests/ -v

# 仅运行 HTTP 相关测试
uv run python -m pytest tests/test_http_routes.py -v
```

测试覆盖：数据模型、Cookie、响应分析、HTTP 路由及回复抓取（含「hello」示例）。

## 许可证

MIT
