"use client";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// Recebe o token JWT do redirect do Google OAuth e salva no localStorage
export default function AuthCallback() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const token = params.get("token");
    const error = params.get("error");
    if (token) {
      localStorage.setItem("token", token);
      router.replace("/dashboard");
    } else {
      router.replace(`/auth/login${error ? `?error=${error}` : ""}`);
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-dark">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-brand-green border-t-transparent rounded-full animate-spin" />
        <p className="text-white/50 text-sm">A autenticar...</p>
      </div>
    </div>
  );
}
