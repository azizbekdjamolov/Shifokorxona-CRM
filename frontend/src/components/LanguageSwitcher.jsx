import { useTranslation } from "react-i18next";

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const changeLanguage = (lang) => i18n.changeLanguage(lang);

  return (
    <div className="language-switcher">
      {["uz", "ru", "en"].map((lang) => (
        <button
          key={lang}
          className={i18n.language === lang ? "lang-btn lang-btn-active" : "lang-btn"}
          onClick={() => changeLanguage(lang)}
        >
          {lang.toUpperCase()}
        </button>
      ))}
    </div>
  );
}