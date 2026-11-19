import type { Metadata, Viewport } from "next";
import "./globals.css";
import { siteConfig } from "@/config/site-config";

export const metadata: Metadata = {
  title: `${siteConfig.logoIcon} ${siteConfig.clientName} ${siteConfig.category} - 고객 & 시술 관리`,
  description: `${siteConfig.clientSubtitle} (PC 데스크톱 및 모바일 실시간 동기화)`,
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
