"use client";

import React from "react";
import { LogOut, RefreshCw, User } from "lucide-react";
import { siteConfig } from "../config/site-config";

interface NavbarProps {
  userEmail: string;
  onLogout: () => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export default function Navbar({
  userEmail,
  onLogout,
  onRefresh,
  isLoading,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* 로고 & 타이틀 */}
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm text-base font-bold">
            {siteConfig.logoIcon}
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-slate-900 sm:text-lg">
              {siteConfig.clientName} <span className="text-indigo-600">{siteConfig.category}</span>
            </h1>
            <p className="hidden text-xs text-slate-500 sm:block">
              {siteConfig.clientSubtitle}
            </p>
          </div>
        </div>

        {/* 우측 사용자 정보 & 액션 */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="hidden items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 sm:flex">
            <User className="h-3.5 w-3.5 text-slate-400" />
            <span className="max-w-[160px] truncate">{userEmail}</span>
          </div>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 active:scale-95 disabled:opacity-50"
            title="새로고침"
          >
            <RefreshCw
              className={`h-4 w-4 ${isLoading ? "animate-spin text-indigo-600" : ""}`}
            />
          </button>

          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 rounded-lg border border-red-200 bg-white px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 active:scale-95 sm:text-sm"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">로그아웃</span>
          </button>
        </div>
      </div>
    </header>
  );
}
