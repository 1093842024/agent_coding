import { Filter } from '../types';
import { useTranslation } from '../hooks/useTranslation';
import './FilterButtons.css';

interface FilterButtonsProps {
  currentFilter: Filter;
  onFilterChange: (filter: Filter) => void;
}

export function FilterButtons({ currentFilter, onFilterChange }: FilterButtonsProps) {
  const { t } = useTranslation();

  const filters: { value: Filter; label: string }[] = [
    { value: 'all', label: t.filter.all },
    { value: 'active', label: t.filter.active },
    { value: 'completed', label: t.filter.completed },
  ];

  const categories: { value: Filter; label: string }[] = [
    { value: 'work', label: t.input.category.work },
    { value: 'personal', label: t.input.category.personal },
    { value: 'study', label: t.input.category.study },
    { value: 'other', label: t.input.category.other },
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
