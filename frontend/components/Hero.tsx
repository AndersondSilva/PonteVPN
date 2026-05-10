"use client";
import Link from "next/link";
import { useLanguage } from "@/contexts/LanguageContext";
import { Shield, Zap, Globe, Lock } from "lucide-react";

export default function Hero() {
  const { t } = useLanguage();

  return (
    <section className="min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24 relative overflow-hidden">
      {/* SOTA Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-brand-green/10 rounded-full blur-[120px] -z-10" />
      <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-brand-gold/5 rounded-full blur-[100px] -z-10" />

      <div className="mb-8 inline-flex items-center gap-3 bg-brand-green/10 border border-brand-green/30 text-brand-green text-xs font-black uppercase tracking-[0.2em] px-5 py-2.5 rounded-full shadow-[0_0_15px_rgba(0,184,107,0.1)]">
        <span className="w-2 h-2 bg-brand-green rounded-full animate-pulse shadow-[0_0_8px_#00b86b]" />
        {t.hero.badge}
      </div>

      <h1 className="text-5xl md:text-8xl font-black leading-[1.1] max-w-5xl tracking-tighter italic uppercase">
        {t.hero.title1}{" "}
        <span className="text-brand-green italic">{t.hero.title2}</span>
        <br />{t.hero.title3}
      </h1>

      <p className="mt-8 text-lg md:text-xl text-white/50 max-w-2xl font-medium leading-relaxed">
        {t.hero.sub}
      </p>

      <div className="mt-12 flex flex-col sm:flex-row gap-5">
        <Link href="/auth/register" className="btn-primary text-base px-10 py-5 flex items-center gap-2">
          <Zap size={18} fill="currentColor" />
          {t.hero.ctaPrimary}
        </Link>
        <Link href="#pricing" className="btn-outline text-base px-10 py-5 glass">
          {t.hero.ctaSecondary}
        </Link>
      </div>

      <div className="mt-16 flex flex-wrap justify-center gap-10 text-[10px] font-black uppercase tracking-[0.3em] text-white/30">
        {[
          { label: t.hero.trust1, icon: <Lock size={12} /> },
          { label: t.hero.trust2, icon: <Shield size={12} /> },
          { label: t.hero.trust3, icon: <Zap size={12} /> },
          { label: t.hero.trust4, icon: <Globe size={12} /> }
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-2 hover:text-brand-green transition-colors cursor-default group">
            <span className="text-brand-green group-hover:scale-125 transition-transform">{item.icon}</span> 
            {item.label}
          </div>
        ))}
      </div>

      <div className="mt-20 flex items-center gap-8 text-4xl flex-wrap justify-center opacity-80 filter grayscale hover:grayscale-0 transition-all duration-500">
        {["🇧🇷", "🇩🇪", "🇳🇱", "🇺🇸", "🇵🇹", "🇬🇧"].map((flag) => (
          <span key={flag} className="hover:scale-150 hover:-translate-y-2 transition-all cursor-default drop-shadow-2xl">
            {flag}
          </span>
        ))}
        <span className="text-[10px] font-bold text-white/20 uppercase tracking-widest">+ 14 countries</span>
      </div>
    </section>
  );
}
