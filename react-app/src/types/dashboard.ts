export type TaskPriority = 'low' | 'medium' | 'high';
export type TaskStatus = 'todo' | 'in_progress' | 'completed';

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate: string;
  assignee?: {
    name: string;
    avatar: string;
  };
  tags: string[];
}

export interface StatisticItem {
  id: string;
  label: string;
  value: number;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon: 'tasks' | 'completed' | 'pending' | 'overdue';
}

export interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  badge?: number;
}

export interface DashboardUser {
  name: string;
  email: string;
  avatar: string;
  role: string;
}
