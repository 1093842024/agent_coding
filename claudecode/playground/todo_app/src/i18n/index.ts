import { zhCN } from './locales/zh-CN';
import { enUS } from './locales/en-US';

export type Language = 'zh-CN' | 'en-US';

export const translations = {
  'zh-CN': zhCN,
  'en-US': enUS,
};

export const defaultLanguage: Language = 'zh-CN';

// Type for translation object
export type Translations = typeof zhCN;
