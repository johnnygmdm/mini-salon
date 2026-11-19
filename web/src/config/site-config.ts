import clientConfig from "../../client_config.json";

export interface SiteConfig {
  clientName: string;
  clientSubtitle: string;
  category: string;
  logoIcon: string;
  theme: string;
  colors: {
    primary: string;
    primaryHover: string;
    primaryLight: string;
    primaryBorder: string;
    textOnPrimary: string;
  };
  defaultMenuItems: string[];
  adminEmail: string;
  version: string;
}

export const siteConfig: SiteConfig = {
  clientName: clientConfig.clientName || "Mini Salon",
  clientSubtitle: clientConfig.clientSubtitle || "1인 미용실 고객 & 시술 관리",
  category: clientConfig.category || "CRM",
  logoIcon: clientConfig.logoIcon || "✂️",
  theme: clientConfig.theme || "indigo",
  colors: clientConfig.colors || {
    primary: "#4f46e5",
    primaryHover: "#4338ca",
    primaryLight: "#eef2ff",
    primaryBorder: "#c7d2fe",
    textOnPrimary: "#ffffff",
  },
  defaultMenuItems: clientConfig.defaultMenuItems || [
    "커트",
    "일반펌",
    "열펌/매직",
    "전체염색",
    "뿌리염색",
    "클리닉",
    "스캘프케어",
  ],
  adminEmail: clientConfig.adminEmail || "ase3612@naver.com",
  version: clientConfig.version || "1.0.1",
};
