"use client";

import React from "react";
import { Customer } from "@/types";
import { Search, Plus, User, Phone, Edit2, Trash2 } from "lucide-react";

interface CustomerListProps {
  customers: Customer[];
  selectedCustomerId?: string | null;
  onSelectCustomer: (customer: Customer) => void;
  onOpenAddModal: () => void;
  onOpenEditModal: (customer: Customer) => void;
  onDeleteCustomer: (customer: Customer) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export default function CustomerList({
  customers,
  selectedCustomerId,
  onSelectCustomer,
  onOpenAddModal,
  onOpenEditModal,
  onDeleteCustomer,
  searchQuery,
  onSearchChange,
}: CustomerListProps) {
  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
      {/* 헤더 & 신규 고객 버튼 */}
      <div className="border-b border-slate-100 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 sm:text-base">
            고객 명단{" "}
            <span className="ml-1 text-xs font-semibold text-indigo-600">
              ({customers.length}명)
            </span>
          </h2>
          <button
            onClick={onOpenAddModal}
            className="flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 active:scale-95"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>신규 고객</span>
          </button>
        </div>

        {/* 검색창 */}
        <div className="relative mt-3">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="고객명 또는 연락처 검색..."
            className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-xs text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-600 sm:text-sm"
          />
        </div>
      </div>

      {/* 고객 목록 리스트 */}
      <div className="flex-1 divide-y divide-slate-100 overflow-y-auto">
        {customers.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
            <User className="h-10 w-10 stroke-[1.5] text-slate-300" />
            <p className="mt-2 text-xs font-medium">등록된 고객이 없습니다.</p>
            {searchQuery && (
              <p className="mt-1 text-[11px] text-slate-400">
                검색어를 확인해 보세요.
              </p>
            )}
          </div>
        ) : (
          customers.map((cust) => {
            const isSelected = cust.id === selectedCustomerId;
            return (
              <div
                key={cust.id}
                onClick={() => onSelectCustomer(cust)}
                className={`group flex cursor-pointer items-center justify-between p-3.5 transition-colors sm:p-4 ${
                  isSelected
                    ? "bg-indigo-50/80 ring-1 ring-inset ring-indigo-500/20"
                    : "hover:bg-slate-50"
                }`}
              >
                <div className="min-w-0 flex-1 pr-3">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-bold text-slate-900">
                      {cust.name}
                    </span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
                      {cust.created_at ? cust.created_at.slice(0, 10) : ""}
                    </span>
                  </div>

                  <div className="mt-1 flex items-center gap-1 text-xs text-slate-500">
                    <Phone className="h-3 w-3 shrink-0 text-slate-400" />
                    <span>{cust.phone}</span>
                  </div>

                  {cust.memo && (
                    <p className="mt-1 line-clamp-1 text-xs text-slate-400">
                      {cust.memo}
                    </p>
                  )}
                </div>

                {/* 수정 / 삭제 버튼 */}
                <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenEditModal(cust);
                    }}
                    className="rounded-md p-1.5 text-slate-400 hover:bg-white hover:text-indigo-600 hover:shadow-sm"
                    title="수정"
                  >
                    <Edit2 className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteCustomer(cust);
                    }}
                    className="rounded-md p-1.5 text-slate-400 hover:bg-white hover:text-red-600 hover:shadow-sm"
                    title="삭제"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
