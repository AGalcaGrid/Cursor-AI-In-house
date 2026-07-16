import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in-progress' | 'in-review' | 'completed';
  assigneeId: string;
  projectId: string;
  createdAt: string;
  completedAt?: string;
}

interface TaskStats {
  label: string;
  value: number;
  color: string;
  percentage: number;
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

interface TaskContextType {
  tasks: Task[];
  projects: Project[];
  activities: Activity[];
  taskStats: TaskStats[];
  addTask: (task: Omit<Task, 'id' | 'createdAt'>) => void;
  completeTask: (taskId: string, userName: string, userAvatar: string) => void;
  updateTaskStatus: (taskId: string, status: Task['status']) => void;
  addActivity: (activity: Omit<Activity, 'id' | 'timestamp'>) => void;
  getProjectStats: () => { total: number; completed: number; inProgress: number; atRisk: number };
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

const initialTasks: Task[] = [
  { id: '1', title: 'Implement user authentication', status: 'completed', assigneeId: '2', projectId: '1', createdAt: '2026-02-01T10:00:00Z', completedAt: '2026-02-15T14:00:00Z' },
  { id: '2', title: 'Design mobile navigation', status: 'in-progress', assigneeId: '3', projectId: '2', createdAt: '2026-02-10T09:00:00Z' },
  { id: '3', title: 'API endpoint testing', status: 'in-review', assigneeId: '5', projectId: '3', createdAt: '2026-02-12T11:00:00Z' },
  { id: '4', title: 'Database optimization', status: 'todo', assigneeId: '4', projectId: '1', createdAt: '2026-02-20T08:00:00Z' },
];

const initialProjects: Project[] = [
  { id: '1', name: 'Website Redesign', description: 'Complete overhaul of the company website', progress: 75, status: 'on-track', dueDate: '2026-03-15', tasksCompleted: 45, totalTasks: 60, priority: 'high' },
  { id: '2', name: 'Mobile App Development', description: 'Native iOS and Android app', progress: 45, status: 'at-risk', dueDate: '2026-04-01', tasksCompleted: 27, totalTasks: 60, priority: 'critical' },
  { id: '3', name: 'API Integration', description: 'Third-party API integrations', progress: 90, status: 'on-track', dueDate: '2026-03-01', tasksCompleted: 18, totalTasks: 20, priority: 'medium' },
  { id: '4', name: 'Documentation Update', description: 'Update technical documentation', progress: 100, status: 'completed', dueDate: '2026-02-20', tasksCompleted: 15, totalTasks: 15, priority: 'low' },
  { id: '5', name: 'Security Audit', description: 'Security review and testing', progress: 30, status: 'delayed', dueDate: '2026-02-28', tasksCompleted: 6, totalTasks: 20, priority: 'critical' },
];

const initialActivities: Activity[] = [
  { id: '1', type: 'task_completed', user: { name: 'Alex Rivera', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face' }, content: 'completed task', target: 'Implement user authentication', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString() },
  { id: '2', type: 'comment', user: { name: 'Sarah Chen', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face' }, content: 'commented on', target: 'API Integration', timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString() },
  { id: '3', type: 'task_created', user: { name: 'Jordan Kim', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face' }, content: 'created new task', target: 'Design mobile navigation', timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString() },
];

export function TaskProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [projects, setProjects] = useState<Project[]>(initialProjects);
  const [activities, setActivities] = useState<Activity[]>(initialActivities);

  const calculateTaskStats = (): TaskStats[] => {
    const completed = tasks.filter((t) => t.status === 'completed').length;
    const inProgress = tasks.filter((t) => t.status === 'in-progress').length;
    const inReview = tasks.filter((t) => t.status === 'in-review').length;
    const todo = tasks.filter((t) => t.status === 'todo').length;
    const total = tasks.length || 1;

    return [
      { label: 'Completed', value: completed, color: '#22c55e', percentage: Math.round((completed / total) * 100) },
      { label: 'In Progress', value: inProgress, color: '#3b82f6', percentage: Math.round((inProgress / total) * 100) },
      { label: 'In Review', value: inReview, color: '#f59e0b', percentage: Math.round((inReview / total) * 100) },
      { label: 'To Do', value: todo, color: '#6b7280', percentage: Math.round((todo / total) * 100) },
    ];
  };

  const addTask = (taskData: Omit<Task, 'id' | 'createdAt'>) => {
    const newTask: Task = {
      ...taskData,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
    };
    setTasks((prev) => [...prev, newTask]);

    // Update project task count
    setProjects((prev) =>
      prev.map((p) =>
        p.id === taskData.projectId ? { ...p, totalTasks: p.totalTasks + 1 } : p
      )
    );
  };

  const completeTask = (taskId: string, userName: string, userAvatar: string) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // Update task status
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, status: 'completed' as const, completedAt: new Date().toISOString() } : t
      )
    );

    // Update project progress
    setProjects((prev) =>
      prev.map((p) => {
        if (p.id === task.projectId) {
          const newCompleted = p.tasksCompleted + 1;
          const newProgress = Math.round((newCompleted / p.totalTasks) * 100);
          return {
            ...p,
            tasksCompleted: newCompleted,
            progress: newProgress,
            status: newProgress >= 100 ? 'completed' as const : p.status,
          };
        }
        return p;
      })
    );

    // Add activity
    const newActivity: Activity = {
      id: Date.now().toString(),
      type: 'task_completed',
      user: { name: userName, avatar: userAvatar },
      content: 'completed task',
      target: task.title,
      timestamp: new Date().toISOString(),
      metadata: { taskName: task.title },
    };
    setActivities((prev) => [newActivity, ...prev]);
  };

  const updateTaskStatus = (taskId: string, status: Task['status']) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status } : t))
    );
  };

  const addActivity = (activityData: Omit<Activity, 'id' | 'timestamp'>) => {
    const newActivity: Activity = {
      ...activityData,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };
    setActivities((prev) => [newActivity, ...prev]);
  };

  const getProjectStats = () => ({
    total: projects.length,
    completed: projects.filter((p) => p.status === 'completed').length,
    inProgress: projects.filter((p) => p.status !== 'completed').length,
    atRisk: projects.filter((p) => p.status === 'at-risk' || p.status === 'delayed').length,
  });

  return (
    <TaskContext.Provider
      value={{
        tasks,
        projects,
        activities,
        taskStats: calculateTaskStats(),
        addTask,
        completeTask,
        updateTaskStatus,
        addActivity,
        getProjectStats,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
}

export function useTask() {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
}
