"use client";

import React, { useState } from "react";
import { Customer } from "@/types";
import { X, Loader2, Sparkles } from "lucide-react";
import { siteConfig } from "@/config/site-config";

interface TreatmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  customer: Customer | null;
  onSubmit: (data: {
    serviceName: string;
    price: number;
    treatedAt: string;
  }) => Promise<void>;
}

const COMMON_SERVICES = siteConfig.defaultMenuItems && siteConfig.defaultMenuItems.length > 0
  ? siteConfig.defaultMenuItems
  : [
      "남성 컷",
      "여성 컷",
      "학생 컷",
      "디자인 펌",
      "열펌 / 세팅펌",
      "볼륨 매직",
      "전체 염색",
      "뿌리 염색",
      "탈색",
      "모발 클리닉",
      "두피 스케일링",
      "다운펌",
      "드라이 / 스타일링",
    ];

export default function TreatmentModal({
  isOpen,
  onClose,
  customer,
  onSubmit,
}: TreatmentModalProps) {
  const today = new Date().toISOString().slice(0, 10);
  const [serviceName, setServiceName] = useState("남성 컷");
  const [price, setPrice] = useState<number>(25000);
  const [treatedAt, setTreatedAt] = useState(today);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  if (!isOpen || !customer) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!serviceName.trim()) {
      setErrorMsg("시술 항목명을 입력해주세요.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg("");

    try {
      await onSubmit({
        serviceName: serviceName.trim(),
        price: Number(price) || 0,
        treatedAt,
      });
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "시술 내역 등록에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              시술 내역 등록
            </h3>
            <p className="mt-0.5 text-xs text-indigo-600 font-medium">
              고객: {customer.name} ({customer.phone})
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="mt-4 rounded-lg bg-red-50 p-2.5 text-xs text-red-600">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* 시술일자 */}
          <div>
            <label className="block text-xs font-semibold text-slate-700">
              시술 일자
            </label>
            <input
              type="date"
              required
              value={treatedAt}
              onChange={(e) => setTreatedAt(e.target.value)}
              className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          {/* 시술 항목 */}
          <div>
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold text-slate-700">
                시술 항목
              </label>
              <span className="flex items-center gap-1 text-[11px] text-slate-400">
                <Sparkles className="h-3 w-3 text-amber-500" /> 빠른 선택
              </span>
            </div>

            {/* 빠른 추천 뱃지 */}
            <div className="mt-2 flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1 bg-slate-50 rounded-lg border border-slate-100">
              {COMMON_SERVICES.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setServiceName(s)}
                  className={`rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                    serviceName === s
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>

            <input
              type="text"
              required
              value={serviceName}
              onChange={(e) => setServiceName(e.target.value)}
              placeholder="시술명 직접 입력..."
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          {/* 시술 금액 */}
          <div>
            <label className="block text-xs font-semibold text-slate-700">
              시술 금액 (원)
            </label>
            <input
              type="number"
              step={1000}
              min={0}
              required
              value={price}
              onChange={(e) => setPrice(Number(e.target.value))}
              placeholder="25000"
              className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="rounded-lg border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 active:scale-95"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 active:scale-95 disabled:opacity-60"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  등록 중...
                </>
              ) : (
                "등록 완료"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
