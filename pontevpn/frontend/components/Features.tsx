import { useLanguage } from "@/contexts/LanguageContext";

const ICONS = ["⚡", "👁️", "🌍", "🔒", "🛡️", "📱"];

export default function Features() {
  const { t } = useLanguage();

  return (
    <section id="features" className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-16">
          <p className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-3">{t.features.label}</p>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">{t.features.title}</h2>
          <p className="text-white/50 text-lg max-w-xl">{t.features.sub}</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {t.features.items.map((f, i) => (
            <div key={f.title} className="card hover:border-brand-green/40 transition-colors">
              <div className="w-10 h-10 bg-brand-green/10 rounded-xl flex items-center justify-center text-xl mb-4">
                {ICONS[i]}
              </div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-white/50 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
