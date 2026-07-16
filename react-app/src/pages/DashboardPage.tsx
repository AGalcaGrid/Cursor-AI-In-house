import { useState } from 'react';
import { Dashboard } from '../components/dashboard';
import type { Task, StatisticItem, DashboardUser } from '../types/dashboard';

const dashboardUser: DashboardUser = {
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
  role: 'Product Manager',
};

const initialTasks: Task[] = [
  {
    id: '1',
    title: 'Design new landing page',
    description: 'Create wireframes and mockups for the new marketing landing page with modern design.',
    priority: 'high',
    status: 'in_progress',
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    assignee: {
      name: 'Sarah Chen',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face',
    },
    tags: ['Design', 'Marketing'],
  },
  {
    id: '2',
    title: 'Implement user authentication',
    description: 'Set up OAuth 2.0 authentication with Google and GitHub providers.',
    priority: 'high',
    status: 'todo',
    dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    assignee: {
      name: 'Alex Rivera',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    },
    tags: ['Backend', 'Security'],
  },
  {
    id: '3',
    title: 'Write API documentation',
    description: 'Document all REST API endpoints with examples and response schemas.',
    priority: 'medium',
    status: 'todo',
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['Documentation'],
  },
  {
    id: '4',
    title: 'Fix mobile navigation bug',
    description: 'Navigation menu not closing properly on mobile devices after clicking a link.',
    priority: 'medium',
    status: 'in_progress',
    dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
    assignee: {
      name: 'John Doe',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    },
    tags: ['Bug', 'Mobile'],
  },
  {
    id: '5',
    title: 'Set up CI/CD pipeline',
    description: 'Configure GitHub Actions for automated testing and deployment.',
    priority: 'high',
    status: 'completed',
    dueDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    assignee: {
      name: 'Alex Rivera',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    },
    tags: ['DevOps'],
  },
  {
    id: '6',
    title: 'Review pull requests',
    description: 'Review and merge pending pull requests from team members.',
    priority: 'low',
    status: 'completed',
    dueDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['Code Review'],
  },
  {
    id: '7',
    title: 'Update dependencies',
    description: 'Update all npm packages to their latest stable versions.',
    priority: 'low',
    status: 'todo',
    dueDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['Maintenance'],
  },
  {
    id: '8',
    title: 'Performance optimization',
    description: 'Analyze and optimize bundle size and loading performance.',
    priority: 'medium',
    status: 'todo',
    dueDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(),
    assignee: {
      name: 'Emma Wilson',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    },
    tags: ['Performance', 'Frontend'],
  },
];

const initialStatistics: StatisticItem[] = [
  { id: '1', label: 'Total Tasks', value: 24, change: 12, changeType: 'increase', icon: 'tasks' },
  { id: '2', label: 'Completed', value: 18, change: 8, changeType: 'increase', icon: 'completed' },
  { id: '3', label: 'In Progress', value: 4, change: 2, changeType: 'decrease', icon: 'pending' },
  { id: '4', label: 'Overdue', value: 2, change: 1, changeType: 'increase', icon: 'overdue' },
];

export function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);

  const handleTaskStatusChange = (taskId: string, status: Task['status']) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, status } : task
      )
    );
  };

  const handleTaskEdit = (task: Task) => {
    alert(`Editing task: ${task.title}`);
  };

  const handleTaskDelete = (taskId: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    }
  };

  const handleLogout = () => {
    alert('Logging out...');
  };

  return (
    <Dashboard
      user={dashboardUser}
      tasks={tasks}
      statistics={initialStatistics}
      onTaskStatusChange={handleTaskStatusChange}
      onTaskEdit={handleTaskEdit}
      onTaskDelete={handleTaskDelete}
      onLogout={handleLogout}
    />
  );
}
