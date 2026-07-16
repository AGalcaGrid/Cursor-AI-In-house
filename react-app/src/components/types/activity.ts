export interface Activity {
  id: string;
  type: ActivityType;
  user: ActivityUser;
  content: string;
  target?: string;
  timestamp: string;
  metadata?: ActivityMetadata;
}

export interface ActivityUser {
  name: string;
  avatar: string;
}

export interface ActivityMetadata {
  oldStatus?: string;
  newStatus?: string;
  fileName?: string;
  taskName?: string;
  projectId?: string;
}

export type ActivityType =
  | 'task_created'
  | 'task_completed'
  | 'comment'
  | 'mention'
  | 'file_upload'
  | 'status_change'
  | 'member_joined';
