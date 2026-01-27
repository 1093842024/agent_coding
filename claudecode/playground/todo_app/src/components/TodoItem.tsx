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
