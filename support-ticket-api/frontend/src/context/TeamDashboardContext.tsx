import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { TeamMember } from '../components/types/team';
import type { Project, ProjectStats, Task } from '../components/types/project';
import type { Activity } from '../components/types/activity';
import { teamDashboardService } from '../services/teamDashboardService';

interface DashboardData {
  projects: Project[];
  stats: ProjectStats;
  members: TeamMember[];
  activities: Activity[];
  weeklyProgress: { label: string; completed: number; total: number }[];
}

interface TeamDashboardContextType {
  data: DashboardData | null;
  isLoading: boolean;
  error: string | null;
  selectedProject: Project | null;
  
  // Actions
  loadDashboardData: () => Promise<void>;
  setSelectedProject: (project: Project | null) => void;
  completeTask: (projectId: number, taskId: number) => void;
  addTeamMember: (member: TeamMember) => void;
  createTask: (projectId: number, task: Partial<Task>) => void;
  updateTaskStatus: (projectId: number, taskId: number, status: Task['status']) => void;
}

const TeamDashboardContext = createContext<TeamDashboardContextType | undefined>(undefined);

export function TeamDashboardProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const dashboardData = await teamDashboardService.getDashboardData();
      setData(dashboardData);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);


  const recalculateStats = useCallback((projects: Project[]): ProjectStats => {
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
  }, []);

  const updateWeeklyProgress = useCallback((projects: Project[]) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const allTasks = projects.flatMap(p => p.tasks);
    const completedCount = allTasks.filter(t => t.status === 'done').length;
    const totalCount = allTasks.length;
    
    return days.map((label, index) => ({
      label,
      completed: Math.floor((completedCount / 7) * (index + 1) * (0.8 + Math.random() * 0.4)),
      total: Math.floor((totalCount / 7) * (index + 1)),
    }));
  }, []);

  const completeTask = useCallback((projectId: number, taskId: number) => {
    setData(prev => {
      if (!prev) return prev;
      
      const updatedProjects = prev.projects.map(project => {
        if (project.id !== projectId) return project;
        
        const updatedTasks = project.tasks.map(task => {
          if (task.id !== taskId) return task;
          return { ...task, status: 'done' as const, updatedAt: new Date().toISOString() };
        });
        
        const completedCount = updatedTasks.filter(t => t.status === 'done').length;
        const progress = Math.round((completedCount / updatedTasks.length) * 100);
        
        return { ...project, tasks: updatedTasks, progress };
      });

      const completedTask = prev.projects
        .find(p => p.id === projectId)?.tasks
        .find(t => t.id === taskId);

      const user = completedTask?.assignee || prev.members[0];
      
      // Add activity for task completion
      const newActivity: Activity = {
        id: Date.now(),
        type: 'task_completed',
        user,
        description: `completed "${completedTask?.title}"`,
        projectName: prev.projects.find(p => p.id === projectId)?.name,
        taskName: completedTask?.title,
        timestamp: new Date().toISOString(),
      };

      return {
        ...prev,
        projects: updatedProjects,
        stats: recalculateStats(updatedProjects),
        weeklyProgress: updateWeeklyProgress(updatedProjects),
        activities: [newActivity, ...prev.activities],
      };
    });
  }, [recalculateStats, updateWeeklyProgress]);

  const addTeamMember = useCallback((member: TeamMember) => {
    setData(prev => {
      if (!prev) return prev;

      // Add activity for new member
      const newActivity: Activity = {
        id: Date.now(),
        type: 'member_joined',
        user: member,
        description: 'joined the team',
        timestamp: new Date().toISOString(),
      };

      return {
        ...prev,
        members: [...prev.members, member],
        activities: [newActivity, ...prev.activities],
      };
    });
  }, []);

  const createTask = useCallback((projectId: number, taskData: Partial<Task>) => {
    setData(prev => {
      if (!prev) return prev;

      const newTask: Task = {
        id: Date.now(),
        title: taskData.title || 'New Task',
        description: taskData.description || '',
        status: taskData.status || 'todo',
        priority: taskData.priority || 'medium',
        assignee: taskData.assignee,
        dueDate: taskData.dueDate,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: taskData.tags || [],
      };

      const updatedProjects = prev.projects.map(project => {
        if (project.id !== projectId) return project;
        const updatedTasks = [...project.tasks, newTask];
        const completedCount = updatedTasks.filter(t => t.status === 'done').length;
        const progress = Math.round((completedCount / updatedTasks.length) * 100);
        return { ...project, tasks: updatedTasks, progress };
      });

      const user = taskData.assignee || prev.members[0];
      
      // Add activity for task creation
      const newActivity: Activity = {
        id: Date.now() + 1,
        type: 'task_created',
        user,
        description: `created "${newTask.title}"`,
        projectName: prev.projects.find(p => p.id === projectId)?.name,
        taskName: newTask.title,
        timestamp: new Date().toISOString(),
      };

      return {
        ...prev,
        projects: updatedProjects,
        stats: recalculateStats(updatedProjects),
        activities: [newActivity, ...prev.activities],
      };
    });
  }, [recalculateStats]);

  const updateTaskStatus = useCallback((projectId: number, taskId: number, status: Task['status']) => {
    if (status === 'done') {
      completeTask(projectId, taskId);
      return;
    }

    setData(prev => {
      if (!prev) return prev;

      const updatedProjects = prev.projects.map(project => {
        if (project.id !== projectId) return project;
        
        const updatedTasks = project.tasks.map(task => {
          if (task.id !== taskId) return task;
          return { ...task, status, updatedAt: new Date().toISOString() };
        });
        
        const completedCount = updatedTasks.filter(t => t.status === 'done').length;
        const progress = Math.round((completedCount / updatedTasks.length) * 100);
        
        return { ...project, tasks: updatedTasks, progress };
      });

      const task = prev.projects
        .find(p => p.id === projectId)?.tasks
        .find(t => t.id === taskId);

      const user = task?.assignee || prev.members[0];

      // Add activity for status change
      const newActivity: Activity = {
        id: Date.now(),
        type: 'status_changed',
        user,
        description: `changed "${task?.title}" status to ${status.replace('_', ' ')}`,
        projectName: prev.projects.find(p => p.id === projectId)?.name,
        taskName: task?.title,
        timestamp: new Date().toISOString(),
      };

      return {
        ...prev,
        projects: updatedProjects,
        stats: recalculateStats(updatedProjects),
        activities: [newActivity, ...prev.activities],
      };
    });
  }, [completeTask, recalculateStats]);

  return (
    <TeamDashboardContext.Provider
      value={{
        data,
        isLoading,
        error,
        selectedProject,
        loadDashboardData,
        setSelectedProject,
        completeTask,
        addTeamMember,
        createTask,
        updateTaskStatus,
      }}
    >
      {children}
    </TeamDashboardContext.Provider>
  );
}

export function useTeamDashboard() {
  const context = useContext(TeamDashboardContext);
  if (context === undefined) {
    throw new Error('useTeamDashboard must be used within a TeamDashboardProvider');
  }
  return context;
}
