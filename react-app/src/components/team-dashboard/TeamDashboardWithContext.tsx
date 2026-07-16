import { useState } from 'react';
import { ProjectOverview } from './ProjectOverview';
import { TeamMembers } from './TeamMembers';
import { TaskProgressChart } from './TaskProgressChart';
import { ActivityFeed } from './ActivityFeed';
import { QuickActions } from './QuickActions';
import { TimelineView } from './TimelineView';
import { KanbanBoardAdvanced } from './kanban';
import { DashboardProvider, TaskProvider, TeamProvider, useDashboard, useTask, useTeam } from './context';

interface TeamDashboardProps {
  onBack?: () => void;
}

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

const weeklyProgress = [
  { day: 'Mon', completed: 12, created: 8 },
  { day: 'Tue', completed: 15, created: 10 },
  { day: 'Wed', completed: 8, created: 12 },
  { day: 'Thu', completed: 20, created: 6 },
  { day: 'Fri', completed: 18, created: 14 },
  { day: 'Sat', completed: 5, created: 2 },
  { day: 'Sun', completed: 3, created: 1 },
];

function DashboardContent({ onBack }: TeamDashboardProps) {
  const { isDarkMode, toggleDarkMode, user, showNotification, notification } = useDashboard();
  const { projects, activities, taskStats, completeTask, addActivity, tasks } = useTask();
  const { members, addMember, getMemberById } = useTeam();
  const [selectedProject, setSelectedProject] = useState<string | undefined>();

  const handleQuickAction = (actionId: string) => {
    switch (actionId) {
      case 'new-task':
        showNotification('Creating new task...');
        break;
      case 'new-project':
        showNotification('Creating new project...');
        break;
      case 'invite-member':
        // Simulate adding a member
        addMember({
          name: 'New Member',
          role: 'Developer',
          avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face',
          status: 'online',
          email: 'new@team.com',
        });
        addActivity({
          type: 'member_joined',
          user: { name: 'New Member', avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face' },
          content: 'joined the team',
        });
        showNotification('New team member added!');
        break;
      case 'schedule-meeting':
        showNotification('Opening calendar...');
        break;
      case 'upload-file':
        showNotification('Opening file picker...');
        break;
      case 'generate-report':
        showNotification('Generating report...');
        break;
      default:
        showNotification('Action triggered');
    }
  };

  const handleMemberClick = (memberId: string) => {
    const member = getMemberById(memberId);
    if (member) {
      showNotification(`Viewing ${member.name}'s profile`);
    }
  };

  const handleCompleteTask = () => {
    const incompleteTasks = tasks.filter((t) => t.status !== 'completed');
    if (incompleteTasks.length > 0 && user) {
      const task = incompleteTasks[0];
      completeTask(task.id, user.name, user.avatar);
      showNotification(`Task "${task.title}" completed!`);
    }
  };

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.status === 'completed').length;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
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
              {/* Demo: Complete Task Button */}
              <button
                onClick={handleCompleteTask}
                className="px-3 py-1.5 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Complete Task
              </button>

              <button
                onClick={toggleDarkMode}
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

              {user && (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="w-8 h-8 rounded-full object-cover ring-2 ring-gray-200 dark:ring-gray-700"
                />
              )}
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
              projects={projects}
              onProjectSelect={setSelectedProject}
              selectedProjectId={selectedProject}
            />
            <TaskProgressChart
              taskStats={taskStats}
              weeklyProgress={weeklyProgress}
              totalTasks={totalTasks}
              completedTasks={completedTasks}
            />
            <ActivityFeed
              activities={activities}
              onActivityClick={(id) => console.log('Activity clicked:', id)}
            />
            <TimelineView
              milestones={sampleMilestones}
              onMilestoneClick={(id) => console.log('Milestone clicked:', id)}
            />
            <KanbanBoardAdvanced
              onTaskChange={() => {
                showNotification('Tasks updated');
              }}
            />
          </div>

          {/* Right Column - Team & Actions */}
          <div className="space-y-6">
            <TeamMembers
              members={members}
              onMemberClick={handleMemberClick}
            />
            <QuickActions onAction={handleQuickAction} />

            {/* Upcoming Deadlines */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Upcoming Deadlines
              </h2>
              <div className="space-y-3">
                {projects
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

export function TeamDashboardWithContext({ onBack }: TeamDashboardProps) {
  return (
    <DashboardProvider>
      <TaskProvider>
        <TeamProvider>
          <DashboardContent onBack={onBack} />
        </TeamProvider>
      </TaskProvider>
    </DashboardProvider>
  );
}
