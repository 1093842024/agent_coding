import { useTranslation } from '../hooks/useTranslation';
import './LanguageToggle.css';

export function LanguageToggle() {
  const { toggleLanguage, language } = useTranslation();

  return (
    <div className="language-toggle">
      <button className="language-btn" onClick={toggleLanguage}>
        {language === 'zh-CN' ? 'English' : '中文'}
      </button>
    </div>
  );
}
