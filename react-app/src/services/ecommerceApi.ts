import axios from 'axios';

console.log('ecommerceApi.ts loaded - exports available');

const API_BASE_URL = 'http://localhost:5004/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ecommerce_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types - Using type instead of interface for better Vite compatibility
export type Product = {
  id: number;
  sku: string;
  name: string;
  description: string;
  price: number;
  compare_at_price?: number;
  category: string;
  brand?: string;
  image_url?: string;
  stock_quantity: number;
  in_stock: boolean;
  is_low_stock: boolean;
  discount_percentage: number;
  rating: number;
  review_count: number;
};

export type CartItem = {
  id: number;
  product_id: number;
  product: Product;
  quantity: number;
  price: number;
  total_price: number;
};

export type Cart = {
  id: number;
  total_items: number;
  subtotal: number;
  discount_amount: number;
  total: number;
  items: CartItem[];
  discount_code?: {
    code: string;
    discount_type: string;
    discount_value: number;
  };
};

export type Order = {
  id: number;
  order_number: string;
  status: string;
  subtotal: number;
  discount_amount: number;
  shipping_cost: number;
  tax_amount: number;
  total: number;
  total_items: number;
  items: Array<{
    product_name: string;
    quantity: number;
    price: number;
    total_price: number;
  }>;
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_email: string;
  shipping_street_address: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  created_at: string;
};

export type CheckoutData = {
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_email: string;
  shipping_phone?: string;
  shipping_street_address: string;
  shipping_apartment?: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country?: string;
  billing_same_as_shipping?: boolean;
  payment_method: string;
  notes?: string;
};

// Auth API
export const authApi = {
  register: async (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => {
    const response = await api.post('/auth/register', data);
    if (response.data.data.access_token) {
      localStorage.setItem('ecommerce_token', response.data.data.access_token);
    }
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.data.access_token) {
      localStorage.setItem('ecommerce_token', response.data.data.access_token);
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('ecommerce_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data.data;
  },
};

// Products API
export const productsApi = {
  getAll: async (params?: {
    page?: number;
    per_page?: number;
    category?: string;
    search?: string;
    in_stock_only?: boolean;
  }) => {
    const response = await api.get('/products', { params });
    return response.data.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/products/${id}`);
    return response.data.data;
  },

  getCategories: async () => {
    const response = await api.get('/products/categories');
    return response.data.data.categories;
  },
};

// Cart API
export const cartApi = {
  getCart: async (): Promise<Cart> => {
    const response = await api.get('/cart');
    return response.data.data;
  },

  addItem: async (productId: number, quantity: number = 1) => {
    const response = await api.post('/cart/items', {
      product_id: productId,
      quantity,
    });
    return response.data.data;
  },

  updateItem: async (productId: number, quantity: number) => {
    const response = await api.put(`/cart/items/${productId}`, { quantity });
    return response.data.data;
  },

  removeItem: async (productId: number) => {
    const response = await api.delete(`/cart/items/${productId}`);
    return response.data.data;
  },

  clearCart: async () => {
    const response = await api.post('/cart/clear');
    return response.data.data;
  },

  applyDiscount: async (code: string) => {
    const response = await api.post('/cart/discount', { code });
    return response.data.data;
  },

  removeDiscount: async () => {
    const response = await api.delete('/cart/discount');
    return response.data.data;
  },
};

// Checkout API
export const checkoutApi = {
  createPaymentIntent: async () => {
    const response = await api.post('/checkout/create-payment-intent');
    return response.data.data;
  },

  completeCheckout: async (data: CheckoutData): Promise<Order> => {
    const response = await api.post('/checkout/complete', data);
    return response.data.data;
  },
};

// Orders API
export const ordersApi = {
  getAll: async (params?: { page?: number; status?: string }) => {
    const response = await api.get('/orders', { params });
    return response.data.data;
  },

  getById: async (id: number): Promise<Order> => {
    const response = await api.get(`/orders/${id}`);
    return response.data.data;
  },

  getByOrderNumber: async (orderNumber: string): Promise<Order> => {
    const response = await api.get(`/orders/${orderNumber}`);
    return response.data.data;
  },

  cancelOrder: async (id: number) => {
    const response = await api.post(`/orders/${id}/cancel`);
    return response.data.data;
  },
};

export default api;
