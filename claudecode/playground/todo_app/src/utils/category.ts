import { Category } from '../types';
import { Translations } from '../i18n';

export const categoryLabels = (t: Translations['input']['category']) => ({
  work: t.work,
  personal: t.personal,
  study: t.study,
  other: t.other,
});

export const getCategoryLabel = (category: Category, labels: Record<Category, string>): string => {
  return labels[category] || '其他';
};
