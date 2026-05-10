"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type Currency = "BRL" | "EUR";

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (c: Currency) => void;
  symbol: string;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currency, setCurrency] = useState<Currency>("BRL");

  useEffect(() => {
    // Tentar detectar automaticamente (simplificado) ou buscar do localStorage
    const saved = localStorage.getItem("preferred_currency") as Currency;
    if (saved) {
      setCurrency(saved);
    } else {
      // Detecção básica por fuso horário ou idioma do browser
      const locale = navigator.language;
      if (locale.includes("PT") || locale.includes("BR")) {
        setCurrency("BRL");
      } else {
        setCurrency("EUR");
      }
    }
  }, []);

  const handleSetCurrency = (c: Currency) => {
    setCurrency(c);
    localStorage.setItem("preferred_currency", c);
  };

  const symbol = currency === "BRL" ? "R$" : "€";

  return (
    <CurrencyContext.Provider value={{ currency, setCurrency: handleSetCurrency, symbol }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) throw new Error("useCurrency must be used within a CurrencyProvider");
  return context;
};
