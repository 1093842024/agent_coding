# LLM Comparison MCP Server

一个MCP服务器工具，可以同时通过智谱AI、千问、Kimi和MiniMax四个大模型网页平台回答问题，并收集结果进行对比分析。

## 功能特性

- **多平台并行查询**: 同时向4个LLM平台发送问题
- **Cookie自动管理**: 自动读取/保存Cookie，失败则提示用户手动登录
- **响应对比**: 并排显示原始回复
- **AI分析**: 自动评估回答质量和一致性
- **双重接口**: 支持MCP工具调用 + 网页界面

## 支持的平台

- 智谱AI (Zhipu AI)
- 千问 (Qwen/Tongyi)
- Kimi (Moonshot AI)
- MiniMax

## 安装

```bash
# 安装依赖
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

## 使用方式

### 方式1: MCP工具调用

配置MCP服务器后，可以使用以下工具：

```json
{
  "name": "llm_compare",
  "parameters": {
    "question": "什么是人工智能？",
    "platforms": ["zhipu", "qwen", "kimi", "minimax"]
  }
}
```

### 方式2: 网页界面

```bash
# 启动MCP服务器
python -m src.server --port 8000

# 或使用HTTP传输
python -m src.server 8000

# 然后打开 frontend/index.html
```

## MCP工具

### llm_compare

比较多个LLM平台的响应。

```python
{
    "question": "你的问题",
    "platforms": ["zhipu", "qwen", "kimi", "minimax"],  # 可选，默认全部
    "response_format": "markdown"  # 或 "json"
}
```

### llm_query_single

查询单个LLM平台。

```python
{
    "platform": "zhipu",
    "question": "你的问题"
}
```

### llm_check_login

检查平台登录状态。

```python
{
    "platform": "zhipu"  # 可选，默认检查全部
}
```

### llm_save_session

保存当前浏览器会话。

```python
{
    "platform": "zhipu"
}
```

## 登录流程

1. 首次运行时，工具会尝试加载保存的Cookie
2. 如果Cookie无效或不存在，会提示用户手动登录
3. 用户在弹出的浏览器窗口中登录各平台
4. 登录成功后，会话会自动保存供下次使用

## 技术栈

- Python 3.11+
- MCP (FastMCP)
- Playwright
- Pydantic

## 许可证

MIT
