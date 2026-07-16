export interface TeamMember {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'manager' | 'developer' | 'designer' | 'qa';
  status: 'online' | 'offline' | 'away' | 'busy';
  department: string;
  tasksCompleted: number;
  tasksInProgress: number;
}

export interface Team {
  id: number;
  name: string;
  description: string;
  members: TeamMember[];
  createdAt: string;
}
