# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在操作本仓库代码时的指导。

## 项目概述

这是一个单文件 HTML 待办事项应用，包含内嵌的 CSS 和 JavaScript。应用使用中文编写，提供完整的待办事项管理系统，并支持本地存储持久化。

## 架构

整个应用包含在一个单独的 HTML 文件 (`todo-app.html`) 中：
- **HTML 结构**：包含输入框、筛选按钮、待办事项列表和统计信息的容器
- **CSS 样式**：现代渐变背景、玻璃态效果和响应式设计
- **JavaScript 逻辑**：`TodoApp` 类管理应用状态和交互

## 关键组件

### TodoApp 类（第 345-590 行）
主应用类，处理以下功能：
- 待办事项的 CRUD 操作（添加、编辑、删除、切换状态）
- 分类功能（工作、个人、学习、其他）
- 截止时间管理
- 筛选功能（全部、未完成、已完成、按分类筛选）
- 本地存储持久化
- UI 更新和事件处理
- 编辑模式支持修改分类和截止时间

### 数据结构
待办事项以对象形式存储：
```javascript
{
    id: number,
    text: string,
    category: string,        // 分类：work、personal、study、other
    deadline: string,        // 截止时间：YYYY-MM-DD 格式
    completed: boolean,
    createdAt: Date
}
```

### 存储
使用浏览器的 localStorage，键名为 'todos' 进行持久化存储。

## 开发说明

由于这是单 HTML 文件应用：
- 无需构建过程
- 无包管理器依赖
- 直接在浏览器中打开 `todo-app.html` 即可测试
- 可使用浏览器控制台调试 JavaScript

## 语言
应用界面为中文（zh-CN）。