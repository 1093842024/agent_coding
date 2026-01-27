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

  const categories: { value: Filter; label: string }[] = [
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
