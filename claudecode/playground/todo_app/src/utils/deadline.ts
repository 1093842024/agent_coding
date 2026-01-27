import { Translations } from '../i18n';

export interface DeadlineStatus {
  text: string;
  class: string;
}

export const getDeadlineStatus = (deadline: string, t: Translations['deadline']): DeadlineStatus => {
  if (!deadline) return { text: '', class: '' };

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const deadlineDate = new Date(deadline);
  deadlineDate.setHours(0, 0, 0, 0);

  const diffTime = deadlineDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: t.overdue(Math.abs(diffDays)), class: 'overdue' };
  } else if (diffDays === 0) {
    return { text: t.today, class: 'today' };
  } else if (diffDays === 1) {
    return { text: t.tomorrow, class: 'today' };
  } else {
    return { text: t.inDays(diffDays), class: '' };
  }
};
