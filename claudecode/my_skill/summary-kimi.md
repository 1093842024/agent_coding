基于最新的官方文档和社区实践，我为你整理了一份完整的 Claude Code 学习路径指南。Claude Code 是 Anthropic 推出的终端原生 AI 编程助手，它直接操作本地文件系统，通过自然语言对话完成代码编写、重构、测试等任务。

---

## 一、入门阶段：环境搭建与基础认知

### 1. 安装与配置

**前置要求**：
- Claude 订阅（Pro/Max/Teams/Enterprise）或 Console API 账户
- Node.js 18+（如使用 NPM 安装）
- macOS、Linux、Windows 或 WSL

**安装方式**（四选一）：

| 方式 | 命令/方法 | 适用场景 |
|------|-----------|----------|
| **原生安装** | 官方安装包 | 大多数用户 |
| **Homebrew** | `brew install claude-code` | macOS 用户 |
| **NPM** | `npm install -g @anthropic-ai/claude-code` | Node.js 开发者 |
| **手动安装** | 下载二进制文件 | 企业/自定义环境 |

**验证安装**：
```bash
claude --version
```

### 2. 首次会话与核心概念

启动 Claude Code：
```bash
claude
# 或使用免确认模式（谨慎使用）
claude --dangerously-skip-permissions
```

**关键概念**：
- **Agentic Search**：Claude 自动扫描、映射整个项目，无需手动选择文件
- **权限系统**：每次文件修改和命令执行都需要你的批准
- **上下文窗口**：标准 200K，Opus 4.6 支持 1M token（Beta）

### 3. 必学斜杠命令（Slash Commands）

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

---

## 二、熟练阶段：工作流与配置优化

### 1. CLAUDE.md —— 项目上下文配置

`CLAUDE.md` 是放在项目根目录的"系统提示"，定义项目边界、约束和风格。

**生成初始文件**：
```bash
/init
```

**最佳实践**：
- **全局配置**：在 `~/.claude/claude.md` 放置团队共识（术语、代码风格）
- **局部覆盖**：在子目录放置专属 `claude.md` 覆盖局部行为
- **动态更新**：在对话中用 `#` 开头的指令追加到 `claaude.md`
- **定期重构**：删除空话与过期约束，保留"可执行的、可验证的"规则

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

### 2. Plan Mode（计划模式）

**核心原则**：任何非平凡任务前先规划。

使用方法：
- 输入 `/plan` 进入计划模式
- 或在提示前加 `Plan:` 前缀

Plan Mode 会：
1. 询问澄清问题
2. 提出执行计划
3. 等待你批准或修改
4. 执行计划

**适用场景**：
- 多文件变更（操作顺序重要）
- 重构任务（需理解影响范围）
- 涉及认证、支付、数据迁移的功能

### 3. Hooks 自动化配置

在 `.claude/settings.json` 中配置 Hooks，实现自动化检查：

```json
{
  "hooks": {
    "PreCommit": [
      "npm run lint",
      "npm run test -- --changed"
    ],
    "PostFileWrite": [
      "prettier --write $FILE",
      "black $FILE"
    ]
  }
}
```

**PreCommit**：提交前运行，失败则阻止提交
**PostFileWrite**：文件写入后运行，用于格式化

### 4. 上下文管理技巧

| 技巧 | 命令/方法 | 说明 |
|------|-----------|------|
| 压缩对话 | `/compact` | 长对话后主动压缩，保留关键信息 |
| 排除文件 | `.claudeignore` | 类似 `.gitignore`，排除 `node_modules`、构建输出等 |
| 图片输入 | 直接粘贴截图 | 用于视觉 Bug 修复（CSS/布局问题） |
| 调整输出限制 | `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000` | 默认 32K，可提升至 64K（Sonnet 4.5+） |

---

## 三、专家精通阶段：高级功能与架构

### 1. MCP（Model Context Protocol）服务器

MCP 服务器扩展 Claude Code 能力，使其能查询数据库、搜索网络、管理 Docker、操作 GitHub 等。

**配置示例**（`.claude/settings.json`）：
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

**常用 MCP 服务器**：
- **数据库**：PostgreSQL、SQLite、MySQL
- **开发工具**：GitHub、GitLab、Docker
- **浏览器**：Puppeteer（网页抓取、自动化测试）
- **搜索**：Brave Search、Exa

### 2. Subagents（子代理并行化）

Claude Code 可生成并行子代理，同时处理独立任务。

**显式请求并行**：
```
请并行执行以下三个任务：
1. 为 auth 模块添加单元测试
2. 更新 README 中的新 API 端点
3. 修复设置页面的 CSS 对齐问题
```

**自动并行**：描述具有独立组件的任务时，Claude 可能自动使用 Task 工具并行化。

### 3. Agent Teams（实验性功能）

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
- 两个代理编辑同一文件 = 后写入者获胜

### 4. Custom Skills（自定义技能）

通过结构化文档创建领域特定专家。

**文件结构**：
```
.skills/
└── your-skill/
    ├── SKILL.md          # 元数据、执行流程、质量门禁
    ├── reference.md      # 领域知识（解释"为什么"）
    └── templates/        # 代码模板、Schema
```

**SKILL.md 结构**：
- Frontmatter（元数据：名称、版本、作者）
- Quick Start（快速开始）
- Execution Flow（执行流程）
- Quality Gates（质量检查点）

**最佳实践**：
- SKILL.md 控制在 500 行以内
- 将知识（reference.md）与指令（SKILL.md）分离
- 通过斜杠命令调用测试

---

## 四、经典应用案例与配置方法

### 案例 1：新代码库快速上手（Codebase Onboarding）

**场景**：加入新项目，需要快速理解架构

**工作流程**：
```bash
# 1. 进入项目目录
cd new-project
claude

# 2. 生成 CLAUDE.md
/init

# 3. 请求高层概览
"请给我这个项目的高层架构概览。主要目录和它们的用途是什么？"

# 4. 理解依赖
"列出项目的关键外部依赖，并简要解释每个的作用"

# 