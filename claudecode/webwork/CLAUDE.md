# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 MCP 服务器工具，用于同时通过智谱AI、千问、Kimi 和 MiniMax 四个中国大模型网页平台回答问题，并收集结果进行对比分析。

**HTTP 模式（推荐）**：执行 `uv run python -m src.server 8000` 时，会自动打开一个浏览器窗口，创建 4 个 Tab 分别打开四个大模型平台网站（并加载缓存的登录信息），第 5 个 Tab 打开本项目的对比页面（http://localhost:8000/）。前端提供「发送问题」与「获取回复并对比」两个按钮，并在 60 秒内轮询各平台回复状态（发送问题、等待模型响应中、模型回复中/思考中、模型已完成问题回复）。

## 常用命令

```bash
# 使用 uv 安装依赖
uv sync --extra test

# 安装 Playwright 浏览器
uv run playwright install chromium

# 运行测试
uv run python -m pytest tests/ -v

# 运行单个测试文件
uv run python -m pytest tests/test_models.py -v

# 启动 MCP 服务器 (stdio 模式)
uv run python -m src.server

# 启动 MCP 服务器 (HTTP 模式，端口 8000)
uv run python -m src.server 8000
```

## 项目架构

### 核心组件

- **src/server.py**: MCP 服务器主入口，包含所有工具定义和平台查询逻辑
- **frontend/index.html**: 网页界面，用于可视化和对比结果
- **pyproject.toml**: Python 项目配置，定义依赖和测试配置

### 技术栈

- **MCP (FastMCP)**: 模型上下文协议服务器
- **Playwright**: 浏览器自动化，用于访问各 LLM 平台网页
- **Pydantic**: 数据验证和模型定义
- **asyncio**: 异步并发处理

### 支持的平台

| 平台 | 标识符 | URL |
|------|--------|-----|
| 智谱AI | zhipu | https://chatglm.cn/ |
| 千问 | qwen | https://www.qianwen.com/ |
| Kimi | kimi | https://www.kimi.com/ |
| MiniMax | minimax | https://agent.minimaxi.com/ |

### MCP 工具

1. **llm_compare**: 并行查询多个 LLM 平台并对比结果
2. **llm_query_single**: 查询单个 LLM 平台
3. **llm_check_login**: 检查平台登录状态
4. **llm_save_session**: 保存当前浏览器会话 Cookie

### HTTP 模式（端口启动时）

1. 启动时打开一个浏览器，依次创建 4 个 Tab 打开四个大模型网站，并读取 `~/.llm_comparison_cookies/` 下各平台 Cookie；若无缓存则需在对应 Tab 内手动登录。
2. 第 5 个 Tab 打开对比页面（根路径 `/`）。
3. **发送问题**：仅向各平台 Tab 发送问题，不等待或拉取回复；后台在 60s 内每 2s 轮询各页状态并更新：发送问题、等待模型响应中、模型回复中/模型思考中、模型已完成问题回复。
4. **获取回复并对比**：从各平台页面抓取最新一条模型回复，在对比页并排展示。

### 自定义 HTTP 接口

- `GET /`：对比页前端（index.html）
- `GET /health`：健康检查
- `POST /query`：发送问题到所选平台 Tab（body: `{ "question": "...", "platforms": ["zhipu", "qwen", "kimi", "minimax"] }`）
- `GET /status`：当前各平台回复状态（供前端轮询）
- `POST /fetch-replies`：拉取各平台最新回复并返回，用于并排对比

### 数据流程（MCP 工具）

1. 用户调用 MCP 工具或通过网页界面提交问题
2. 服务器使用 Playwright 打开各平台网页
3. 自动加载保存的 Cookie 进行登录
4. 在输入框填写问题并提交
5. 等待响应并提取结果
6. 返回并排显示的对比结果

### Cookie 管理

- Cookie 存储位置: `~/.llm_comparison_cookies/`
- 每个平台一个 JSON 文件: `{platform}.json`
- 首次使用需手动登录，登录成功后自动保存

## 测试

测试位于 `tests/` 目录:
- `test_models.py`: 数据模型测试
- `test_cookies.py`: Cookie 管理测试
- `test_analyze.py`: 响应分析测试
- `test_http_routes.py`: HTTP 自定义路由测试（/health, /query, /status, /fetch-replies, /）

运行全部测试：`uv run python -m pytest tests/ -v`


<claude-mem-context>

</claude-mem-context>