import { TodoStats } from '../types';
import { useTranslation } from '../hooks/useTranslation';
import './Stats.css';

interface StatsProps {
  stats: TodoStats;
}

export function Stats({ stats }: StatsProps) {
  const { t } = useTranslation();

  return (
    <div className="stats">
      <div className="stat-item">
        <span className="stat-number">{stats.total}</span>
        <span>{t.stats.total}</span>
      </div>
      <div className="stat-item">
        <span className="stat-number">{stats.active}</span>
        <span>{t.stats.active}</span>
      </div>
      <div className="stat-item">
        <span className="stat-number">{stats.completed}</span>
        <span>{t.stats.completed}</span>
      </div>
    </div>
  );
}
