# Todo App React + TypeScript + Vite 重构计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 将单文件HTML待办事项应用重构为React + TypeScript + Vite项目，保留所有现有功能且UI风格保持一致

**架构:** 使用Vite作为构建工具，React作为UI框架，TypeScript提供类型安全，自定义hooks管理状态和localStorage持久化

**技术栈:** React 18, TypeScript, Vite, CSS

---

## 任务 1: 初始化 Vite + React + TypeScript 项目

**Files:**
- Create: `package.json`
- Create: `vite.config.ts`
- Create: `tsconfig.json`
- Create: `index.html`
- Create: `tsconfig.node.json`

**Step 1: 创建 package.json**

```json
{
  "name": "todo-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.0",
    "vite": "^5.0.0"
  }
}
```

**Step 2: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

**Step 3: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 4: 创建 tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

**Step 5: 创建 index.html**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>待办事项 - Todo App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 6: 安装依赖**

```bash
npm install
```

**Step 7: Commit**

```bash
git add .
git commit -m "chore: 初始化 Vite + React + TypeScript 项目结构"
```

---

## 任务 2: 创建类型定义和 hooks

**Files:**
- Create: `src/types.ts`
- Create: `src/hooks/useTodos.ts`
- Create: `src/hooks/useFilter.ts`

**Step 1: 创建 src/types.ts**

```typescript
export type Category = 'work' | 'personal' | 'study' | 'other';

export type Filter = 'all' | 'active' | 'completed' | Category;

export interface Todo {
  id: number;
  text: string;
  category: Category;
  deadline: string;
  completed: boolean;
  createdAt: string;
}

export interface TodoStats {
  total: number;
  active: number;
  completed: number;
}
```

**Step 2: 创建 src/hooks/useTodos.ts**

```typescript
import { useState, useEffect } from 'react';
import { Todo } from '../types';

const STORAGE_KEY = 'todos';

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  }, [todos]);

  const addTodo = (text: string, category: string, deadline: string) => {
    const newTodo: Todo = {
      id: Date.now(),
      text,
      category: category as Todo['category'],
      deadline,
      completed: false,
      createdAt: new Date().toISOString(),
    };
    setTodos(prev => [newTodo, ...prev]);
  };

  const toggleTodo = (id: number) => {
    setTodos(prev =>
      prev.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const deleteTodo = (id: number) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  const updateTodo = (id: number, updates: Partial<Todo>) => {
    setTodos(prev =>
      prev.map(todo => (todo.id === id ? { ...todo, ...updates } : todo))
    );
  };

  return { todos, addTodo, toggleTodo, deleteTodo, updateTodo };
}
```

**Step 3: 创建 src/hooks/useFilter.ts**

```typescript
import { useState } from 'react';
import { Filter } from '../types';

export function useFilter() {
  const [filter, setFilter] = useState<Filter>('all');

  return { filter, setFilter };
}
```

**Step 4: Commit**

```bash
git add src/types.ts src/hooks/
git commit -m "feat: 添加类型定义和自定义hooks"
```

---

## 任务 3: 创建工具函数

**Files:**
- Create: `src/utils/category.ts`
- Create: `src/utils/deadline.ts`

**Step 1: 创建 src/utils/category.ts**

```typescript
import { Category } from '../types';

export const categoryLabels: Record<Category, string> = {
  work: '工作',
  personal: '个人',
  study: '学习',
  other: '其他',
};

export const getCategoryLabel = (category: Category): string => {
  return categoryLabels[category] || '其他';
};
```

**Step 2: 创建 src/utils/deadline.ts**

```typescript
export interface DeadlineStatus {
  text: string;
  class: string;
}

export const getDeadlineStatus = (deadline: string): DeadlineStatus => {
  if (!deadline) return { text: '', class: '' };

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const deadlineDate = new Date(deadline);
  deadlineDate.setHours(0, 0, 0, 0);

  const diffTime = deadlineDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: `已过期 ${Math.abs(diffDays)} 天`, class: 'overdue' };
  } else if (diffDays === 0) {
    return { text: '今天到期', class: 'today' };
  } else if (diffDays === 1) {
    return { text: '明天到期', class: 'today' };
  } else {
    return { text: `${diffDays} 天后到期`, class: '' };
  }
};
```

**Step 3: Commit**

```bash
git add src/utils/
git commit -m "feat: 添加工具函数"
```

---

## 任务 4: 创建组件 - TodoInput

**Files:**
- Create: `src/components/TodoInput.tsx`
- Create: `src/components/TodoInput.css`

**Step 1: 创建 src/components/TodoInput.css**

```css
.input-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 30px;
}

.input-row {
  display: flex;
  gap: 10px;
}

.todo-input {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  outline: none;
}

.todo-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.add-btn {
  padding: 15px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.category-select, .deadline-input {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
  background: white;
}

.category-select:focus, .deadline-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.deadline-input {
  width: 150px;
}

.category-select {
  width: 120px;
}
```

**Step 2: 创建 src/components/TodoInput.tsx**

```typescript
import { useState } from 'react';
import { Category } from '../types';
import './TodoInput.css';

interface TodoInputProps {
  onAdd: (text: string, category: Category, deadline: string) => void;
}

export function TodoInput({ onAdd }: TodoInputProps) {
  const [text, setText] = useState('');
  const [category, setCategory] = useState<Category>('work');
  const [deadline, setDeadline] = useState('');

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onAdd(trimmed, category, deadline);
    setText('');
    setDeadline('');
  };

  return (
    <div className="input-container">
      <div className="input-row">
        <input
          type="text"
          className="todo-input"
          placeholder="添加新的待办事项..."
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSubmit()}
        />
        <button className="add-btn" onClick={handleSubmit}>
          添加
        </button>
      </div>
      <div className="input-row">
        <select
          className="category-select"
          value={category}
          onChange={e => setCategory(e.target.value as Category)}
        >
          <option value="work">工作</option>
          <option value="personal">个人</option>
          <option value="study">学习</option>
          <option value="other">其他</option>
        </select>
        <input
          type="date"
          className="deadline-input"
          value={deadline}
          onChange={e => setDeadline(e.target.value)}
        />
      </div>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add src/components/TodoInput.tsx src/components/TodoInput.css
git commit -m "feat: 创建 TodoInput 组件"
```

---

## 任务 5: 创建组件 - TodoItem

**Files:**
- Create: `src/components/TodoItem.tsx`
- Create: `src/components/TodoItem.css`

**Step 1: 创建 src/components/TodoItem.css**

```css
.todo-item {
  background: white;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.todo-item:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.todo-checkbox {
  width: 24px;
  height: 24px;
  border: 2px solid #cbd5e0;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.todo-checkbox.checked {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
}

.todo-checkbox.checked::after {
  content: '✓';
  color: white;
  font-size: 16px;
  font-weight: bold;
}

.todo-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-main {
  display: flex;
  align-items: center;
  gap: 15px;
}

.todo-text {
  flex: 1;
  font-size: 16px;
  color: #2d3748;
  transition: all 0.3s ease;
}

.todo-text.completed {
  text-decoration: line-through;
  color: #a0aec0;
}

.todo-actions {
  display: flex;
  gap: 10px;
}

.todo-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.edit-btn {
  background: #4299e1;
  color: white;
}

.edit-btn:hover {
  background: #3182ce;
  transform: translateY(-1px);
}

.delete-btn {
  background: #f56565;
  color: white;
}

.delete-btn:hover {
  background: #e53e3e;
  transform: translateY(-1px);
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #718096;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.category-work {
  background: #ebf8ff;
  color: #3182ce;
}

.category-personal {
  background: #f0fff4;
  color: #38a169;
}

.category-study {
  background: #faf5ff;
  color: #805ad5;
}

.category-other {
  background: #fffaf0;
  color: #dd6b20;
}

.deadline {
  display: flex;
  align-items: center;
  gap: 4px;
}

.deadline.overdue {
  color: #e53e3e;
  font-weight: 500;
}

.deadline.today {
  color: #dd6b20;
  font-weight: 500;
}

/* 编辑模式 */
.todo-item.editing .todo-main,
.todo-item.editing .todo-meta {
  display: none;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.edit-meta {
  display: flex;
  gap: 10px;
}

.edit-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #667eea;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
}

.edit-deadline {
  padding: 8px 12px;
  border: 2px solid #667eea;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.save-btn {
  background: #48bb78;
  color: white;
}

.save-btn:hover {
  background: #38a169;
}

.cancel-btn {
  background: #a0aec0;
  color: white;
}

.cancel-btn:hover {
  background: #718096;
}
```

**Step 2: 创建 src/components/TodoItem.tsx**

```typescript
import { useState } from 'react';
import { Todo, Category } from '../types';
import { getCategoryLabel } from '../utils/category';
import { getDeadlineStatus } from '../utils/deadline';
import './TodoItem.css';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
  onUpdate: (id: number, updates: Partial<Todo>) => void;
}

export function TodoItem({ todo, onToggle, onDelete, onUpdate }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);
  const [editCategory, setEditCategory] = useState<Category>(todo.category);
  const [editDeadline, setEditDeadline] = useState(todo.deadline);

  const categoryLabel = getCategoryLabel(todo.category);
  const deadlineStatus = getDeadlineStatus(todo.deadline);

  const handleSave = () => {
    const trimmed = editText.trim();
    if (!trimmed) return;
    onUpdate(todo.id, {
      text: trimmed,
      category: editCategory,
      deadline: editDeadline,
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditText(todo.text);
    setEditCategory(todo.category);
    setEditDeadline(todo.deadline);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <li className="todo-item editing" data-id={todo.id}>
        <div className={`todo-checkbox ${todo.completed ? 'checked' : ''}`}
             onClick={() => onToggle(todo.id)} />
        <div className="todo-content">
          <div className="edit-form">
            <input
              type="text"
              className="edit-input"
              value={editText}
              onChange={e => setEditText(e.target.value)}
              autoFocus
            />
            <div className="edit-meta">
              <select
                className="category-select"
                value={editCategory}
                onChange={e => setEditCategory(e.target.value as Category)}
              >
                <option value="work">工作</option>
                <option value="personal">个人</option>
                <option value="study">学习</option>
                <option value="other">其他</option>
              </select>
              <input
                type="date"
                className="edit-deadline"
                value={editDeadline}
                onChange={e => setEditDeadline(e.target.value)}
              />
            </div>
            <div className="edit-actions">
              <button className="todo-btn save-btn" onClick={handleSave}>保存</button>
              <button className="todo-btn cancel-btn" onClick={handleCancel}>取消</button>
            </div>
          </div>
        </div>
      </li>
    );
  }

  return (
    <li className="todo-item" data-id={todo.id}>
      <div className={`todo-checkbox ${todo.completed ? 'checked' : ''}`}
           onClick={() => onToggle(todo.id)} />
      <div className="todo-content">
        <div className="todo-main">
          <span className={`todo-text ${todo.completed ? 'completed' : ''}`}>
            {todo.text}
          </span>
          <div className="todo-actions">
            <button className="todo-btn edit-btn" onClick={() => setIsEditing(true)}>编辑</button>
            <button className="todo-btn delete-btn" onClick={() => onDelete(todo.id)}>删除</button>
          </div>
        </div>
        <div className="todo-meta">
          <span className={`category-badge category-${todo.category}`}>
            {categoryLabel}
          </span>
          {todo.deadline && (
            <span className={`deadline ${deadlineStatus.class}`}>
              📅 {deadlineStatus.text}
            </span>
          )}
        </div>
      </div>
    </li>
  );
}
```

**Step 3: Commit**

```bash
git add src/components/TodoItem.tsx src/components/TodoItem.css
git commit -m "feat: 创建 TodoItem 组件"
```

---

## 任务 6: 创建组件 - FilterButtons 和 Stats

**Files:**
- Create: `src/components/FilterButtons.tsx`
- Create: `src/components/FilterButtons.css`
- Create: `src/components/Stats.tsx`
- Create: `src/components/Stats.css`

**Step 1: 创建 src/components/FilterButtons.css**

```css
.filter-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #4a5568;
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.filter-separator {
  margin: 0 10px;
  color: #e2e8f0;
  display: flex;
  align-items: center;
}
```

**Step 2: 创建 src/components/FilterButtons.tsx**

```typescript
import { Filter } from '../types';
import './FilterButtons.css';

interface FilterButtonsProps {
  currentFilter: Filter;
  onFilterChange: (filter: Filter) => void;
}

export function FilterButtons({ currentFilter, onFilterChange }: FilterButtonsProps) {
  const filters: { value: Filter; label: string }[] = [
    { value: 'all', label: '全部' },
    { value: 'active', label: '未完成' },
    { value: 'completed', label: '已完成' },
  ];

  const categories = [
    { value: 'work', label: '工作' },
    { value: 'personal', label: '个人' },
    { value: 'study', label: '学习' },
    { value: 'other', label: '其他' },
  ];

  return (
    <div className="filter-container">
      {filters.map(filter => (
        <button
          key={filter.value}
          className={`filter-btn ${currentFilter === filter.value ? 'active' : ''}`}
          onClick={() => onFilterChange(filter.value)}
        >
          {filter.label}
        </button>
      ))}
      <span className="filter-separator">|</span>
      {categories.map(cat => (
        <button
          key={cat.value}
          className={`filter-btn ${currentFilter === cat.value ? 'active' : ''}`}
          onClick={() => onFilterChange(cat.value)}
        >
          {cat.label}
        </button>
      ))}
    </div>
  );
}
```

**Step 3: 创建 src/components/Stats.css**

```css
.stats {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #718096;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  display: block;
}
```

**Step 4: 创建 src/components/Stats.tsx**

```typescript
import { TodoStats } from '../types';
import './Stats.css';

interface StatsProps {
  stats: TodoStats;
}

export function Stats({ stats }: StatsProps) {
  return (
    <div className="stats">
      <div className="stat-item">
        <span className="stat-number">{stats.total}</span>
        <span>总计</span>
      </div>
      <div className="stat-item">
        <span className="stat-number">{stats.active}</span>
        <span>未完成</span>
      </div>
      <div className="stat-item">
        <span className="stat-number">{stats.completed}</span>
        <span>已完成</span>
      </div>
    </div>
  );
}
```

**Step 5: Commit**

```bash
git add src/components/FilterButtons.tsx src/components/FilterButtons.css
git add src/components/Stats.tsx src/components/Stats.css
git commit -m "feat: 创建 FilterButtons 和 Stats 组件"
```

---

## 任务 7: 创建组件 - TodoList 和 EmptyState

**Files:**
- Create: `src/components/TodoList.tsx`
- Create: `src/components/TodoList.css`
- Create: `src/components/EmptyState.tsx`
- Create: `src/components/EmptyState.css`

**Step 1: 创建 src/components/EmptyState.css**

```css
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #a0aec0;
}

.empty-state-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state-text {
  font-size: 18px;
  margin-bottom: 10px;
}

.empty-state-hint {
  font-size: 14px;
  opacity: 0.7;
}
```

**Step 2: 创建 src/components/EmptyState.tsx**

```typescript
import './EmptyState.css';

export function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">📝</div>
      <div className="empty-state-text">暂无待办事项</div>
      <div className="empty-state-hint">添加一个新任务开始吧！</div>
    </div>
  );
}
```

**Step 3: 创建 src/components/TodoList.css**

```css
.todo-list {
  list-style: none;
  max-height: 400px;
  overflow-y: auto;
}

.todo-list::-webkit-scrollbar {
  width: 6px;
}

.todo-list::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.todo-list::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.todo-list::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
```

**Step 4: 创建 src/components/TodoList.tsx**

```typescript
import { Todo } from '../types';
import { TodoItem } from './TodoItem';
import { EmptyState } from './EmptyState';
import './TodoList.css';

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
  onUpdate: (id: number, updates: Partial<Todo>) => void;
}

export function TodoList({ todos, onToggle, onDelete, onUpdate }: TodoListProps) {
  if (todos.length === 0) {
    return <EmptyState />;
  }

  return (
    <ul className="todo-list">
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onUpdate={onUpdate}
        />
      ))}
    </ul>
  );
}
```

**Step 5: Commit**

```bash
git add src/components/TodoList.tsx src/components/TodoList.css
git add src/components/EmptyState.tsx src/components/EmptyState.css
git commit -m "feat: 创建 TodoList 和 EmptyState 组件"
```

---

## 任务 8: 创建主 App 组件

**Files:**
- Create: `src/App.tsx`
- Create: `src/App.css`

**Step 1: 创建 src/App.css**

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  margin: 0;
}

.app-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  padding: 40px;
  backdrop-filter: blur(10px);
}

.app-title {
  color: #2d3748;
  text-align: center;
  margin-bottom: 30px;
  font-size: 32px;
  font-weight: 700;
}
```

**Step 2: 创建 src/App.tsx**

```typescript
import { useMemo } from 'react';
import { Todo, Filter } from '../types';
import { TodoInput } from './components/TodoInput';
import { TodoList } from './components/TodoList';
import { FilterButtons } from './components/FilterButtons';
import { Stats } from './components/Stats';
import { useTodos } from './hooks/useTodos';
import { useFilter } from './hooks/useFilter';
import './App.css';

function App() {
  const { todos, addTodo, toggleTodo, deleteTodo, updateTodo } = useTodos();
  const { filter, setFilter } = useFilter();

  const filteredTodos = useMemo(() => {
    let result = todos;

    switch (filter) {
      case 'active':
        result = result.filter(t => !t.completed);
        break;
      case 'completed':
        result = result.filter(t => t.completed);
        break;
      case 'work':
      case 'personal':
      case 'study':
      case 'other':
        result = result.filter(t => t.category === filter);
        break;
    }

    return result;
  }, [todos, filter]);

  const stats = useMemo(() => ({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length,
  }), [todos]);

  return (
    <div className="app-container">
      <h1 className="app-title">我的待办事项</h1>

      <TodoInput onAdd={addTodo} />

      <FilterButtons currentFilter={filter} onFilterChange={setFilter} />

      <TodoList
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
        onUpdate={updateTodo}
      />

      <Stats stats={stats} />
    </div>
  );
}

export default App;
```

**Step 3: Commit**

```bash
git add src/App.tsx src/App.css
git commit -m "feat: 创建主 App 组件"
```

---

## 任务 9: 创建入口文件

**Files:**
- Create: `src/main.tsx`
- Create: `src/index.css`
- Create: `src/vite-env.d.ts`

**Step 1: 创建 src/main.tsx**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Step 2: 创建 src/index.css**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

**Step 3: 创建 src/vite-env.d.ts**

```typescript
/// <reference types="vite/client" />
```

**Step 4: Commit**

```bash
git add src/main.tsx src/index.css src/vite-env.d.ts
git commit -m "feat: 添加入口文件"
```

---

## 任务 10: 更新 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: 更新 CLAUDE.md**

```markdown
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
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: 更新 CLAUDE.md"
```

---

## 任务 11: 测试构建

**Step 1: 运行构建**

```bash
npm run build
```

Expected: Build successful with no TypeScript errors

**Step 2: Commit**

```bash
git add .
git commit -m "chore: 完成 React + TypeScript + Vite 重构"
```
