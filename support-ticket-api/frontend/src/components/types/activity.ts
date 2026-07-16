import type { TeamMember } from './team';

export type ActivityType = 
  | 'task_created'
  | 'task_completed'
  | 'task_assigned'
  | 'comment_added'
  | 'project_created'
  | 'member_joined'
  | 'file_uploaded'
  | 'status_changed'
  | 'deadline_updated';

export interface Activity {
  id: number;
  type: ActivityType;
  user: TeamMember;
  description: string;
  projectName?: string;
  taskName?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ActivityGroup {
  date: string;
  activities: Activity[];
}
