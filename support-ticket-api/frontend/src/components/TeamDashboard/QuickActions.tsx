import { Card, CardHeader, CardBody } from '../shared/Card';
import { 
  Plus, 
  FolderPlus, 
  UserPlus, 
  FileText, 
  Calendar,
  MessageSquare,
  Settings,
  BarChart3
} from 'lucide-react';

interface QuickAction {
  id: string;
  label: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  onClick?: () => void;
}

interface QuickActionsProps {
  onCreateTask?: () => void;
  onCreateProject?: () => void;
  onInviteMember?: () => void;
  onGenerateReport?: () => void;
  onScheduleMeeting?: () => void;
  onOpenChat?: () => void;
  onOpenSettings?: () => void;
  onViewAnalytics?: () => void;
}

export default function QuickActions({
  onCreateTask,
  onCreateProject,
  onInviteMember,
  onGenerateReport,
  onScheduleMeeting,
  onOpenChat,
  onOpenSettings,
  onViewAnalytics,
}: QuickActionsProps) {
  const actions: QuickAction[] = [
    {
      id: 'create-task',
      label: 'New Task',
      icon: Plus,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50 hover:bg-blue-100',
      onClick: onCreateTask,
    },
    {
      id: 'create-project',
      label: 'New Project',
      icon: FolderPlus,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50 hover:bg-purple-100',
      onClick: onCreateProject,
    },
    {
      id: 'invite-member',
      label: 'Invite Member',
      icon: UserPlus,
      color: 'text-green-600',
      bgColor: 'bg-green-50 hover:bg-green-100',
      onClick: onInviteMember,
    },
    {
      id: 'generate-report',
      label: 'Generate Report',
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50 hover:bg-orange-100',
      onClick: onGenerateReport,
    },
    {
      id: 'schedule-meeting',
      label: 'Schedule Meeting',
      icon: Calendar,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50 hover:bg-pink-100',
      onClick: onScheduleMeeting,
    },
    {
      id: 'open-chat',
      label: 'Team Chat',
      icon: MessageSquare,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-50 hover:bg-cyan-100',
      onClick: onOpenChat,
    },
    {
      id: 'view-analytics',
      label: 'Analytics',
      icon: BarChart3,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50 hover:bg-indigo-100',
      onClick: onViewAnalytics,
    },
    {
      id: 'open-settings',
      label: 'Settings',
      icon: Settings,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50 hover:bg-gray-100',
      onClick: onOpenSettings,
    },
  ];

  return (
    <Card padding="none">
      <CardHeader className="px-5 pt-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          <p className="text-sm text-gray-500 mt-1">Shortcuts to common tasks</p>
        </div>
      </CardHeader>
      <CardBody className="px-5 pb-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {actions.map((action) => (
            <button
              key={action.id}
              onClick={action.onClick}
              className={`flex flex-col items-center gap-2 p-4 rounded-xl ${action.bgColor} transition-colors`}
            >
              <action.icon className={`w-6 h-6 ${action.color}`} />
              <span className="text-sm font-medium text-gray-700">{action.label}</span>
            </button>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
