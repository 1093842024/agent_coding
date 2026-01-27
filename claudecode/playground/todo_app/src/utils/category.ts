import { Category } from '../types';

export const categoryLabels: Record<Category, string> = {
  work: '工作',
  personal: '个人',
  study: '学习',
  other: '其他',
};

export const getCategoryLabel = (category: Category): string => {
  return categoryLabels[category] || '其他';
};
