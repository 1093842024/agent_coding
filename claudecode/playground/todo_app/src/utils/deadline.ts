export interface DeadlineStatus {
  text: string;
  class: string;
}

export const getDeadlineStatus = (deadline: string): DeadlineStatus => {
  if (!deadline) return { text: '', class: '' };

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const deadlineDate = new Date(deadline);
  deadlineDate.setHours(0, 0, 0, 0);

  const diffTime = deadlineDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: `已过期 ${Math.abs(diffDays)} 天`, class: 'overdue' };
  } else if (diffDays === 0) {
    return { text: '今天到期', class: 'today' };
  } else if (diffDays === 1) {
    return { text: '明天到期', class: 'today' };
  } else {
    return { text: `${diffDays} 天后到期`, class: '' };
  }
};
