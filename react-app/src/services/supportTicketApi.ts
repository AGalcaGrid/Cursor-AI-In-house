const API_BASE_URL = import.meta.env.VITE_SUPPORT_API_URL || 'http://localhost:5000/api';

export interface SupportUser {
  id: number;
  name: string;
  email: string;
  role: 'customer' | 'agent' | 'admin';
  is_active?: boolean;
  created_at?: string;
}

export interface SupportTicket {
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
  assigned_agent?: SupportUser;
  sla_deadline?: string;
  sla_breached: boolean;
  created_at: string;
  updated_at: string;
}

export interface SupportComment {
  id: number;
  ticket_id: number;
  user_id: number;
  user: SupportUser;
  content: string;
  is_internal: boolean;
  created_at: string;
}

export interface SupportAuthResponse {
  access_token: string;
  user: SupportUser;
}

export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  sla_breached: number;
  tickets_by_status: Record<string, number>;
  tickets_by_priority: Record<string, number>;
}

class SupportTicketApiService {
  private getAuthHeader(token: string): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async register(name: string, email: string, password: string): Promise<SupportAuthResponse> {
    await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    return response.json();
  }

  async login(email: string, password: string): Promise<SupportAuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    return response.json();
  }

  async me(token: string): Promise<SupportUser> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    return response.json();
  }

  async getTickets(token: string, params?: Record<string, string>): Promise<{ tickets: SupportTicket[]; total: number; pages: number }> {
    const queryParams = new URLSearchParams(params);
    const url = `${API_BASE_URL}/tickets${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch tickets');
    }

    return response.json();
  }

  async getTicket(token: string, id: number): Promise<SupportTicket> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch ticket');
    }

    return response.json();
  }

  async createTicket(token: string, ticket: Partial<SupportTicket>): Promise<SupportTicket> {
    const response = await fetch(`${API_BASE_URL}/tickets`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(ticket),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create ticket');
    }

    return response.json();
  }

  async updateTicketStatus(token: string, id: number, status: string): Promise<SupportTicket> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}/status`, {
      method: 'PUT',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to update status');
    }

    return response.json();
  }

  async assignTicket(token: string, id: number, agentId: number): Promise<SupportTicket> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}/assign`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({ agent_id: agentId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to assign ticket');
    }

    return response.json();
  }

  async deleteTicket(token: string, id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to delete ticket');
    }
  }

  async getComments(token: string, ticketId: number): Promise<SupportComment[]> {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch comments');
    }

    return response.json();
  }

  async createComment(token: string, ticketId: number, content: string, isInternal: boolean = false): Promise<SupportComment> {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({ content, is_internal: isInternal }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create comment');
    }

    return response.json();
  }

  async getDashboardStats(token: string): Promise<DashboardStats> {
    const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch dashboard stats');
    }

    return response.json();
  }

  async getAgents(token: string): Promise<SupportUser[]> {
    const response = await fetch(`${API_BASE_URL}/agents`, {
      method: 'GET',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agents');
    }

    return response.json();
  }
}

export const supportTicketApi = new SupportTicketApiService();
