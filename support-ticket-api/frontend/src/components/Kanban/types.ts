export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';

// Map ticket statuses to Kanban columns
export type TicketStatus = 'open' | 'assigned' | 'in_progress' | 'waiting' | 'resolved' | 'closed' | 'reopened';

export const TICKET_TO_KANBAN_STATUS: Record<TicketStatus, TaskStatus> = {
  open: 'todo',
  assigned: 'todo',
  reopened: 'todo',
  in_progress: 'in_progress',
  waiting: 'review',
  resolved: 'done',
  closed: 'done',
};

export const KANBAN_TO_TICKET_STATUS: Record<TaskStatus, TicketStatus> = {
  todo: 'open',
  in_progress: 'in_progress',
  review: 'waiting',
  done: 'resolved',
};

export interface KanbanTask {
  id: string;
  ticketId?: number; // Link to real ticket
  ticketNumber?: string; // e.g., TICK-20260701-0001
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: {
    id: number;
    name: string;
    avatar?: string;
  };
  dueDate?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  category?: string;
  customerEmail?: string;
  isFromTicket?: boolean; // Flag to identify ticket-based tasks
}

export interface KanbanColumn {
  id: TaskStatus;
  title: string;
  color: string;
  tasks: KanbanTask[];
}

export interface KanbanBoardState {
  columns: KanbanColumn[];
  searchQuery: string;
  filterPriority: TaskPriority | 'all';
  filterAssignee: number | 'all';
}

export const COLUMN_CONFIG: Record<TaskStatus, { title: string; color: string }> = {
  todo: { title: 'To Do', color: '#6b7280' },
  in_progress: { title: 'In Progress', color: '#3b82f6' },
  review: { title: 'Review', color: '#f59e0b' },
  done: { title: 'Done', color: '#22c55e' },
};

export const PRIORITY_CONFIG: Record<TaskPriority, { label: string; color: string; bgColor: string }> = {
  low: { label: 'Low', color: 'text-gray-600', bgColor: 'bg-gray-100' },
  medium: { label: 'Medium', color: 'text-blue-600', bgColor: 'bg-blue-100' },
  high: { label: 'High', color: 'text-orange-600', bgColor: 'bg-orange-100' },
  urgent: { label: 'Urgent', color: 'text-red-600', bgColor: 'bg-red-100' },
};
