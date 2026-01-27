import { useState } from 'react';
import { Category } from '../types';
import { useTranslation } from '../hooks/useTranslation';
import './TodoInput.css';

interface TodoInputProps {
  onAdd: (text: string, category: Category, deadline: string) => void;
}

export function TodoInput({ onAdd }: TodoInputProps) {
  const { t } = useTranslation();
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
          placeholder={t.input.placeholder}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSubmit()}
        />
        <button className="add-btn" onClick={handleSubmit}>
          {t.input.addButton}
        </button>
      </div>
      <div className="input-row">
        <select
          className="category-select"
          value={category}
          onChange={e => setCategory(e.target.value as Category)}
        >
          <option value="work">{t.input.category.work}</option>
          <option value="personal">{t.input.category.personal}</option>
          <option value="study">{t.input.category.study}</option>
          <option value="other">{t.input.category.other}</option>
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
