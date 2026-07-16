import { useState, useEffect } from 'react';
import { ProjectOverview } from './ProjectOverview';
import { TeamMembers } from './TeamMembers';
import { TaskProgressChart } from './TaskProgressChart';
import { ActivityFeed } from './ActivityFeed';
import { QuickActions } from './QuickActions';
import { TimelineView } from './TimelineView';

interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: 'on-track' | 'at-risk' | 'delayed' | 'completed';
  dueDate: string;
  tasksCompleted: number;
  totalTasks: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

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

interface Activity {
  id: string;
  type: 'task_created' | 'task_completed' | 'comment' | 'mention' | 'file_upload' | 'status_change' | 'member_joined';
  user: { name: string; avatar: string };
  content: string;
  target?: string;
  timestamp: string;
  metadata?: { oldStatus?: string; newStatus?: string; fileName?: string; taskName?: string };
}

interface TeamDashboardProps {
  onBack?: () => void;
}

const sampleProjects: Project[] = [
  {
    id: '1',
    name: 'Website Redesign',
    description: 'Complete overhaul of the company website with modern UI/UX',
    progress: 75,
    status: 'on-track',
    dueDate: '2026-03-15',
    tasksCompleted: 45,
    totalTasks: 60,
    priority: 'high',
  },
  {
    id: '2',
    name: 'Mobile App Development',
    description: 'Native iOS and Android app for customer engagement',
    progress: 45,
    status: 'at-risk',
    dueDate: '2026-04-01',
    tasksCompleted: 27,
    totalTasks: 60,
    priority: 'critical',
  },
  {
    id: '3',
    name: 'API Integration',
    description: 'Third-party API integrations for payment and analytics',
    progress: 90,
    status: 'on-track',
    dueDate: '2026-03-01',
    tasksCompleted: 18,
    totalTasks: 20,
    priority: 'medium',
  },
  {
    id: '4',
    name: 'Documentation Update',
    description: 'Update all technical documentation and user guides',
    progress: 100,
    status: 'completed',
    dueDate: '2026-02-20',
    tasksCompleted: 15,
    totalTasks: 15,
    priority: 'low',
  },
  {
    id: '5',
    name: 'Security Audit',
    description: 'Comprehensive security review and penetration testing',
    progress: 30,
    status: 'delayed',
    dueDate: '2026-02-28',
    tasksCompleted: 6,
    totalTasks: 20,
    priority: 'critical',
  },
];

const sampleMembers: TeamMember[] = [
  { id: '1', name: 'Sarah Chen', role: 'Project Manager', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 12, tasksCompleted: 8, email: 'sarah@team.com' },
  { id: '2', name: 'Alex Rivera', role: 'Lead Developer', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 15, tasksCompleted: 12, email: 'alex@team.com' },
  { id: '3', name: 'Jordan Kim', role: 'UI/UX Designer', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face', status: 'away', tasksAssigned: 10, tasksCompleted: 7, email: 'jordan@team.com' },
  { id: '4', name: 'Taylor Morgan', role: 'Backend Developer', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face', status: 'busy', tasksAssigned: 8, tasksCompleted: 5, email: 'taylor@team.com' },
  { id: '5', name: 'Casey Johnson', role: 'QA Engineer', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 20, tasksCompleted: 18, email: 'casey@team.com' },
  { id: '6', name: 'Morgan Lee', role: 'DevOps Engineer', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face', status: 'offline', tasksAssigned: 6, tasksCompleted: 4, email: 'morgan@team.com' },
  { id: '7', name: 'Jamie Wilson', role: 'Frontend Developer', avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face', status: 'online', tasksAssigned: 14, tasksCompleted: 11, email: 'jamie@team.com' },
  { id: '8', name: 'Riley Brown', role: 'Data Analyst', avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&h=150&fit=crop&crop=face', status: 'away', tasksAssigned: 9, tasksCompleted: 6, email: 'riley@team.com' },
];

const sampleActivities: Activity[] = [
  { id: '1', type: 'task_completed', user: { name: 'Alex Rivera', avatar: sampleMembers[1].avatar }, content: 'completed task', target: 'Implement user authentication', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), metadata: { taskName: 'User Auth Module' } },
  { id: '2', type: 'comment', user: { name: 'Sarah Chen', avatar: sampleMembers[0].avatar }, content: 'commented on', target: 'API Integration', timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString() },
  { id: '3', type: 'task_created', user: { name: 'Jordan Kim', avatar: sampleMembers[2].avatar }, content: 'created new task', target: 'Design mobile navigation', timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString() },
  { id: '4', type: 'file_upload', user: { name: 'Taylor Morgan', avatar: sampleMembers[3].avatar }, content: 'uploaded', target: 'api-docs-v2.pdf', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), metadata: { fileName: 'api-docs-v2.pdf' } },
  { id: '5', type: 'status_change', user: { name: 'Casey Johnson', avatar: sampleMembers[4].avatar }, content: 'changed status of', target: 'Security Review', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), metadata: { oldStatus: 'In Progress', newStatus: 'In Review' } },
  { id: '6', type: 'mention', user: { name: 'Morgan Lee', avatar: sampleMembers[5].avatar }, content: 'mentioned you in', target: 'Deployment Pipeline', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString() },
  { id: '7', type: 'member_joined', user: { name: 'Jamie Wilson', avatar: sampleMembers[6].avatar }, content: 'joined the team', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() },
  { id: '8', type: 'task_completed', user: { name: 'Riley Brown', avatar: sampleMembers[7].avatar }, content: 'completed task', target: 'Data migration script', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString() },
];

const taskStats = [
  { label: 'Completed', value: 111, color: '#22c55e', percentage: 45 },
  { label: 'In Progress', value: 74, color: '#3b82f6', percentage: 30 },
  { label: 'In Review', value: 37, color: '#f59e0b', percentage: 15 },
  { label: 'To Do', value: 25, color: '#6b7280', percentage: 10 },
];

const weeklyProgress = [
  { day: 'Mon', completed: 12, created: 8 },
  { day: 'Tue', completed: 15, created: 10 },
  { day: 'Wed', completed: 8, created: 12 },
  { day: 'Thu', completed: 20, created: 6 },
  { day: 'Fri', completed: 18, created: 14 },
  { day: 'Sat', completed: 5, created: 2 },
  { day: 'Sun', completed: 3, created: 1 },
];

const sampleMilestones = [
  {
    id: '1',
    title: 'Project Kickoff',
    date: '2026-01-15',
    status: 'completed' as const,
    description: 'Initial project planning and team alignment meeting',
    assignee: { name: 'Sarah Chen', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face' },
  },
  {
    id: '2',
    title: 'Design Phase Complete',
    date: '2026-02-01',
    status: 'completed' as const,
    description: 'All UI/UX designs approved and ready for development',
    assignee: { name: 'Jordan Kim', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face' },
  },
  {
    id: '3',
    title: 'Backend API Ready',
    date: '2026-02-20',
    status: 'in-progress' as const,
    description: 'Core API endpoints implemented and tested',
    assignee: { name: 'Taylor Morgan', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face' },
  },
  {
    id: '4',
    title: 'Beta Release',
    date: '2026-03-10',
    status: 'upcoming' as const,
    description: 'Internal beta testing with select users',
    assignee: { name: 'Casey Johnson', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face' },
  },
  {
    id: '5',
    title: 'Production Launch',
    date: '2026-03-25',
    status: 'upcoming' as const,
    description: 'Full production deployment and public release',
    assignee: { name: 'Alex Rivera', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face' },
  },
];

export function TeamDashboard({ onBack }: TeamDashboardProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [selectedProject, setSelectedProject] = useState<string | undefined>();
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleQuickAction = (actionId: string) => {
    const actionMessages: Record<string, string> = {
      'new-task': 'Creating new task...',
      'new-project': 'Creating new project...',
      'invite-member': 'Opening invite dialog...',
      'schedule-meeting': 'Opening calendar...',
      'upload-file': 'Opening file picker...',
      'generate-report': 'Generating report...',
    };
    setNotification(actionMessages[actionId] || 'Action triggered');
    setTimeout(() => setNotification(null), 3000);
  };

  const handleMemberClick = (memberId: string) => {
    const member = sampleMembers.find((m) => m.id === memberId);
    if (member) {
      setNotification(`Viewing ${member.name}'s profile`);
      setTimeout(() => setNotification(null), 3000);
    }
  };

  return (
    <div className={`min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-300`}>
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              {onBack && (
                <button
                  onClick={onBack}
                  className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Go back"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </button>
              )}
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Team Dashboard</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Collaboration Hub</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>

              <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>

              <img
                src={sampleMembers[0].avatar}
                alt="Profile"
                className="w-8 h-8 rounded-full object-cover ring-2 ring-gray-200 dark:ring-gray-700"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Notification Toast */}
      {notification && (
        <div className="fixed top-20 right-4 z-50 bg-gray-900 dark:bg-gray-700 text-white px-4 py-3 rounded-lg shadow-lg animate-slide-in">
          {notification}
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Projects & Activity */}
          <div className="lg:col-span-2 space-y-6">
            <ProjectOverview
              projects={sampleProjects}
              onProjectSelect={setSelectedProject}
              selectedProjectId={selectedProject}
            />
            <TaskProgressChart
              taskStats={taskStats}
              weeklyProgress={weeklyProgress}
              totalTasks={247}
              completedTasks={111}
            />
            <ActivityFeed
              activities={sampleActivities}
              onActivityClick={(id) => console.log('Activity clicked:', id)}
            />
            <TimelineView
              milestones={sampleMilestones}
              onMilestoneClick={(id) => console.log('Milestone clicked:', id)}
            />
          </div>

          {/* Right Column - Team & Actions */}
          <div className="space-y-6">
            <TeamMembers
              members={sampleMembers}
              onMemberClick={handleMemberClick}
            />
            <QuickActions onAction={handleQuickAction} />

            {/* Upcoming Deadlines */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Upcoming Deadlines
              </h2>
              <div className="space-y-3">
                {sampleProjects
                  .filter((p) => p.status !== 'completed')
                  .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime())
                  .slice(0, 3)
                  .map((project) => {
                    const daysLeft = Math.ceil(
                      (new Date(project.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
                    );
                    return (
                      <div
                        key={project.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
                      >
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white text-sm">
                            {project.name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(project.dueDate).toLocaleDateString()}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full
                            ${daysLeft <= 3
                              ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                              : daysLeft <= 7
                              ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                              : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                            }`}
                        >
                          {daysLeft} days left
                        </span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
