# 贪吃蛇游戏 (Snake Game)

一个使用 Python 和 Pygame 创建的经典贪吃蛇游戏。

## 🚀 快速开始

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理和环境配置。

### 安装 uv

如果您还没有安装 uv：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip
pip install uv
```

### 安装依赖

```bash
uv sync
```

### 运行游戏

```bash
uv run main.py
```

或者：

```bash
uv run python main.py
```

### 查看项目依赖

```bash
uv tree
```

## 游戏控制

- **方向键 (↑ ↓ ← →)**: 控制蛇的移动方向
- **Q**: 退出游戏
- **C**: 重新开始游戏

## 游戏规则

1. 使用方向键控制蛇移动
2. 吃到红色食物可以得分并增加蛇的长度
3. 撞到墙壁或自己的身体游戏结束
4. 游戏结束后按 C 重新开始，按 Q 退出

## 🎮 游戏控制

- **方向键 (↑ ↓ ← →)**: 控制蛇的移动方向
- **Q**: 退出游戏
- **C**: 重新开始游戏

## 📜 游戏规则

1. 使用方向键控制蛇移动
2. 吃到红色食物可以得分并增加蛇的长度
3. 撞到墙壁或自己的身体游戏结束
4. 游戏结束后按 C 重新开始，按 Q 退出

## ✨ 游戏特性

- 🎮 流畅的游戏体验（60 FPS）
- 🏆 实时得分显示
- 🎨 简洁的视觉效果
- 🔄 游戏结束后可重新开始
- 🎯 防止反向移动（不能直接反方向移动）
- 📱 响应式游戏窗口（800x600）

## 📁 项目结构

```
snake-game/
├── main.py           # 游戏主程序
├── pyproject.toml    # 项目配置和依赖
├── .python-version   # Python 版本指定
├── README.md         # 项目文档
└── .venv/           # 虚拟环境（由 uv 管理）
```

## 🔧 配置说明

### Python 版本
项目使用 Python 3.13+，在 `.python-version` 文件中指定。

### 依赖项
- `pygame>=2.5.0`: 用于游戏开发和图形渲染

### 游戏参数
在 `main.py` 中可以调整以下参数：
- `WIDTH`: 窗口宽度（默认：800）
- `HEIGHT`: 窗口高度（默认：600）
- `SNAKE_SIZE`: 蛇和食物的大小（默认：20）
- `SNAKE_SPEED`: 游戏速度，帧率（默认：15）

### 颜色配置
游戏使用的颜色可以在 `main.py` 中自定义：
- `WHITE`: 背景色
- `BLACK`: 前景色
- `RED`: 食物颜色
- `GREEN`: 蛇的颜色
- `BLUE`: 得分文字颜色

## 🛠️ 开发说明

### 添加新功能
1. 在 `main.py` 中修改相应的函数
2. 如需添加新的依赖，编辑 `pyproject.toml`
3. 运行 `uv sync` 同步依赖

### 调试
使用 `uv run python main.py` 运行游戏，控制台会输出 pygame 初始化信息。

## 📄 许可证

本项目仅供学习和娱乐使用。

## 🎉 祝你玩得开心！
