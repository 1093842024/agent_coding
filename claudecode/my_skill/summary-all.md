# Claude Code 完全指南

本指南整合了多个 AI 源的 Claude Code 中文指南摘要，旨在提供一份逻辑清晰、有学习分享价值的文档。

---

# 第一章 概述与安装配置

## 一、Claude Code 概述

### 1.1 什么是 Claude Code

Claude Code 是由 Anthropic 于 2025 年 2 月 24 日发布的 AI 编程助手。它是一款集成在终端中的智能编码工具，能够理解代码库并通过自然语言指令帮助开发者更快地编写代码。与传统的 IDE 集成 AI 助手不同，Claude Code 采用纯终端界面的设计理念。

Claude Code 的核心定位是"受监督编码代理"，它能够在软件开发工作流程中执行相对复杂的任务，有时甚至可以自主完成整个开发流程。

### 1.2 Claude Code 的核心优势

- **智能对话式编程能力**：通过自然语言描述需求，自动生成高质量代码
- **跨平台兼容性**：支持 macOS、Linux、Windows 三大主流操作系统
- **成本控制优势**：提供 Opus（高级）和 Sonnet（性价比）两种模型选择

### 1.3 Claude Code 的发展历程

- **基础建设期**：核心功能构建，终端体验优化
- **能力扩展期**：功能丰富与优化
- **代理框架成熟期**：代理系统完善，引入 Hooks、Subagents、MCP
- **生态系统期**：插件生态与集成扩展

### 1.4 与传统工具的区别

Claude Code 与 GitHub Copilot 等 IDE 插件式代码补全工具最大的不同在于作用范围和工作方式：

| 特性 | Claude Code | GitHub Copilot |
|------|-------------|----------------|
| 作用范围 | 项目级别，处理整个流程 | 编码时的代码片段补全 |
| 交互方式 | 多轮对话，逐步完善 | 一次性建议 |
| 执行能力 | 可自主完成整个开发流程 | 仅提供补全建议 |
| 适用场景 | 复杂任务、自动化、重构 | 日常编码辅助 |

**最佳实践**：两者可以结合使用——先用 Claude Code 理清思路或处理繁重任务，再用 Copilot 进行细节编码。

---

## 二、安装与配置

### 2.1 系统要求

| 类别 | 要求 |
|------|------|
| 操作系统 | macOS 10.15+、Ubuntu 20.04+/Debian 10+、WSL（Windows） |
| 硬件 | 4GB 以上内存 |
| 软件 | Node.js 18+（推荐 LTS 20+）、git 2.23+、ripgrep（可选） |

**前置要求**：Claude 订阅（Pro/Max/Teams/Enterprise）或 Console API 账户

### 2.2 安装方式

| 方式 | 命令/方法 | 适用场景 |
|------|-----------|----------|
| **原生安装** | 官方安装包 | 大多数用户 |
| **Homebrew** | `brew install claude-code` | macOS 用户 |
| **NPM** | `npm install -g @anthropic-ai/claude-code` | Node.js 开发者 |
| **手动安装** | 下载二进制文件 | 企业/自定义环境 |

**Windows 特殊说明**：推荐使用 Windows Terminal，先安装 Node.js LTS 20.x，再通过 npm 全局安装。可用国内镜像：

```bash
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com
```

**Linux 特殊说明**：建议使用 nvm 管理 Node.js 后安装 Claude Code。

### 2.3 验证安装

```bash
claude --version
```

### 2.4 首次认证与登录

运行 `claude` 命令首次会跳转至网页进行 OAuth 认证。Claude Code 支持多种认证方式：
- **Anthropic 账户**：直接使用 Anthropic 账号登录
- **GitHub 账户**：使用 GitHub 账号进行 OAuth 认证

登录成功后，所有会话自动免认证。

### 2.5 权限控制系统

Claude Code 采用严格的权限控制机制，每次文件修改和命令执行都需要用户批准。可以在 `.claude/settings.json` 中配置：

**工具权限**：
```json
{
  "permissions": {
    "allow": ["Bash npm test", "Bash npm run lint"],
    "deny": ["Write src/config/*"]
  }
}
```

**文件权限（扩展工作目录）**：
```json
{
  "permissions": {
    "additionalDirectories": ["../docs/", "../shared/"]
  }
}
```

**审计日志**：记录所有执行的操作，便于回顾和合规审查。

### 2.6 配置命令别名

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias cc='cd ~/projects && claude'
```

---

## 三、核心概念

### 3.1 Agentic Search

Claude Code 能够自动扫描、映射整个项目，无需手动选择文件。它能够理解代码库结构，并根据任务需求智能定位相关代码。

### 3.2 权限系统

Claude Code 采用严格的权限控制机制：每次文件修改和命令执行都需要用户的批准。这一设计确保了操作的安全性和可控性。

```bash
# 谨慎使用，可跳过确认
claude --dangerously-skip-permissions
```

### 3.3 上下文窗口

- **标准上下文**：200K token
- **扩展上下文**：Opus 4.6 支持 1M token（Beta）

---

## 四、基础命令

### 4.1 必学斜杠命令

| 命令 | 功能 | 使用场景 |
|------|------|----------|
| `/help` | 显示所有命令 | 随时查阅 |
| `/plan` | 进入计划模式 | 复杂任务前先规划 |
| `/compact` | 压缩对话历史 | 上下文窗口不足时 |
| `/clear` | 清空对话 | 开始新话题 |
| `/commit` | AI 生成提交信息并提交 | 代码完成后 |
| `/review` | 审查代码变更 | PR 前检查 |
| `/config` | 配置菜单 | 修改设置 |
| `/cost` | 查看 Token 使用情况 | 成本控制 |
| `/status` | 系统/账户状态 | 查看当前模型和用量 |

### 4.2 基本使用模式

- **交互模式**：`claude` —— 启动持续对话
- **一次性任务模式**：`claude "修复构建错误"` —— 执行完任务后退出
- **一次性查询模式**：`claude -p "解释这个函数"` —— 获取答案后退出
- **继续会话模式**：`claude -c` 或 `claude --resume` —— 恢复之前的对话

---

# 第二章 基础使用与 CLAUDE.md

## 一、CLAUDE.md 项目配置

### 1.1 是什么

`CLAUDE.md` 是放在项目根目录的"系统提示"，定义项目边界、约束和风格。Claude Code 在开始对话时会自动将其拉入上下文，用于记录项目规范、编码约定、常用命令等信息。

可以记录的内容包括：常用 bash 命令、核心文件和实用函数、代码风格指南、测试说明、代码库规范、开发环境设置、项目特有的意外行为等。

### 1.2 创建方式

在项目根目录运行 `/init` 命令，Claude Code 会自动扫描代码库并生成 CLAUDE.md 文件。也可以手动创建。

### 1.3 放置位置

- **项目根目录（推荐）**：放置在代码库根目录，检入 git 共享
- **父目录**：monorepo 项目中可放在父目录
- **子目录**：放在运行 claude 的子目录中，覆盖局部行为
- **主目录**：`~/.claude/CLAUDE.md` 作为全局级别规范

### 1.4 最佳实践

- **全局配置**：在 `~/.claude/claude.md` 放置团队共识（术语、代码风格）
- **局部覆盖**：在子目录放置专属 `claude.md` 覆盖局部行为
- **动态更新**：在对话中用 `#` 开头的指令追加到 `claude.md`
- **定期重构**：删除空话与过期约束，保留"可执行的、可验证的"规则
- **简洁原则**：建议不超过 150 行，内容应简洁且人类可读

**示例片段**：

```markdown
# 代码风格
- TypeScript 必写显式导出类型；禁止 any；函数用动词短语命名

# PR 审查标准
- 所有变更需包含测试；覆盖到关键分支；提供风险与回滚方案

# 架构约束
- 所有 API 调用必须通过 services/ 目录下的封装
- UI 组件必须使用 Tailwind CSS，禁止内联样式
```

---

## 二、Plan Mode 计划模式

### 2.1 核心原则

任何非平凡任务前先规划。

### 2.2 使用方法

- 输入 `/plan` 进入计划模式
- 或在提示前加 `Plan:` 前缀

Plan Mode 会：
1. 询问澄清问题
2. 提出执行计划
3. 等待你批准或修改
4. 执行计划

### 2.3 适用场景

- 多文件变更（操作顺序重要）
- 重构任务（需理解影响范围）
- 涉及认证、支付、数据迁移的功能

---

## 三、上下文管理

### 3.1 压缩对话

长对话后使用 `/compact` 主动压缩，保留关键信息。建议在 50% 左右上下文使用率时开始压缩。

### 3.2 排除文件

创建 `.claudeignore` 文件，类似 `.gitignore`，排除 `node_modules`、构建输出等不需要理解的文件。

### 3.3 图片输入

直接粘贴截图可用于视觉 Bug 修复（CSS/布局问题）。

### 3.4 调整输出限制

通过环境变量 `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000` 调整输出限制，默认 32K，可提升至 64K。

### 3.5 Hooks 自动化配置

Hooks 允许在特定事件发生时自动执行 shell 命令，实现格式化代码、发送通知、验证操作等。

**触发时机**：

| 触发时机 | 说明 | 使用场景 |
|----------|------|----------|
| `PostToolUse` | 工具使用后执行 | 自动格式化代码 |
| `PreToolUse` | 工具使用前执行 | 检查环境条件 |
| `Notification` | 需要用户输入时 | 发送桌面通知 |
| `Stop` | 会话结束时 | 最终验证 |

**配置示例**（自动格式化）：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

这意味着每当 Claude Code 使用 Edit 或 Write 工具修改文件后，自动运行 Prettier 格式化代码。

---

## 四、理解新代码库

进入项目根目录后启动 Claude Code，请求代码库概况：

```
give me an overview of this codebase
```

进一步了解特定组件：

```
explain main architecture patterns used here
what are key data models?
how is authentication handled?
```

查找相关代码：

```
查找处理用户认证的文件
这些认证文件是如何协同工作的？
从前端到数据库，跟踪登录过程
```

高效修复 Bug：直接提供错误信息让 Claude 分析原因并修复。

---

# 第三章 高级功能

## 一、进阶提示技巧

### 1.1 提示词结构建议

采用清晰的任务框定方式，明确告诉 Claude 具体要做什么，永远把最重要的要求放在提示词最顶部。有效的提示词结构为：`[角色] + [任务] + [上下文]`。

### 1.2 给 Claude 自检的方法

提供测试、截图或期望输出，让 Claude 能够验证自己是否做对。

### 1.3 假设零上下文

假设 Claude 对你的项目一无所知，把它"需要知道的一切"讲清楚。

### 1.4 富上下文

使用 `@` 符号链接文件、数据和图片，让 Claude 获得更丰富的上下文信息。

### 1.5 先探索，再规划，再编码

对于复杂任务，建议先让 Claude 调研，然后进入 Plan 模式，最后回到普通模式执行代码。

### 1.6 高频效率技巧

- `/init` 命令：让 Claude 给自己写入职文档，每次打开新项目都运行
- Plan 模式：使用 Plan 模式让 Claude 先想清楚要做什么
- Subagents 并行协作：让多个 AI 专家并行工作
- 明确指示 AI"深入思考"：对于复杂问题，明确要求"请深度思考此问题"
- 善用消息编辑：连续按两次 Esc 可跳转并分叉历史消息

### 1.7 项目级指令

用项目级指令定义长期行为，通过 CLAUDE.md 和子代理来建立持久的工作规范。

---

## 二、MCP 集成

### 2.1 什么是 MCP

MCP（Model Context Protocol）是 Anthropic 在 2025 年推出的开源标准协议，旨在连接 AI 助手与各种数据源系统。

架构组成：
- **Host（主机）**：运行 MCP 客户端的应用程序
- **MCP Client（客户端）**：集成在主机应用内
- **MCP Server（服务器）**：独立服务程序，专注于特定集成点
- **外部工具与 API**：实际功能和数据源

Claude Code 既充当 MCP 客户端，也可作为 MCP 服务器运行。

### 2.2 MCP 集成方式

**项目配置方式**（`.mcp.json`）：

```json
{
  "servers": {
    "puppeteer": {
      "command": "uvx",
      "args": ["mcp-server-puppeteer"]
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"]
    }
  }
}
```

**全局配置方式**：`claude --mcp-config global`

**直接指定方式**：`claude --mcp-server puppeteer://localhost:3000`

### 2.3 常用 MCP 服务器

**数据库类**：Database-MCP（支持 SQL Server、MySQL、PostgreSQL）

**开发工具**：GitHub-MCP、GitLab-MCP、Docker、Sentry-MCP

**浏览器自动化**：Puppeteer-MCP

**搜索**：Brave Search、Exa

**设计与 UI 类**：
- Figma-MCP：让 Claude 可以直接读取 Figma 设计稿，生成 1:1 还原的前端代码
- BlenderMCP：让 Claude 可以控制 Blender 进行 3D 建模

### 2.4 MCP 配置示例

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres",
               "postgresql://localhost:5432/mydb"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_..." }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

---

## 三、Subagents 子代理

### 3.1 子代理并行化

Claude Code 可生成并行子代理，同时处理独立任务。

**显式请求并行**：

```
请并行执行以下三个任务：
1. 为 auth 模块添加单元测试
2. 更新 README 中的新 API 端点
3. 修复设置页面的 CSS 对齐问题
```

**自动并行**：描述具有独立组件的任务时，Claude 可能自动使用 Task 工具并行化。

### 3.2 Agent Teams

启用并行代理团队，多个 Claude 实例协调工作：

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

或在 `settings.json` 中：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**工作模式**：
- 一个会话作为团队领导
- 代理通过共享任务列表协调
- 可直接相互发送消息
- 适用于：多角度代码审查、竞争性方案研究、跨文件集并行重构

**注意事项**：
- 先从非代码任务开始（PR 审查、研究、调试假设）
- 两个代理编辑同一文件时，后写入者获胜

---

## 四、Custom Skills 自定义技能

### 4.1 文件结构

通过结构化文档创建领域特定专家。文件结构如下：

```
.skills/
└── your-skill/
    ├── SKILL.md          # 元数据、执行流程、质量门禁
    ├── reference.md      # 领域知识（解释"为什么"）
    └── templates/        # 代码模板、Schema
```

### 4.2 SKILL.md 结构

- Frontmatter（元数据：名称、版本、作者）
- Quick Start（快速开始）
- Execution Flow（执行流程）
- Quality Gates（质量检查点）

### 4.3 最佳实践

- SKILL.md 控制在 500 行以内
- 将知识（reference.md）与指令（SKILL.md）分离
- 通过斜杠命令调用测试

---

# 第四章 最佳实践与生态比较

## 一、经典应用案例

### 1.1 智能代码审查

Claude Code 可作为智能代码审查工具，自动识别代码问题、性能瓶颈和安全漏洞。

**应用场景**：代码审查

**实施方法**：请求审查代码质量，关注代码规范、性能瓶颈、安全漏洞、内存泄漏风险

### 1.2 前端 UI 开发

结合 Figma-MCP，实现设计稿到代码的像素级还原。

**实施方法**：
1. 开启 Figma 的 MCP 服务器
2. 让 Claude Code 连接 Figma MCP
3. 描述想要实现的功能

### 1.3 数据库操作

通过 Database-MCP，用自然语言操作数据库。

**实施方法**：
1. 安装 Database-MCP 并配置数据库连接
2. 让 Claude 理解现有的数据结构和需求
3. 用自然语言描述数据库操作

### 1.4 代码重构

Claude Code 在重构复杂的历史代码方面表现优异。

**实施方法**：
1. 向 Claude 描述重构目标
2. 说明重点注意事项和需要保持一致的命名
3. 让 Claude 自动完成重构

### 1.5 多代理协作

利用 Subagents 功能，建立专门处理特定任务的子代理，并行处理多个相关但独立的任务。

### 1.6 保护敏感文件

使用 PreToolUse Hook 阻止对敏感文件（如 .env、package-lock.json）的修改：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

`protect-files.sh` 脚本检查目标文件路径是否匹配敏感模式，如果匹配则返回错误码阻止操作。

### 1.7 跨项目任务自动化

在企业级配置中创建共享技能，放置在所有项目都能访问的父目录 `.claude/skills/` 下，实现跨项目部署等统一操作。

---

## 二、生态工具对比

### 2.1 Claude Code 生态热门项目

**工作流编排与多代理协作类**：
- **Claude Taskmaster**（20.9k星）：AI 驱动的任务管理 CLI，将 PRD 转化为可执行的开发任务
- **Claude-Flow**（6.7k星）：先进的 AI 编排框架，协调多个 Claude Code 代理以"蜂群"形式处理复杂任务

**工具增强类**：
- **ccusage**：查看 Claude Code 使用量和费用统计
- **Claudia**：将 Claude Code 变回 IDE 体验

### 2.2 Claude Code vs Cursor

| 特性 | Claude Code | Cursor |
|------|-------------|--------|
| 界面 | 终端 | IDE 插件（VS Code） |
| 交互模式 | 纯终端 | 融入 IDE 环境 |
| 上下文理解 | 能理解整个项目架构和业务逻辑 | 相对较浅 |
| 工作流 | 终端完成整个开发流程 | 编辑器和聊天窗口切换 |
| 模型访问 | 完整 Opus 和 Sonnet 模型 | 有时会转换到其他模型 |

### 2.3 Claude Code vs Cline

| 特性 | Claude Code | Cline |
|------|------------|-------|
| 界面 | 终端 | IDE 插件 |
| LLM 连接 | API 密钥/按使用付费 | API 密钥/按使用付费 |
| MCP 支持 | 是 | 是 |
| 生态系统 | 快速发展中 | 成熟 |

### 2.4 claude-hud 插件

社区开发了 claude-hud 插件，可以实时显示上下文使用情况。

```bash
# 添加插件市场
/plugin marketplace add jarrodwatts/claude-hud
# 安装插件
/plugin install claude-hud
# 配置状态栏
/claude-hud:setup
```

安装后，终端底部会显示实时上下文进度条。

### 2.5 选择建议

- **追求极致集成体验**：选择 Cursor 或 Cline
- **追求原生控制力和灵活性**：选择 Claude Code
- **需要复杂任务自动化**：选择 Claude Code 配合 MCP
- **团队协作场景**：根据团队技术栈和习惯选择

---

## 三、最佳实践

### 3.1 Anthropic 官方最佳实践

**核心原则**：
1. **清晰任务框定**：一开始就明确告诉 Claude 具体要做什么
2. **关键指令前置**：永远把最重要的要求放在提示词最顶部
3. **给 Claude 自检的方法**：提供测试、截图或期望输出
4. **假设零上下文**：把 Claude 当作对你的项目一无所知的新人

### 3.2 专业人士私藏技巧

**必会基础**：
- `/init` 命令让 Claude 给自己写入职文档
- 每次打开新项目都运行 /init
- 学会使用 Plan 模式

**效率提升**：
- 使用 Subagents 实现并行协作
- 手动触发而非设计复杂自动化流程
- 针对具体功能设计专属子代理

**进阶控制**：
- 合理管理上下文，50% 左右开始压缩
- 任务越小，Claude 越稳定
- 命令负责入口和交互，代理负责编排流程，技能负责注入领域知识

### 3.3 生产环境建议

**工具链选择**：
- 使用 iTerm 而不是 IDE 内置终端，后者容易崩溃
- 语音输入工具能让效率翻倍
- 用 git worktree 实现并行开发

**调试技巧**：
- 让 Claude 把需要观察日志的终端作为后台任务运行
- 配合 MCP 让 Claude 直接读取浏览器控制台

**代码管理**：
- 完成一个任务就立刻提交代码
- 代码提交的频率应该和呼吸一样自然

### 3.4 使用感悟

根据深度使用者的经验总结：
- 与其设计复杂的自动化流程，不如用命令手动触发
- 与其创建"通用角色"，不如针对具体功能设计专属子代理
- 通用的东西听起来万能，实际上什么都做不好
- 对于小任务，原生 Claude Code 比任何精心设计的工作流都好用
- 用好 AI 编程工具的关键不是找到完美的配置，而是理解它的工作方式，然后顺势而为

---

## 四、总结与展望

Claude Code 作为 Anthropic 官方推出的命令行 AI 编程助手，代表了一种全新的编程范式。它通过终端原生设计、强大的上下文理解能力、灵活的 MCP 扩展机制，为开发者提供了前所未有的编程体验。

从入门到精通需要经历几个阶段：
1. 基础环境搭建和基本命令使用
2. 深入理解 CLAUDE.md 和项目规范
3. 掌握 MCP 集成和高级使用技巧
4. 在实际项目中灵活运用，形成适合自己的工作流程

**核心要点**：
- **上下文是关键**：通过 CLAUDE.md 和规划模式，为 Claude Code 提供清晰的上下文
- **信任与控制并重**：逐步建立信任，但始终通过权限配置保持必要的控制
- **持续学习与实践**：关注官方文档和社区动态，不断尝试新功能

随着生态系统的快速发展，Claude Code 正在成为 AI 编程领域的重要力量。

**记住：最重要的不是找到完美的配置，而是理解工具的工作方式，然后顺势而为。**
