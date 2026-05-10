"use client";
import { useLanguage } from "@/contexts/LanguageContext";

export default function HowItWorks() {
  const { t } = useLanguage();

  return (
    <section className="py-24 px-4 bg-brand-card/30">
      <div className="max-w-6xl mx-auto text-center">
        <p className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-3">{t.hiw.label}</p>
        <h2 className="text-3xl md:text-4xl font-bold mb-16">{t.hiw.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {t.hiw.steps.map((step, i) => (
            <div key={i} className="relative text-center">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-brand-green/10 border border-brand-green/30 flex items-center justify-center text-brand-green font-bold text-lg mb-4">
                {String(i + 1).padStart(2, "0")}
              </div>
              <h3 className="font-semibold mb-2">{step.title}</h3>
              <p className="text-white/50 text-sm leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
