"use client";
import { useState } from "react";
import Link from "next/link";
import { Check } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const HIGHLIGHT_INDEX = 1; // Pro plan

export default function Pricing() {
  const [yearly, setYearly] = useState(false);
  const { t } = useLanguage();

  return (
    <section id="pricing" className="py-24 px-4" style={{ background: "linear-gradient(180deg, #060c18 0%, #0A0F1E 100%)" }}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-4">
          <p className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-3">{t.pricing.label}</p>
          <h2 className="text-3xl md:text-4xl font-bold">{t.pricing.title}</h2>
          <p className="mt-4 text-white/50 text-lg">{t.pricing.sub}</p>

          <div className="mt-8 inline-flex items-center bg-brand-card border border-white/10 rounded-full p-1">
            <button onClick={() => setYearly(false)} className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${!yearly ? "bg-brand-green text-white" : "text-white/50 hover:text-white"}`}>
              {t.pricing.monthly}
            </button>
            <button onClick={() => setYearly(true)} className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${yearly ? "bg-brand-green text-white" : "text-white/50 hover:text-white"}`}>
              {t.pricing.yearly} <span className="text-brand-gold ml-1 text-xs">-33%</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {t.pricing.plans.map((plan, i) => (
            <div key={plan.name} className={`card relative flex flex-col ${i === HIGHLIGHT_INDEX ? "border-brand-green ring-1 ring-brand-green" : ""}`}>
              {i === HIGHLIGHT_INDEX && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-green text-white text-xs font-bold px-4 py-1 rounded-full whitespace-nowrap">
                  ⭐ {t.pricing.monthly === "Mensal" ? "Mais popular" : "Most popular"}
                </div>
              )}
              <div className="mb-6">
                <h3 className="text-xl font-bold">{plan.name}</h3>
                <div className="mt-3">
                  <span className="text-3xl font-extrabold">
                    {yearly ? plan.price.yearly : plan.price.monthly}
                  </span>
                </div>
                {yearly && plan.yearlyNote && (
                  <p className="text-brand-gold text-xs mt-1">{plan.yearlyNote}</p>
                )}
                <p className="text-white/50 text-sm mt-2">{plan.desc}</p>
              </div>
              <ul className="flex-1 space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <Check size={16} className="text-brand-green mt-0.5 flex-shrink-0" />
                    <span className="text-white/80">{f}</span>
                  </li>
                ))}
              </ul>
              <Link href={i === 0 ? "/auth/register" : `/auth/register?plan=${plan.name.toLowerCase()}`}
                className={`text-center text-sm font-semibold py-3 rounded-xl transition-all ${i === HIGHLIGHT_INDEX ? "btn-primary" : "border border-white/20 hover:border-brand-green text-white"}`}>
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
        <p className="text-center text-white/30 text-sm mt-8">{t.pricing.note}</p>
      </div>
    </section>
  );
}
