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
