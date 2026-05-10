"use client";
import { useState } from "react";
import Link from "next/link";
import { ChevronDown } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  const { t } = useLanguage();

  return (
    <section id="faq" className="py-24 px-4 bg-brand-card/30">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-3">{t.faq.label}</p>
        <h2 className="text-3xl md:text-4xl font-bold mb-12">{t.faq.title}</h2>
        <div className="space-y-3">
          {t.faq.items.map((faq, i) => (
            <div key={i} className="card cursor-pointer" onClick={() => setOpen(open === i ? null : i)}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{faq.q}</h3>
                <ChevronDown size={18} className={`text-white/50 flex-shrink-0 ml-4 transition-transform ${open === i ? "rotate-180" : ""}`} />
              </div>
              {open === i && (
                <p className="mt-3 text-white/60 text-sm leading-relaxed border-t border-white/10 pt-3">{faq.a}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
