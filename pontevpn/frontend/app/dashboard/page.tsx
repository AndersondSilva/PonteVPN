"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Download, Trash2, Plus, LogOut, CreditCard, Globe } from "lucide-react";
import { api } from "@/lib/api";

interface UserInfo { id: number; email: string; plan: string; }
interface Server { id: number; name: string; country: string; country_code: string; flag: string; is_available: boolean; load_percent: number; }
interface Config { id: number; server_name: string; server_country: string; country_code: string; device_name: string; vpn_ip: string; is_active: boolean; }

const PLAN_LABELS: Record<string, string> = { free: "Free", pro: "Pro", business: "Business" };
const FLAG: Record<string, string> = { BR: "🇧🇷", DE: "🇩🇪", NL: "🇳🇱", US: "🇺🇸", PT: "🇵🇹", GB: "🇬🇧" };

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [servers, setServers] = useState<Server[]>([]);
  const [configs, setConfigs] = useState<Config[]>([]);
  const [generating, setGenerating] = useState<number | null>(null);
  const [deviceName, setDeviceName] = useState("Meu Dispositivo");
  const [showNewConfig, setShowNewConfig] = useState(false);
  const [selectedServer, setSelectedServer] = useState<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/auth/login"); return; }
    Promise.all([
      api.get("/auth/me").then(r => setUser(r.data)),
      api.get("/servers").then(r => setServers(r.data)),
      api.get("/vpn/configs").then(r => setConfigs(r.data)),
    ]).catch(() => router.push("/auth/login"));
  }, []);

  async function generateConfig() {
    if (!selectedServer) return;
    setGenerating(selectedServer);
    try {
      const res = await api.post("/vpn/generate", { server_id: selectedServer, device_name: deviceName }, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `pontevpn-config.conf`;
      a.click();
      URL.revokeObjectURL(url);
      const updated = await api.get("/vpn/configs");
      setConfigs(updated.data);
      setShowNewConfig(false);
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro ao gerar configuração");
    } finally {
      setGenerating(null);
    }
  }

  async function revokeConfig(id: number) {
    if (!confirm("Revogar esta configuração? O dispositivo perderá acesso.")) return;
    await api.delete(`/vpn/configs/${id}`);
    setConfigs(configs.filter(c => c.id !== id));
  }

  async function goToBilling() {
    const { data } = await api.get("/payments/portal");
    window.open(data.portal_url, "_blank");
  }

  function logout() {
    localStorage.removeItem("token");
    router.push("/");
  }

  if (!user) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-brand-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="min-h-screen bg-brand-dark">
      {/* Header */}
      <header className="border-b border-white/10 bg-brand-card/50 px-4 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link href="/" className="font-bold text-lg">🌉 Ponte<span className="text-brand-green">VPN</span></Link>
          <div className="flex items-center gap-3">
            <span className={`text-xs font-bold px-3 py-1 rounded-full ${user.plan === "free" ? "bg-white/10 text-white/60" : "bg-brand-green/20 text-brand-green"}`}>
              {PLAN_LABELS[user.plan]}
            </span>
            <button onClick={goToBilling} className="text-white/50 hover:text-white p-2 transition-colors" title="Faturação">
              <CreditCard size={18} />
            </button>
            <button onClick={logout} className="text-white/50 hover:text-white p-2 transition-colors" title="Sair">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10 space-y-8">
        {/* Upgrade banner para free */}
        {user.plan === "free" && (
          <div className="card border-brand-gold/40 bg-brand-gold/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="font-semibold">Está no plano Free</p>
              <p className="text-white/50 text-sm">Aceda a todos os servidores e tráfego ilimitado com o Pro</p>
            </div>
            <Link href="/pricing" className="btn-primary text-sm whitespace-nowrap">Fazer Upgrade — €7,99/mês</Link>
          </div>
        )}

        {/* Configurações ativas */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">As minhas configurações</h2>
            <button onClick={() => setShowNewConfig(!showNewConfig)} className="btn-primary text-sm flex items-center gap-2 py-2 px-4">
              <Plus size={16} /> Nova Config
            </button>
          </div>

          {/* Formulário nova config */}
          {showNewConfig && (
            <div className="card mb-4 space-y-4">
              <h3 className="font-semibold">Gerar nova configuração</h3>
              <div>
                <label className="text-sm text-white/70 mb-2 block">Nome do dispositivo</label>
                <input value={deviceName} onChange={e => setDeviceName(e.target.value)} className="input" placeholder="Ex: iPhone, MacBook, Android..." />
              </div>
              <div>
                <label className="text-sm text-white/70 mb-2 block">Servidor</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {servers.map(s => (
                    <button
                      key={s.id}
                      onClick={() => s.is_available && setSelectedServer(s.id)}
                      className={`p-3 rounded-xl border text-left transition-all text-sm ${
                        !s.is_available
                          ? "border-white/5 opacity-40 cursor-not-allowed"
                          : selectedServer === s.id
                          ? "border-brand-green bg-brand-green/10"
                          : "border-white/10 hover:border-white/30"
                      }`}
                    >
                      <span className="text-xl">{s.flag}</span>
                      <p className="font-medium mt-1">{s.country}</p>
                      {!s.is_available && <p className="text-brand-gold text-xs">Requer Pro</p>}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={generateConfig} disabled={!selectedServer || !!generating} className="btn-primary flex items-center gap-2">
                  <Download size={16} />
                  {generating ? "A gerar..." : "Gerar e Descarregar .conf"}
                </button>
                <button onClick={() => setShowNewConfig(false)} className="btn-outline">Cancelar</button>
              </div>
            </div>
          )}

          {configs.length === 0 ? (
            <div className="card text-center py-12 text-white/40">
              <Globe size={40} className="mx-auto mb-3 opacity-30" />
              <p>Ainda não tem configurações.</p>
              <p className="text-sm mt-1">Clique em "Nova Config" para começar.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {configs.map(cfg => (
                <div key={cfg.id} className="card flex items-center gap-4">
                  <span className="text-3xl">{FLAG[cfg.country_code] || "🌐"}</span>
                  <div className="flex-1">
                    <p className="font-semibold">{cfg.device_name}</p>
                    <p className="text-white/50 text-sm">{cfg.server_country} · IP VPN: {cfg.vpn_ip}</p>
                  </div>
                  <button onClick={() => revokeConfig(cfg.id)} className="p-2 text-white/30 hover:text-red-400 transition-colors" title="Revogar">
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Guia de instalação */}
        <div className="card">
          <h2 className="font-bold mb-4">Como instalar o WireGuard</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            {[
              { os: "📱 iPhone / iPad", steps: ["App Store → WireGuard", "Abrir app → +", "Importar do ficheiro", "Ativar a ligação"] },
              { os: "🤖 Android", steps: ["Play Store → WireGuard", "Abrir app → +", "Criar a partir de ficheiro", "Ativar a ligação"] },
              { os: "💻 Windows / Mac", steps: ["wireguard.com → Download", "Instalar e abrir", "Import tunnel(s) from file", "Activate"] },
            ].map(g => (
              <div key={g.os} className="bg-white/5 rounded-xl p-4">
                <p className="font-semibold mb-3">{g.os}</p>
                <ol className="space-y-1 text-white/60">
                  {g.steps.map((s, i) => <li key={i}>{i + 1}. {s}</li>)}
                </ol>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
