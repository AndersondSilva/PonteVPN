"use client";
import { useState } from "react";
import { X, Send, MessageSquare } from "lucide-react";
import { api } from "@/lib/api";

export default function FeedbackModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [type, setType] = useState("general");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/feedback", { type, content });
      setSent(true);
      setTimeout(() => {
        onClose();
        setSent(false);
        setContent("");
      }, 2000);
    } catch (err) {
      alert("Erro ao enviar feedback.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="card w-full max-w-md relative overflow-hidden">
        <button onClick={onClose} className="absolute top-4 right-4 text-white/30 hover:text-white transition-colors">
          <X size={20} />
        </button>

        {sent ? (
          <div className="py-12 text-center space-y-4">
            <div className="w-16 h-16 bg-brand-green/20 text-brand-green rounded-full flex items-center justify-center mx-auto">
              <Send size={30} />
            </div>
            <h2 className="text-xl font-bold">Obrigado!</h2>
            <p className="text-white/50">O seu feedback foi enviado com sucesso.</p>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-brand-green/10 text-brand-green rounded-lg">
                <MessageSquare size={20} />
              </div>
              <h2 className="text-xl font-bold">Enviar Feedback</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-2">
                {["general", "bug", "feature"].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setType(t)}
                    className={`flex-1 py-2 px-3 rounded-xl border text-xs font-medium capitalize transition-all ${
                      type === t ? "border-brand-green bg-brand-green/10 text-brand-green" : "border-white/10 hover:border-white/30 text-white/50"
                    }`}
                  >
                    {t === "general" ? "Geral" : t === "bug" ? "Erro" : "Sugestão"}
                  </button>
                ))}
              </div>

              <textarea
                required
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Como podemos melhorar?"
                className="input min-h-[120px] resize-none"
              />

              <button disabled={loading || !content} className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? "A enviar..." : "Enviar Feedback"}
                {!loading && <Send size={16} />}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
