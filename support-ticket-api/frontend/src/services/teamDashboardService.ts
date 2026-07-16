import type { TeamMember } from '../components/types/team';
import type { Project, ProjectStats, Task } from '../components/types/project';
import type { Activity } from '../components/types/activity';

const mockMembers: TeamMember[] = [
  { id: 1, name: 'Sarah Johnson', email: 'sarah@example.com', role: 'admin', status: 'online', department: 'Engineering', tasksCompleted: 45, tasksInProgress: 3 },
  { id: 2, name: 'Michael Chen', email: 'michael@example.com', role: 'developer', status: 'online', department: 'Engineering', tasksCompleted: 38, tasksInProgress: 5 },
  { id: 3, name: 'Emily Davis', email: 'emily@example.com', role: 'designer', status: 'away', department: 'Design', tasksCompleted: 29, tasksInProgress: 2 },
  { id: 4, name: 'James Wilson', email: 'james@example.com', role: 'developer', status: 'online', department: 'Engineering', tasksCompleted: 52, tasksInProgress: 4 },
  { id: 5, name: 'Lisa Anderson', email: 'lisa@example.com', role: 'manager', status: 'busy', department: 'Product', tasksCompleted: 31, tasksInProgress: 6 },
  { id: 6, name: 'David Brown', email: 'david@example.com', role: 'qa', status: 'offline', department: 'QA', tasksCompleted: 67, tasksInProgress: 8 },
  { id: 7, name: 'Anna Martinez', email: 'anna@example.com', role: 'designer', status: 'online', department: 'Design', tasksCompleted: 24, tasksInProgress: 3 },
  { id: 8, name: 'Robert Taylor', email: 'robert@example.com', role: 'developer', status: 'online', department: 'Engineering', tasksCompleted: 41, tasksInProgress: 2 },
];

const createTasks = (count: number, projectId: number): Task[] => {
  const statuses: Task['status'][] = ['todo', 'in_progress', 'review', 'done'];
  const priorities: Task['priority'][] = ['low', 'medium', 'high', 'urgent'];
  const taskNames = [
    'Implement user authentication',
    'Design landing page',
    'Set up CI/CD pipeline',
    'Write unit tests',
    'Create API documentation',
    'Optimize database queries',
    'Review pull requests',
    'Update dependencies',
    'Fix responsive layout',
    'Add error handling',
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: projectId * 100 + i + 1,
    title: taskNames[i % taskNames.length],
    description: `Task description for ${taskNames[i % taskNames.length]}`,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    priority: priorities[Math.floor(Math.random() * priorities.length)],
    assignee: mockMembers[Math.floor(Math.random() * mockMembers.length)],
    dueDate: new Date(Date.now() + Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['frontend', 'backend', 'design', 'testing'].slice(0, Math.floor(Math.random() * 3) + 1),
  }));
};

const mockProjects: Project[] = [
  {
    id: 1,
    name: 'Website Redesign',
    description: 'Complete overhaul of the company website with modern design and improved UX',
    status: 'in_progress',
    progress: 65,
    startDate: '2024-01-15',
    endDate: '2024-04-30',
    tasks: createTasks(12, 1),
    members: mockMembers.slice(0, 5),
    color: '#3b82f6',
  },
  {
    id: 2,
    name: 'Mobile App Development',
    description: 'Native mobile application for iOS and Android platforms',
    status: 'in_progress',
    progress: 40,
    startDate: '2024-02-01',
    endDate: '2024-06-30',
    tasks: createTasks(18, 2),
    members: mockMembers.slice(1, 6),
    color: '#8b5cf6',
  },
  {
    id: 3,
    name: 'API Integration',
    description: 'Third-party API integrations for payment and analytics',
    status: 'review',
    progress: 85,
    startDate: '2024-01-01',
    endDate: '2024-03-15',
    tasks: createTasks(8, 3),
    members: mockMembers.slice(3, 7),
    color: '#22c55e',
  },
  {
    id: 4,
    name: 'Security Audit',
    description: 'Comprehensive security review and vulnerability assessment',
    status: 'planning',
    progress: 15,
    startDate: '2024-03-01',
    endDate: '2024-04-15',
    tasks: createTasks(6, 4),
    members: mockMembers.slice(5, 8),
    color: '#ef4444',
  },
  {
    id: 5,
    name: 'Documentation Update',
    description: 'Update all technical documentation and user guides',
    status: 'completed',
    progress: 100,
    startDate: '2024-01-10',
    endDate: '2024-02-28',
    tasks: createTasks(10, 5),
    members: mockMembers.slice(0, 3),
    color: '#f59e0b',
  },
];

const mockActivities: Activity[] = [
  { id: 1, type: 'task_completed', user: mockMembers[0], description: 'completed "Implement user authentication"', projectName: 'Website Redesign', taskName: 'Implement user authentication', timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString() },
  { id: 2, type: 'comment_added', user: mockMembers[1], description: 'commented on "Design landing page"', projectName: 'Website Redesign', taskName: 'Design landing page', timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString() },
  { id: 3, type: 'task_assigned', user: mockMembers[4], description: 'assigned "Set up CI/CD pipeline" to Michael Chen', projectName: 'Mobile App Development', taskName: 'Set up CI/CD pipeline', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: 4, type: 'file_uploaded', user: mockMembers[2], description: 'uploaded design mockups', projectName: 'Website Redesign', timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString() },
  { id: 5, type: 'status_changed', user: mockMembers[3], description: 'changed status of "API Integration" to Review', projectName: 'API Integration', timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString() },
  { id: 6, type: 'member_joined', user: mockMembers[7], description: 'joined the team', timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString() },
  { id: 7, type: 'task_created', user: mockMembers[4], description: 'created "Review pull requests"', projectName: 'Mobile App Development', taskName: 'Review pull requests', timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString() },
  { id: 8, type: 'deadline_updated', user: mockMembers[0], description: 'updated deadline for "Security Audit"', projectName: 'Security Audit', timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() },
  { id: 9, type: 'project_created', user: mockMembers[4], description: 'created new project "Q2 Marketing Campaign"', projectName: 'Q2 Marketing Campaign', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() },
  { id: 10, type: 'task_completed', user: mockMembers[5], description: 'completed "Write unit tests"', projectName: 'API Integration', taskName: 'Write unit tests', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
];

const calculateStats = (projects: Project[]): ProjectStats => {
  const allTasks = projects.flatMap(p => p.tasks);
  const now = new Date();
  
  return {
    totalTasks: allTasks.length,
    completedTasks: allTasks.filter(t => t.status === 'done').length,
    inProgressTasks: allTasks.filter(t => t.status === 'in_progress').length,
    overdueTasks: allTasks.filter(t => t.dueDate && new Date(t.dueDate) < now && t.status !== 'done').length,
    upcomingDeadlines: allTasks.filter(t => {
      if (!t.dueDate) return false;
      const dueDate = new Date(t.dueDate);
      const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      return dueDate > now && dueDate <= weekFromNow;
    }).length,
  };
};

const generateWeeklyProgress = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map(label => ({
    label,
    completed: Math.floor(Math.random() * 15) + 5,
    total: Math.floor(Math.random() * 10) + 15,
  }));
};

export const teamDashboardService = {
  getDashboardData: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      projects: mockProjects,
      stats: calculateStats(mockProjects),
      members: mockMembers,
      activities: mockActivities,
      weeklyProgress: generateWeeklyProgress(),
    };
  },

  getProjects: async () => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockProjects;
  },

  getMembers: async () => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockMembers;
  },

  getActivities: async () => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockActivities;
  },
};
