"use client";
import { useLanguage } from "@/contexts/LanguageContext";

const servers = [
  { flag: "🇧🇷", country: { pt: "Brasil", en: "Brazil" }, city: "São Paulo", plan: "Free", latency: "12ms" },
  { flag: "🇩🇪", country: { pt: "Alemanha", en: "Germany" }, city: "Frankfurt", plan: "Pro", latency: "8ms" },
  { flag: "🇳🇱", country: { pt: "Holanda", en: "Netherlands" }, city: "Amsterdam", plan: "Pro", latency: "9ms" },
  { flag: "🇺🇸", country: { pt: "Estados Unidos", en: "United States" }, city: "Miami", plan: "Pro", latency: "18ms" },
  { flag: "🇵🇹", country: { pt: "Portugal", en: "Portugal" }, city: "Lisbon", plan: "Pro", latency: "11ms" },
  { flag: "🇬🇧", country: { pt: "Reino Unido", en: "United Kingdom" }, city: "London", plan: "Pro", latency: "14ms" },
];

export default function Servers() {
  const { t, locale } = useLanguage();

  return (
    <section id="servers" className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <p className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-3">{t.servers.label}</p>
        <h2 className="text-3xl md:text-4xl font-bold mb-4">{t.servers.title}</h2>
        <p className="text-white/50 text-lg mb-12">{t.servers.sub}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {servers.map((s) => (
            <div key={s.city} className="card flex items-center gap-4 hover:border-brand-green/40 transition-colors">
              <span className="text-4xl">{s.flag}</span>
              <div className="flex-1">
                <p className="font-semibold">{s.country[locale]}</p>
                <p className="text-white/50 text-sm">{s.city}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className="w-1.5 h-1.5 bg-brand-green rounded-full" />
                  <span className="text-brand-green text-xs font-medium">Online</span>
                </div>
              </div>
              <div className="text-right">
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${s.plan === "Free" ? "bg-brand-green/20 text-brand-green" : "bg-brand-gold/20 text-brand-gold"}`}>
                  {s.plan}
                </span>
                <p className="text-white/40 text-xs mt-1">{s.latency}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
