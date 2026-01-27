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
