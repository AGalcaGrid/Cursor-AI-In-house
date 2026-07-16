import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  tasksAssigned: number;
  tasksCompleted: number;
  email: string;
}

interface TeamContextType {
  members: TeamMember[];
  addMember: (member: Omit<TeamMember, 'id' | 'tasksAssigned' | 'tasksCompleted'>) => void;
  removeMember: (memberId: string) => void;
  updateMemberStatus: (memberId: string, status: TeamMember['status']) => void;
  incrementMemberTasks: (memberId: string, type: 'assigned' | 'completed') => void;
  getMemberById: (memberId: string) => TeamMember | undefined;
  getOnlineCount: () => number;
}

const TeamContext = createContext<TeamContextType | undefined>(undefined);

const initialMembers: TeamMember[] = [
  { id: '1', name: 'Sarah Chen', role: 'Project Manager', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 12, tasksCompleted: 8, email: 'sarah@team.com' },
  { id: '2', name: 'Alex Rivera', role: 'Lead Developer', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 15, tasksCompleted: 12, email: 'alex@team.com' },
  { id: '3', name: 'Jordan Kim', role: 'UI/UX Designer', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face', status: 'away', tasksAssigned: 10, tasksCompleted: 7, email: 'jordan@team.com' },
  { id: '4', name: 'Taylor Morgan', role: 'Backend Developer', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face', status: 'busy', tasksAssigned: 8, tasksCompleted: 5, email: 'taylor@team.com' },
  { id: '5', name: 'Casey Johnson', role: 'QA Engineer', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 20, tasksCompleted: 18, email: 'casey@team.com' },
  { id: '6', name: 'Morgan Lee', role: 'DevOps Engineer', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face', status: 'offline', tasksAssigned: 6, tasksCompleted: 4, email: 'morgan@team.com' },
  { id: '7', name: 'Jamie Wilson', role: 'Frontend Developer', avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 14, tasksCompleted: 11, email: 'jamie@team.com' },
  { id: '8', name: 'Riley Brown', role: 'Data Analyst', avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&h=150&fit=crop&crop=face', status: 'away', tasksAssigned: 9, tasksCompleted: 6, email: 'riley@team.com' },
];

interface TeamProviderProps {
  children: ReactNode;
  onMemberAdded?: (member: TeamMember) => void;
}

export function TeamProvider({ children, onMemberAdded }: TeamProviderProps) {
  const [members, setMembers] = useState<TeamMember[]>(initialMembers);

  const addMember = (memberData: Omit<TeamMember, 'id' | 'tasksAssigned' | 'tasksCompleted'>) => {
    const newMember: TeamMember = {
      ...memberData,
      id: Date.now().toString(),
      tasksAssigned: 0,
      tasksCompleted: 0,
    };
    setMembers((prev) => [...prev, newMember]);
    onMemberAdded?.(newMember);
  };

  const removeMember = (memberId: string) => {
    setMembers((prev) => prev.filter((m) => m.id !== memberId));
  };

  const updateMemberStatus = (memberId: string, status: TeamMember['status']) => {
    setMembers((prev) =>
      prev.map((m) => (m.id === memberId ? { ...m, status } : m))
    );
  };

  const incrementMemberTasks = (memberId: string, type: 'assigned' | 'completed') => {
    setMembers((prev) =>
      prev.map((m) => {
        if (m.id === memberId) {
          return type === 'assigned'
            ? { ...m, tasksAssigned: m.tasksAssigned + 1 }
            : { ...m, tasksCompleted: m.tasksCompleted + 1 };
        }
        return m;
      })
    );
  };

  const getMemberById = (memberId: string) => members.find((m) => m.id === memberId);

  const getOnlineCount = () => members.filter((m) => m.status === 'online').length;

  return (
    <TeamContext.Provider
      value={{
        members,
        addMember,
        removeMember,
        updateMemberStatus,
        incrementMemberTasks,
        getMemberById,
        getOnlineCount,
      }}
    >
      {children}
    </TeamContext.Provider>
  );
}

export function useTeam() {
  const context = useContext(TeamContext);
  if (context === undefined) {
    throw new Error('useTeam must be used within a TeamProvider');
  }
  return context;
}
