"use client";

import React, { useState, useEffect, useCallback } from "react";
import { supabase } from "@/lib/supabaseClient";
import { Customer, Treatment, CustomerSummary } from "@/types";
import Navbar from "@/components/Navbar";
import LoginView from "@/components/LoginView";
import CustomerList from "@/components/CustomerList";
import CustomerModal from "@/components/CustomerModal";
import TreatmentList from "@/components/TreatmentList";
import TreatmentModal from "@/components/TreatmentModal";
import { Loader2 } from "lucide-react";

export default function Home() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);

  // 고객 및 시술 상태
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [treatments, setTreatments] = useState<Treatment[]>([]);
  const [summary, setSummary] = useState<CustomerSummary>({
    count: 0,
    totalAmount: 0,
    latestDate: "-",
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // 모달 제어
  const [isCustomerModalOpen, setIsCustomerModalOpen] = useState(false);
  const [customerToEdit, setCustomerToEdit] = useState<Customer | null>(null);
  const [isTreatmentModalOpen, setIsTreatmentModalOpen] = useState(false);

  // 모바일 전용 뷰 제어 ("list" | "detail")
  const [mobileView, setMobileView] = useState<"list" | "detail">("list");

  // 1. 인증 세션 확인
  useEffect(() => {
    const checkSession = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        if (data.session?.user) {
          setCurrentUser(data.session.user);
        }
      } catch (err) {
        console.error("세션 확인 실패:", err);
      } finally {
        setIsAuthChecking(false);
      }
    };

    checkSession();

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setCurrentUser(session?.user || null);
      }
    );

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  // 2. 고객 목록 로드
  const fetchCustomers = useCallback(async () => {
    if (!currentUser) return;
    setIsLoading(true);

    try {
      let query = supabase
        .from("customers")
        .select("*")
        .order("created_at", { ascending: false });

      if (searchQuery.trim()) {
        const term = searchQuery.trim();
        query = query.or(`name.ilike.%${term}%,phone.ilike.%${term}%`);
      }

      const { data, error } = await query;
      if (error) throw error;

      const list = data || [];
      setCustomers(list);

      // 현재 선택된 고객이 있으면 동기화
      if (selectedCustomer) {
        const matched = list.find((c) => c.id === selectedCustomer.id);
        if (matched) {
          setSelectedCustomer(matched);
        } else {
          setSelectedCustomer(null);
          setMobileView("list");
        }
      }
    } catch (err: any) {
      alert(`고객 목록 조회 실패: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [currentUser, searchQuery, selectedCustomer]);

  useEffect(() => {
    if (currentUser) {
      fetchCustomers();
    }
  }, [currentUser, fetchCustomers]);

  // 3. 특정 고객의 시술 내역 로드
  const fetchTreatments = useCallback(async (customerId: string) => {
    try {
      const { data, error } = await supabase
        .from("treatments")
        .select("*")
        .eq("customer_id", customerId)
        .order("treated_at", { ascending: false })
        .order("created_at", { ascending: false });

      if (error) throw error;

      const list: Treatment[] = data || [];
      setTreatments(list);

      const count = list.length;
      const totalAmount = list.reduce((sum, item) => sum + (item.price || 0), 0);
      const latestDate = count > 0 ? list[0].treated_at : "-";

      setSummary({ count, totalAmount, latestDate });
    } catch (err: any) {
      alert(`시술 내역 조회 실패: ${err.message}`);
    }
  }, []);

  // 고객 선택 핸들러
  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    fetchTreatments(customer.id);
    setMobileView("detail");
  };

  // 4. 고객 등록 / 수정
  const handleSaveCustomer = async (formData: {
    name: string;
    phone: string;
    memo: string;
  }) => {
    if (!currentUser) return;

    if (customerToEdit) {
      // 수정
      const { error } = await supabase
        .from("customers")
        .update({
          name: formData.name,
          phone: formData.phone,
          memo: formData.memo,
        })
        .eq("id", customerToEdit.id);

      if (error) throw error;
    } else {
      // 신규 등록
      const { error } = await supabase.from("customers").insert({
        name: formData.name,
        phone: formData.phone,
        memo: formData.memo,
        user_id: currentUser.id,
      });

      if (error) throw error;
    }

    await fetchCustomers();
  };

  // 5. 고객 삭제
  const handleDeleteCustomer = async (customer: Customer) => {
    const ok = window.confirm(
      `'${customer.name}' 고객을 삭제하시겠습니까?\n\n⚠️ 고객을 삭제하면 관련된 모든 시술 내역도 함께 영구 삭제됩니다.`
    );
    if (!ok) return;

    try {
      const { error } = await supabase
        .from("customers")
        .delete()
        .eq("id", customer.id);

      if (error) throw error;

      if (selectedCustomer?.id === customer.id) {
        setSelectedCustomer(null);
        setTreatments([]);
        setMobileView("list");
      }

      await fetchCustomers();
    } catch (err: any) {
      alert(`고객 삭제 실패: ${err.message}`);
    }
  };

  // 6. 시술 등록
  const handleSaveTreatment = async (formData: {
    serviceName: string;
    price: number;
    treatedAt: string;
  }) => {
    if (!currentUser || !selectedCustomer) return;

    const { error } = await supabase.from("treatments").insert({
      customer_id: selectedCustomer.id,
      service_name: formData.serviceName,
      price: formData.price,
      treated_at: formData.treatedAt,
      user_id: currentUser.id,
    });

    if (error) throw error;

    await fetchTreatments(selectedCustomer.id);
  };

  // 7. 시술 삭제
  const handleDeleteTreatment = async (treatment: Treatment) => {
    const ok = window.confirm(
      `'${treatment.service_name}' (${treatment.treated_at}) 시술 내역을 삭제하시겠습니까?`
    );
    if (!ok) return;

    try {
      const { error } = await supabase
        .from("treatments")
        .delete()
        .eq("id", treatment.id);

      if (error) throw error;

      if (selectedCustomer) {
        await fetchTreatments(selectedCustomer.id);
      }
    } catch (err: any) {
      alert(`시술 내역 삭제 실패: ${err.message}`);
    }
  };

  // 로그아웃
  const handleLogout = async () => {
    if (window.confirm("로그아웃 하시겠습니까?")) {
      await supabase.auth.signOut();
      setCurrentUser(null);
      setSelectedCustomer(null);
      setCustomers([]);
      setTreatments([]);
    }
  };

  // 인증 로딩 중 화면
  if (isAuthChecking) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  // 비로그인 상태일 때
  if (!currentUser) {
    return (
      <LoginView
        onLoginSuccess={(email) => {
          supabase.auth.getUser().then(({ data }) => {
            if (data?.user) setCurrentUser(data.user);
          });
        }}
      />
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-100/60">
      <Navbar
        userEmail={currentUser.email || ""}
        onLogout={handleLogout}
        onRefresh={() => {
          fetchCustomers();
          if (selectedCustomer) fetchTreatments(selectedCustomer.id);
        }}
        isLoading={isLoading}
      />

      <main className="mx-auto flex w-full max-w-7xl flex-1 px-3 py-3 sm:px-6 sm:py-6">
        {/* 모바일 뷰: 고객 리스트 ↔ 시술 상세 탭 전환 */}
        <div className="flex w-full flex-1 gap-5 md:hidden">
          {mobileView === "list" ? (
            <div className="h-[calc(100vh-80px)] w-full">
              <CustomerList
                customers={customers}
                selectedCustomerId={selectedCustomer?.id}
                onSelectCustomer={handleSelectCustomer}
                onOpenAddModal={() => {
                  setCustomerToEdit(null);
                  setIsCustomerModalOpen(true);
                }}
                onOpenEditModal={(cust) => {
                  setCustomerToEdit(cust);
                  setIsCustomerModalOpen(true);
                }}
                onDeleteCustomer={handleDeleteCustomer}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
              />
            </div>
          ) : (
            <div className="h-[calc(100vh-80px)] w-full">
              <TreatmentList
                customer={selectedCustomer}
                treatments={treatments}
                summary={summary}
                onOpenAddModal={() => setIsTreatmentModalOpen(true)}
                onDeleteTreatment={handleDeleteTreatment}
                onBackToList={() => setMobileView("list")}
              />
            </div>
          )}
        </div>

        {/* 데스크톱/태블릿 뷰: 2단 분할 레이아웃 (좌: 고객, 우: 시술 상세) */}
        <div className="hidden w-full flex-1 gap-6 md:grid md:grid-cols-12">
          {/* 좌측 고객 목록 (5 컬럼) */}
          <div className="h-[calc(100vh-100px)] md:col-span-5 lg:col-span-5">
            <CustomerList
              customers={customers}
              selectedCustomerId={selectedCustomer?.id}
              onSelectCustomer={handleSelectCustomer}
              onOpenAddModal={() => {
                setCustomerToEdit(null);
                setIsCustomerModalOpen(true);
              }}
              onOpenEditModal={(cust) => {
                setCustomerToEdit(cust);
                setIsCustomerModalOpen(true);
              }}
              onDeleteCustomer={handleDeleteCustomer}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />
          </div>

          {/* 우측 시술 상세 및 통계 (7 컬럼) */}
          <div className="h-[calc(100vh-100px)] md:col-span-7 lg:col-span-7">
            <TreatmentList
              customer={selectedCustomer}
              treatments={treatments}
              summary={summary}
              onOpenAddModal={() => setIsTreatmentModalOpen(true)}
              onDeleteTreatment={handleDeleteTreatment}
            />
          </div>
        </div>
      </main>

      {/* 모달 창들 */}
      <CustomerModal
        isOpen={isCustomerModalOpen}
        onClose={() => setIsCustomerModalOpen(false)}
        onSubmit={handleSaveCustomer}
        customerToEdit={customerToEdit}
      />

      <TreatmentModal
        isOpen={isTreatmentModalOpen}
        onClose={() => setIsTreatmentModalOpen(false)}
        customer={selectedCustomer}
        onSubmit={handleSaveTreatment}
      />
    </div>
  );
}
