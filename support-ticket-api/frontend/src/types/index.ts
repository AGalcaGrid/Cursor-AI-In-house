export interface User {
  id: number;
  name: string;
  email: string;
  role: 'customer' | 'agent' | 'admin';
  is_active?: boolean;
  created_at?: string;
}

export interface Ticket {
  id: number;
  ticket_number: string;
  subject: string;
  description: string;
  status: 'open' | 'assigned' | 'in_progress' | 'waiting' | 'resolved' | 'closed' | 'reopened';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'technical' | 'billing' | 'general' | 'feature_request';
  customer_id: number;
  customer_email: string;
  assigned_agent_id?: number;
  assigned_agent?: User;
  sla_deadline?: string;
  sla_breached: boolean;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  ticket_id: number;
  user_id: number;
  user: User;
  content: string;
  is_internal: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  sla_breached: number;
  tickets_by_status: Record<string, number>;
  tickets_by_priority: Record<string, number>;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category: 'electronics' | 'clothing' | 'books' | 'home' | 'sports';
  image_url: string;
  rating: number;
  stock: number;
  created_at: string;
}

export interface ProductSearchParams {
  query?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  sort_by?: 'price_asc' | 'price_desc' | 'name_asc' | 'name_desc' | 'rating' | 'newest';
  page?: number;
  per_page?: number;
}

export interface ProductSearchResponse {
  products: Product[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}
