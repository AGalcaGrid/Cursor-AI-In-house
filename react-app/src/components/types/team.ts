export interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  tasksAssigned: number;
  tasksCompleted: number;
  email: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  members: TeamMember[];
  createdAt: string;
  updatedAt: string;
}

export type MemberStatus = 'online' | 'away' | 'busy' | 'offline';
