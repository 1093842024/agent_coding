import { useTranslation } from '../hooks/useTranslation';
import './EmptyState.css';

export function EmptyState() {
  const { t } = useTranslation();

  return (
    <div className="empty-state">
      <div className="empty-state-icon"></div>
      <div className="empty-state-text">{t.empty.title}</div>
      <div className="empty-state-hint">{t.empty.hint}</div>
    </div>
  );
}
