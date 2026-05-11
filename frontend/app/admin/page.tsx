"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Users, Shield, Gift, Calendar, ArrowLeft, Search } from "lucide-react";
import { api } from "@/lib/api";

interface User {
  id: number;
  email: string;
  is_admin: boolean;
  is_free_user: boolean;
  is_whitelisted: boolean;
  trial_ends_at: string | null;
  created_at: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchUsers();
  }, []);

  async function fetchUsers() {
    try {
      const res = await api.get("/admin/users");
      setUsers(res.data);
    } catch (e) {
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  }

  async function toggleFreeAccess(userId: number, currentStatus: boolean) {
    try {
      await api.post("/admin/toggle-free", { user_id: userId, is_free: !currentStatus });
      setUsers(users.map(u => u.id === userId ? { ...u, is_free_user: !currentStatus } : u));
    } catch (e) {
      alert("Erro ao atualizar gratuidade");
    }
  }

  async function setAccess(userId: number) {
    const days = prompt("Quantos dias de acesso extra? (0 para remover)");
    if (days === null) return;
    
    const expires_at = days === "0" ? null : new Date(Date.now() + parseInt(days) * 86400000).toISOString();
    
    try {
      await api.post("/admin/access", { user_id: userId, expires_at, is_whitelisted: true });
      fetchUsers();
    } catch (e) {
      alert("Erro ao atualizar acesso");
    }
  }

  const filteredUsers = users.filter(u => u.email.toLowerCase().includes(searchTerm.toLowerCase()));

  if (loading) return <div className="min-h-screen flex items-center justify-center text-white">Carregando...</div>;

  return (
    <div className="min-h-screen bg-brand-dark text-white p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="p-2 hover:bg-white/10 rounded-full transition-colors">
              <ArrowLeft size={24} />
            </Link>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Shield className="text-brand-green" /> Painel Admin
            </h1>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
            <input 
              className="input pl-10 w-64" 
              placeholder="Procurar utilizador..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-4">
          {filteredUsers.map(u => (
            <div key={u.id} className="card flex items-center justify-between gap-6 hover:border-white/20 transition-all">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-lg">{u.email}</p>
                  {u.is_admin && <span className="bg-brand-green/20 text-brand-green text-[10px] uppercase font-bold px-2 py-0.5 rounded">Admin</span>}
                  {u.is_free_user && <span className="bg-brand-gold/20 text-brand-gold text-[10px] uppercase font-bold px-2 py-0.5 rounded">Gratuito</span>}
                </div>
                <p className="text-sm text-white/40">ID: {u.id} · Criado em: {new Date(u.created_at).toLocaleDateString()}</p>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  onClick={() => toggleFreeAccess(u.id, u.is_free_user)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${u.is_free_user ? "bg-brand-gold text-brand-dark" : "bg-white/5 hover:bg-white/10 text-white"}`}
                  title={u.is_free_user ? "Remover Gratuidade" : "Dar Gratuidade"}
                >
                  <Gift size={16} /> {u.is_free_user ? "Revogar" : "Dar Grátis"}
                </button>
                
                <button 
                  onClick={() => setAccess(u.id)}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white text-sm font-medium transition-all"
                >
                  <Calendar size={16} /> Trial/Extra
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
