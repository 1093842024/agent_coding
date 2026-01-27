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
