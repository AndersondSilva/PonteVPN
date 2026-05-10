"use client";
import Link from "next/link";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Footer() {
  const { t } = useLanguage();
  const l = t.footer;

  return (
    <footer className="border-t border-white/10 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div>
            <p className="font-bold text-lg mb-2">🌉 PonteVPN</p>
            <p className="text-white/40 text-sm">{l.tagline}</p>
          </div>
          <div>
            <p className="font-semibold text-sm mb-3 text-white/70 uppercase tracking-wide text-xs">{l.product}</p>
            <ul className="space-y-2 text-sm text-white/40">
              <li><Link href="#features" className="hover:text-white transition-colors">{l.links.features}</Link></li>
              <li><Link href="#servers" className="hover:text-white transition-colors">{l.links.servers}</Link></li>
              <li><Link href="#pricing" className="hover:text-white transition-colors">{l.links.pricing}</Link></li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-sm mb-3 text-white/70 uppercase tracking-wide text-xs">{l.support}</p>
            <ul className="space-y-2 text-sm text-white/40">
              <li><Link href="#faq" className="hover:text-white transition-colors">{l.links.faq}</Link></li>
              <li><a href={`mailto:${l.links.email}`} className="hover:text-white transition-colors">{l.links.email}</a></li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-sm mb-3 text-white/70 uppercase tracking-wide text-xs">{l.legal}</p>
            <ul className="space-y-2 text-sm text-white/40">
              <li><Link href="/legal/privacy" className="hover:text-white transition-colors">{l.links.privacy}</Link></li>
              <li><Link href="/legal/terms" className="hover:text-white transition-colors">{l.links.terms}</Link></li>
              <li><Link href="/legal/cookies" className="hover:text-white transition-colors">{l.links.cookies}</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-white/10 pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-white/30 text-xs">
          <p>{l.bottom1}</p>
          <p>{l.bottom2}</p>
        </div>
      </div>
    </footer>
  );
}
