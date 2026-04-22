import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "@/contexts/LanguageContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PonteVPN — Your bridge to Brazilian content",
  description: "Fast, secure VPN for Brazilian expats and anyone needing borderless internet. Servers in Brazil, Europe, USA and more.",
  keywords: "vpn brazil, globoplay abroad, vpn brasileira, vpn portugal, brazilian expat vpn, vpn para brasileiros europa",
  openGraph: {
    title: "PonteVPN",
    description: "Access Brazil from anywhere in the world.",
    url: "https://pontevpn.com",
    siteName: "PonteVPN",
    type: "website",
  },
};

import ErrorBoundary from "@/components/ErrorBoundary";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt">
      <body className={`${inter.className} bg-brand-dark text-white antialiased`}>
        <ErrorBoundary>
          <LanguageProvider>
            {children}
          </LanguageProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
