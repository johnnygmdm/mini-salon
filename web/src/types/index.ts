export interface Customer {
  id: string;
  user_id: string;
  name: string;
  phone: string;
  memo: string | null;
  created_at: string;
}

export interface Treatment {
  id: string;
  user_id: string;
  customer_id: string;
  service_name: string;
  price: number;
  treated_at: string;
  created_at: string;
}

export interface CustomerSummary {
  count: number;
  totalAmount: number;
  latestDate: string;
}
