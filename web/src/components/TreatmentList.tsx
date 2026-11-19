"use client";

import React from "react";
import { Customer, Treatment, CustomerSummary } from "@/types";
import { formatCurrency } from "@/lib/utils";
import {
  Plus,
  Scissors,
  ArrowLeft,
  Calendar,
  CreditCard,
  History,
  Trash2,
  FileText,
} from "lucide-react";

interface TreatmentListProps {
  customer: Customer | null;
  treatments: Treatment[];
  summary: CustomerSummary;
  onOpenAddModal: () => void;
  onDeleteTreatment: (treatment: Treatment) => void;
  onBackToList?: () => void; // 모바일 뷰 전용 뒤로가기
}

export default function TreatmentList({
  customer,
  treatments,
  summary,
  onOpenAddModal,
  onDeleteTreatment,
  onBackToList,
}: TreatmentListProps) {
  if (!customer) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-400 shadow-sm">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-50 text-slate-300">
          <Scissors className="h-8 w-8 stroke-[1.5]" />
        </div>
        <h3 className="mt-4 text-base font-bold text-slate-700">
          고객을 선택해주세요
        </h3>
        <p className="mt-1 text-xs text-slate-400">
          좌측 목록에서 고객을 선택하면 1:N 시술 내역과 상세 정보를 확인하고
          등록할 수 있습니다.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-4">
      {/* 1. 상단 고객 요약 카드 */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {onBackToList && (
              <button
                onClick={onBackToList}
                className="mr-1 rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 sm:hidden"
                title="목록으로 돌아가기"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
            )}
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900 sm:text-lg">
                  {customer.name}
                </h2>
                <span className="text-xs font-medium text-slate-500">
                  {customer.phone}
                </span>
              </div>
              {customer.memo ? (
                <p className="mt-1 flex items-start gap-1 text-xs text-slate-600">
                  <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                  <span>{customer.memo}</span>
                </p>
              ) : (
                <p className="mt-1 text-xs text-slate-400">특이사항 없음</p>
              )}
            </div>
          </div>

          <button
            onClick={onOpenAddModal}
            className="flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-emerald-700 active:scale-95"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>시술 등록</span>
          </button>
        </div>

        {/* 3대 통계 지표 박스 */}
        <div className="mt-4 grid grid-cols-3 gap-2 rounded-xl bg-slate-50 p-3 sm:gap-4">
          <div className="text-center sm:text-left">
            <span className="flex items-center justify-center gap-1 text-[11px] font-medium text-slate-500 sm:justify-start">
              <History className="h-3 w-3 text-indigo-500" /> 방문 횟수
            </span>
            <p className="mt-1 text-sm font-bold text-slate-900 sm:text-base">
              {summary.count}회
            </p>
          </div>

          <div className="border-x border-slate-200 px-2 text-center sm:text-left">
            <span className="flex items-center justify-center gap-1 text-[11px] font-medium text-slate-500 sm:justify-start">
              <CreditCard className="h-3 w-3 text-indigo-500" /> 누적 금액
            </span>
            <p className="mt-1 truncate text-sm font-bold text-indigo-600 sm:text-base">
              {formatCurrency(summary.totalAmount)}
            </p>
          </div>

          <div className="text-center sm:text-left">
            <span className="flex items-center justify-center gap-1 text-[11px] font-medium text-slate-500 sm:justify-start">
              <Calendar className="h-3 w-3 text-indigo-500" /> 최근 방문일
            </span>
            <p className="mt-1 truncate text-xs font-bold text-slate-900 sm:text-sm">
              {summary.latestDate}
            </p>
          </div>
        </div>
      </div>

      {/* 2. 시술 내역 목록 */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-4 py-3 sm:px-5">
          <h3 className="text-xs font-bold text-slate-900 sm:text-sm">
            시술 이력 ({treatments.length}건)
          </h3>
        </div>

        <div className="flex-1 divide-y divide-slate-100 overflow-y-auto">
          {treatments.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
              <Scissors className="h-8 w-8 stroke-[1.5] text-slate-300" />
              <p className="mt-2 text-xs font-medium">등록된 시술 내역이 없습니다.</p>
              <button
                onClick={onOpenAddModal}
                className="mt-3 text-xs font-semibold text-indigo-600 hover:underline"
              >
                + 첫 시술 내역 등록하기
              </button>
            </div>
          ) : (
            treatments.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between p-3.5 transition-colors hover:bg-slate-50 sm:px-5"
              >
                <div className="min-w-0 flex-1 pr-3">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600">
                      {t.treated_at}
                    </span>
                    <span className="truncate text-sm font-bold text-slate-900">
                      {t.service_name}
                    </span>
                  </div>
                  <p className="mt-1 text-xs font-semibold text-indigo-600">
                    {formatCurrency(t.price)}
                  </p>
                </div>

                <button
                  onClick={() => onDeleteTreatment(t)}
                  className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600"
                  title="시술 내역 삭제"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
