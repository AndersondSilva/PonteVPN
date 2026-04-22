"use client";
import Link from "next/link";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Hero() {
  const { t } = useLanguage();

  return (
    <section className="min-h-screen flex flex-col items-center justify-center text-center px-4 pt-16"
      style={{ background: "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,184,107,.08) 0%, transparent 70%)" }}>
      <div className="mb-6 inline-flex items-center gap-2 bg-brand-green/10 border border-brand-green/30 text-brand-green text-sm font-medium px-4 py-2 rounded-full">
        <span className="w-2 h-2 bg-brand-green rounded-full animate-pulse" />
        {t.hero.badge}
      </div>

      <h1 className="text-4xl md:text-6xl font-extrabold leading-tight max-w-4xl tracking-tight">
        {t.hero.title1}{" "}
        <span className="text-brand-green">{t.hero.title2}</span>
        <br />{t.hero.title3}
      </h1>

      <p className="mt-6 text-lg md:text-xl text-white/60 max-w-2xl">{t.hero.sub}</p>

      <div className="mt-10 flex flex-col sm:flex-row gap-4">
        <Link href="/auth/register" className="btn-primary text-base px-8 py-4">{t.hero.ctaPrimary}</Link>
        <Link href="#pricing" className="btn-outline text-base px-8 py-4">{t.hero.ctaSecondary}</Link>
      </div>

      <div className="mt-12 flex flex-wrap justify-center gap-8 text-sm text-white/50">
        {[t.hero.trust1, t.hero.trust2, t.hero.trust3, t.hero.trust4].map((item) => (
          <div key={item} className="flex items-center gap-2">
            <span className="text-brand-green">✦</span> {item}
          </div>
        ))}
      </div>

      <div className="mt-16 flex items-center gap-6 text-3xl flex-wrap justify-center">
        {["🇧🇷", "🇩🇪", "🇳🇱", "🇺🇸", "🇵🇹", "🇬🇧"].map((flag) => (
          <span key={flag} className="hover:scale-125 transition-transform cursor-default">{flag}</span>
        ))}
        <span className="text-base text-white/40">+ more soon</span>
      </div>
    </section>
  );
}
