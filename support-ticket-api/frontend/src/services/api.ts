import axios from 'axios';
import type { User, Ticket, Comment, AuthResponse, DashboardStats, Product, ProductSearchParams, ProductSearchResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface NotificationPreferences {
  email_ticket_created: boolean;
  email_ticket_assigned: boolean;
  email_status_changed: boolean;
  email_new_comment: boolean;
  email_sla_warning: boolean;
  email_sla_breach: boolean;
  email_mentions: boolean;
  in_app_notifications: boolean;
}

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await api.post('/auth/login', { email, password });
    return data;
  },
  register: async (name: string, email: string, password: string): Promise<AuthResponse> => {
    // Register the user
    await api.post('/auth/register', { name, email, password });
    // Then log them in to get the token
    const { data } = await api.post('/auth/login', { email, password });
    return data;
  },
  me: async (): Promise<User> => {
    const { data } = await api.get('/auth/me');
    return data;
  },
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },
  getNotificationPreferences: async (): Promise<{ preferences: NotificationPreferences }> => {
    const { data } = await api.get('/auth/notification-preferences');
    return data;
  },
  updateNotificationPreferences: async (prefs: Partial<NotificationPreferences>): Promise<{ preferences: NotificationPreferences }> => {
    const { data } = await api.put('/auth/notification-preferences', prefs);
    return data;
  },
};

export const ticketService = {
  list: async (params?: Record<string, string>): Promise<{ tickets: Ticket[]; total: number; pages: number }> => {
    const { data } = await api.get('/tickets', { params });
    return data;
  },
  get: async (id: number): Promise<Ticket> => {
    const { data } = await api.get(`/tickets/${id}`);
    return data;
  },
  create: async (ticket: Partial<Ticket>): Promise<Ticket> => {
    const { data } = await api.post('/tickets', ticket);
    return data;
  },
  update: async (id: number, ticket: Partial<Ticket>): Promise<Ticket> => {
    const { data } = await api.put(`/tickets/${id}`, ticket);
    return data;
  },
  updateStatus: async (id: number, status: string): Promise<Ticket> => {
    const { data } = await api.put(`/tickets/${id}/status`, { status });
    return data;
  },
  assign: async (id: number, agentId: number): Promise<Ticket> => {
    const { data } = await api.post(`/tickets/${id}/assign`, { agent_id: agentId });
    return data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/tickets/${id}`);
  },
};

export const commentService = {
  list: async (ticketId: number): Promise<Comment[]> => {
    const { data } = await api.get(`/tickets/${ticketId}/comments`);
    return data;
  },
  create: async (ticketId: number, content: string, isInternal: boolean = false): Promise<Comment> => {
    const { data } = await api.post(`/tickets/${ticketId}/comments`, { content, is_internal: isInternal });
    return data;
  },
  delete: async (ticketId: number, commentId: number): Promise<void> => {
    await api.delete(`/tickets/${ticketId}/comments/${commentId}`);
  },
};

export const agentService = {
  list: async (): Promise<User[]> => {
    const { data } = await api.get('/agents');
    return data;
  },
};

export const adminService = {
  dashboard: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/admin/dashboard');
    return data;
  },
  listUsers: async (role?: string): Promise<{ users: User[] }> => {
    const params = role ? { role } : {};
    const { data } = await api.get('/admin/users', { params });
    return data;
  },
  createUser: async (userData: { name: string; email: string; password: string; role: 'agent' | 'admin' }): Promise<{ user: User }> => {
    const { data } = await api.post('/admin/users', userData);
    return data;
  },
  updateUser: async (userId: number, userData: { name?: string; role?: string; is_active?: boolean }): Promise<{ user: User }> => {
    const { data } = await api.put(`/admin/users/${userId}`, userData);
    return data;
  },
  exportTickets: async (format: 'csv' | 'pdf', filters?: { status?: string; priority?: string }): Promise<Blob> => {
    const params = { format, ...filters };
    const { data } = await api.get('/admin/reports/export/tickets', { params, responseType: 'blob' });
    return data;
  },
  runSlaCheck: async (): Promise<{ warnings_sent: number; breaches_found: number }> => {
    const { data } = await api.post('/admin/sla/check');
    return data;
  },
};

// Mock product data for demo purposes
const mockProducts: Product[] = [
  { id: 1, name: 'Wireless Headphones', description: 'High-quality wireless headphones with noise cancellation', price: 199.99, category: 'electronics', image_url: '/images/headphones.jpg', rating: 4.5, stock: 50, created_at: '2024-01-15' },
  { id: 2, name: 'Running Shoes', description: 'Lightweight running shoes for marathon training', price: 129.99, category: 'sports', image_url: '/images/shoes.jpg', rating: 4.8, stock: 30, created_at: '2024-01-20' },
  { id: 3, name: 'Cotton T-Shirt', description: 'Comfortable 100% cotton t-shirt', price: 29.99, category: 'clothing', image_url: '/images/tshirt.jpg', rating: 4.2, stock: 100, created_at: '2024-02-01' },
  { id: 4, name: 'JavaScript Guide', description: 'Complete guide to modern JavaScript', price: 49.99, category: 'books', image_url: '/images/book.jpg', rating: 4.9, stock: 25, created_at: '2024-02-10' },
  { id: 5, name: 'Smart Watch', description: 'Fitness tracking smart watch with GPS', price: 299.99, category: 'electronics', image_url: '/images/watch.jpg', rating: 4.6, stock: 40, created_at: '2024-02-15' },
  { id: 6, name: 'Yoga Mat', description: 'Non-slip yoga mat for home workouts', price: 39.99, category: 'sports', image_url: '/images/yogamat.jpg', rating: 4.4, stock: 60, created_at: '2024-02-20' },
  { id: 7, name: 'Winter Jacket', description: 'Warm winter jacket with hood', price: 189.99, category: 'clothing', image_url: '/images/jacket.jpg', rating: 4.7, stock: 20, created_at: '2024-03-01' },
  { id: 8, name: 'Coffee Table', description: 'Modern wooden coffee table', price: 249.99, category: 'home', image_url: '/images/table.jpg', rating: 4.3, stock: 15, created_at: '2024-03-05' },
  { id: 9, name: 'Bluetooth Speaker', description: 'Portable waterproof bluetooth speaker', price: 79.99, category: 'electronics', image_url: '/images/speaker.jpg', rating: 4.5, stock: 45, created_at: '2024-03-10' },
  { id: 10, name: 'Desk Lamp', description: 'LED desk lamp with adjustable brightness', price: 59.99, category: 'home', image_url: '/images/lamp.jpg', rating: 4.1, stock: 35, created_at: '2024-03-15' },
  { id: 11, name: 'Tennis Racket', description: 'Professional tennis racket', price: 149.99, category: 'sports', image_url: '/images/racket.jpg', rating: 4.6, stock: 22, created_at: '2024-03-20' },
  { id: 12, name: 'Novel Collection', description: 'Best-selling novel collection', price: 34.99, category: 'books', image_url: '/images/novels.jpg', rating: 4.8, stock: 50, created_at: '2024-03-25' },
];

export const productService = {
  search: async (params: ProductSearchParams): Promise<ProductSearchResponse> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    let filtered = [...mockProducts];
    
    // Apply search query
    if (params.query) {
      const query = params.query.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.description.toLowerCase().includes(query)
      );
    }
    
    // Apply category filter
    if (params.category) {
      filtered = filtered.filter(p => p.category === params.category);
    }
    
    // Apply price range
    if (params.min_price !== undefined) {
      filtered = filtered.filter(p => p.price >= params.min_price!);
    }
    if (params.max_price !== undefined) {
      filtered = filtered.filter(p => p.price <= params.max_price!);
    }
    
    // Apply sorting
    if (params.sort_by) {
      switch (params.sort_by) {
        case 'price_asc':
          filtered.sort((a, b) => a.price - b.price);
          break;
        case 'price_desc':
          filtered.sort((a, b) => b.price - a.price);
          break;
        case 'name_asc':
          filtered.sort((a, b) => a.name.localeCompare(b.name));
          break;
        case 'name_desc':
          filtered.sort((a, b) => b.name.localeCompare(a.name));
          break;
        case 'rating':
          filtered.sort((a, b) => b.rating - a.rating);
          break;
        case 'newest':
          filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
          break;
      }
    }
    
    // Apply pagination
    const page = params.page || 1;
    const perPage = params.per_page || 6;
    const total = filtered.length;
    const pages = Math.ceil(total / perPage);
    const start = (page - 1) * perPage;
    const paginatedProducts = filtered.slice(start, start + perPage);
    
    return {
      products: paginatedProducts,
      total,
      page,
      pages,
      per_page: perPage,
    };
  },
  
  get: async (id: number): Promise<Product | null> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return mockProducts.find(p => p.id === id) || null;
  },
};

export default api;
