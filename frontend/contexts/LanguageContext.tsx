"use client";
import { createContext, useContext, useState, useEffect } from "react";
import { translations, type Locale, type Translations } from "@/lib/translations";

interface LanguageContextType {
  locale: Locale;
  t: Translations;
  setLocale: (l: Locale) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  locale: "pt",
  t: translations.pt,
  setLocale: () => {},
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("pt");

  // Detectar idioma do browser na primeira visita
  useEffect(() => {
    const saved = localStorage.getItem("locale") as Locale | null;
    if (saved) { setLocaleState(saved); return; }
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith("en")) setLocaleState("en");
  }, []);

  function setLocale(l: Locale) {
    setLocaleState(l);
    localStorage.setItem("locale", l);
  }

  return (
    <LanguageContext.Provider value={{ locale, t: translations[locale], setLocale }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLanguage = () => useContext(LanguageContext);
