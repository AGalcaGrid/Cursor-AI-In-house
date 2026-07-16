export interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: ProjectStatus;
  dueDate: string;
  tasksCompleted: number;
  totalTasks: number;
  priority: ProjectPriority;
  createdAt?: string;
  updatedAt?: string;
  teamId?: string;
}

export type ProjectStatus = 'on-track' | 'at-risk' | 'delayed' | 'completed';

export type ProjectPriority = 'low' | 'medium' | 'high' | 'critical';

export interface TaskStats {
  label: string;
  value: number;
  color: string;
  percentage: number;
}

export interface WeeklyProgress {
  day: string;
  completed: number;
  created: number;
}
