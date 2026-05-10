"use client";
import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useLanguage } from "@/contexts/LanguageContext";

export default function RegisterPage() {
  const { t, locale, setLocale } = useLanguage();
  const a = t.auth;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) { setError(locale === "pt" ? "A password deve ter pelo menos 8 caracteres" : "Password must be at least 8 characters"); return; }
    setLoading(true);
    setError("");
    try {
      await api.post("/auth/register", { email, password });
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar conta.");
    } finally {
      setLoading(false);
    }
  }

  function handleGoogle() {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/google`;
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-brand-dark">
        <div className="w-full max-w-md text-center card">
          <div className="text-5xl mb-4">📧</div>
          <h2 className="text-2xl font-bold mb-2">{a.verifyTitle}</h2>
          <p className="text-white/50">{a.verifyMsg} <strong className="text-white">{email}</strong>. {a.verifySpam}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-brand-dark">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="text-2xl font-bold">🌉 Ponte<span className="text-brand-green">VPN</span></Link>
          <h1 className="mt-6 text-2xl font-bold">{a.registerTitle}</h1>
          <p className="text-white/50 mt-2">{a.registerSub}</p>
        </div>

        <div className="card space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-xl">{error}</div>
          )}

          {/* Social OAuth */}
          <div className="grid grid-cols-1 gap-2">
            <button onClick={handleGoogle}
              className="w-full flex items-center justify-center gap-3 bg-white text-gray-800 font-semibold py-3 rounded-xl hover:bg-gray-100 transition-all text-sm">
              <svg width="18" height="18" viewBox="0 0 18 18"><path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/><path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/><path fill="#FBBC05" d="M3.964 10.706A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.038l3.007-2.332z"/><path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.962L3.964 7.294C4.672 5.163 6.656 3.58 9 3.58z"/></svg>
              {a.googleLogin}
            </button>
            <button onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/apple`}
              className="w-full flex items-center justify-center gap-3 bg-black text-white font-semibold py-3 rounded-xl hover:bg-black/80 transition-all text-sm">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="white"><path d="M15.064 10.662c.038 2.378 2.083 3.167 2.11 3.179-.02.057-.332 1.139-1.096 2.253-.66 1.002-1.347 1.96-2.457 1.983-1.088.024-1.442-.644-2.686-.644-1.246 0-1.636.621-2.662.664-1.071.042-1.84-.963-2.503-1.921-1.354-1.956-2.39-5.526-.994-7.947.693-1.203 1.93-1.964 3.264-1.984 1.014-.017 1.97.683 2.586.683.618 0 1.769-.854 2.973-.73 1.066.046 2.031.59 2.684 1.547-2.148 1.29-1.815 3.864.218 5.093l-.001.001M12.441 2.871c.542-.656.908-1.567.808-2.474-.78.033-1.724.521-2.285 1.177-.503.57-.942 1.498-.824 2.386.871.067 1.761-.433 2.301-1.089z"/></svg>
              {a.appleLogin}
            </button>
            <button onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/microsoft`}
              className="w-full flex items-center justify-center gap-3 bg-[#2F2F2F] text-white font-semibold py-3 rounded-xl hover:bg-[#2F2F2F]/80 transition-all text-sm">
              <svg width="18" height="18" viewBox="0 0 18 18"><path fill="#f35325" d="M0 0h8.5v8.5H0z"/><path fill="#81bc06" d="M9.5 0H18v8.5H9.5z"/><path fill="#05a6f0" d="M0 9.5h8.5V18H0z"/><path fill="#ffba08" d="M9.5 9.5H18V18H9.5z"/></svg>
              {a.microsoftLogin}
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-white/30 text-xs">{a.orDivider}</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-white/70 mb-2">{a.email}</label>
              <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="email@example.com" className="input" />
            </div>
            <div>
              <label className="block text-sm text-white/70 mb-2">{a.password}</label>
              <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Min. 8 characters" className="input" />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? a.registerBtnLoading : a.registerBtn}
            </button>
          </form>

          <p className="text-white/30 text-xs text-center">
            {a.terms1}{" "}
            <Link href="/legal/terms" className="underline hover:text-white/60">{a.terms2}</Link>
            {" "}{a.terms3}{" "}
            <Link href="/legal/privacy" className="underline hover:text-white/60">{a.terms4}</Link>.
          </p>
        </div>

        <p className="text-center text-white/50 text-sm mt-6">
          {a.hasAccount}{" "}
          <Link href="/auth/login" className="text-brand-green hover:underline">{a.loginLink}</Link>
        </p>

        <div className="text-center mt-4">
          <button onClick={() => setLocale(locale === "pt" ? "en" : "pt")} className="text-white/30 text-xs hover:text-white/60 transition-colors">
            {locale === "pt" ? "🇬🇧 Switch to English" : "🇧🇷 Mudar para Português"}
          </button>
        </div>
      </div>
    </div>
  );
}
