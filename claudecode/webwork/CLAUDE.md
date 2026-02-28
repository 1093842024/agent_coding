# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 MCP 服务器工具，用于同时通过智谱AI、千问、Kimi 和 MiniMax 四个中国大模型网页平台回答问题，并收集结果进行对比分析。

## 常用命令

```bash
# 使用 uv 安装依赖
uv sync --extra test

# 安装 Playwright 浏览器
uv run playwright install chromium

# 运行测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_models.py

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
| 智谱AI | zhipu | https://www.zhipuai.cn/ |
| 千问 | qwen | https://tongyi.aliyun.com/ |
| Kimi | kimi | https://kimi.moonshot.cn/ |
| MiniMax | minimax | https://platform.minimax.io/ |

### MCP 工具

1. **llm_compare**: 并行查询多个 LLM 平台并对比结果
2. **llm_query_single**: 查询单个 LLM 平台
3. **llm_check_login**: 检查平台登录状态
4. **llm_save_session**: 保存当前浏览器会话 Cookie

### 数据流程

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


<claude-mem-context>

</claude-mem-context>