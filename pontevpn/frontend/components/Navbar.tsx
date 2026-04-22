"use client";
import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { t, locale, setLocale } = useLanguage();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-brand-dark/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <span>🌉</span>
          <span>Ponte<span className="text-brand-green">VPN</span></span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-8 text-sm text-white/70">
          <Link href="#features" className="hover:text-white transition-colors">{t.nav.features}</Link>
          <Link href="#servers" className="hover:text-white transition-colors">{t.nav.servers}</Link>
          <Link href="#pricing" className="hover:text-white transition-colors">{t.nav.pricing}</Link>
          <Link href="#faq" className="hover:text-white transition-colors">{t.nav.faq}</Link>
        </div>

        <div className="hidden md:flex items-center gap-3">
          {/* Language toggle */}
          <button
            onClick={() => setLocale(locale === "pt" ? "en" : "pt")}
            className="flex items-center gap-1.5 text-xs font-semibold text-white/50 hover:text-white border border-white/10 hover:border-white/30 px-3 py-1.5 rounded-lg transition-all"
          >
            <span>{locale === "pt" ? "🇬🇧" : "🇧🇷"}</span>
            <span>{locale === "pt" ? "EN" : "PT"}</span>
          </button>
          <Link href="/auth/login" className="btn-outline py-2 px-4 text-sm">{t.nav.login}</Link>
          <Link href="/auth/register" className="btn-primary py-2 px-4 text-sm">{t.nav.cta}</Link>
        </div>

        <button className="md:hidden p-2" onClick={() => setOpen(!open)}>
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-brand-card border-t border-white/10 px-4 py-4 flex flex-col gap-4">
          <Link href="#features" className="text-white/70 hover:text-white" onClick={() => setOpen(false)}>{t.nav.features}</Link>
          <Link href="#servers" className="text-white/70 hover:text-white" onClick={() => setOpen(false)}>{t.nav.servers}</Link>
          <Link href="#pricing" className="text-white/70 hover:text-white" onClick={() => setOpen(false)}>{t.nav.pricing}</Link>
          <Link href="#faq" className="text-white/70 hover:text-white" onClick={() => setOpen(false)}>{t.nav.faq}</Link>
          <hr className="border-white/10" />
          <button onClick={() => setLocale(locale === "pt" ? "en" : "pt")} className="text-left text-sm text-white/50">
            {locale === "pt" ? "🇬🇧 Switch to English" : "🇧🇷 Mudar para Português"}
          </button>
          <Link href="/auth/login" className="btn-outline text-center text-sm">{t.nav.login}</Link>
          <Link href="/auth/register" className="btn-primary text-center text-sm">{t.nav.cta}</Link>
        </div>
      )}
    </nav>
  );
}
