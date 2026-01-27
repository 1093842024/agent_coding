# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在操作本仓库代码时的指导。

## 项目概述

这是一个基于 React + TypeScript + Vite 构建的待办事项应用。应用使用中文编写，提供完整的待办事项管理系统，并支持本地存储持久化。

## 架构

使用 Vite 作为构建工具，React 18 作为 UI 框架，TypeScript 提供类型安全，自定义 hooks 管理状态：

- **src/components/** - React 组件
- **src/hooks/** - 自定义 hooks (useTodos, useFilter)
- **src/utils/** - 工具函数
- **src/types.ts** - TypeScript 类型定义

## 关键组件

### App.tsx
主应用组件，协调所有子组件和状态管理。

### TodoInput.tsx
待办事项输入组件，包含文本输入、分类选择和截止日期选择。

### TodoItem.tsx
单个待办事项组件，支持展示、编辑、切换状态和删除。

### TodoList.tsx
待办事项列表组件，渲染所有待办事项或空状态。

### FilterButtons.tsx
筛选按钮组件，支持按状态和分类筛选。

### Stats.tsx
统计组件，显示总数、未完成数和已完成数。

## 类型定义 (src/types.ts)

```typescript
type Category = 'work' | 'personal' | 'study' | 'other';
type Filter = 'all' | 'active' | 'completed' | Category;

interface Todo {
  id: number;
  text: string;
  category: Category;
  deadline: string;
  completed: boolean;
  createdAt: string;
}
```

## 开发命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 语言
应用界面为中文（zh-CN）。
