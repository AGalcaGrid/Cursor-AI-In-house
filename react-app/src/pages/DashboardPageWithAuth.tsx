import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { taskApi } from '../services/taskApi';
import type { Task as ApiTask } from '../services/taskApi';
import { Dashboard } from '../components/dashboard';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import type { Task, StatisticItem, DashboardUser } from '../types/dashboard';

export function DashboardPageWithAuth() {
  const { user, accessToken, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statistics, setStatistics] = useState<StatisticItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [error, setError] = useState('');

  const convertApiTaskToDashboardTask = (apiTask: ApiTask): Task => {
    return {
      id: apiTask.id.toString(),
      title: apiTask.title,
      description: apiTask.description || '',
      priority: apiTask.priority,
      status: apiTask.status === 'pending' ? 'todo' : apiTask.status === 'in_progress' ? 'in_progress' : 'completed',
      dueDate: apiTask.due_date || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      tags: [],
    };
  };

  const loadTasks = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError('');

    try {
      const apiTasks = await taskApi.getTasks(accessToken);
      const dashboardTasks = apiTasks.map(convertApiTaskToDashboardTask);
      setTasks(dashboardTasks);

      const totalTasks = apiTasks.length;
      const completedTasks = apiTasks.filter(t => t.status === 'completed').length;
      const inProgressTasks = apiTasks.filter(t => t.status === 'in_progress').length;
      const pendingTasks = apiTasks.filter(t => t.status === 'pending').length;
      const overdueTasks = apiTasks.filter(t => {
        if (!t.due_date) return false;
        return new Date(t.due_date) < new Date() && t.status !== 'completed';
      }).length;

      // Calculate meaningful percentages
      const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
      const progressRate = totalTasks > 0 ? Math.round((inProgressTasks / totalTasks) * 100) : 0;
      const overdueRate = totalTasks > 0 ? Math.round((overdueTasks / totalTasks) * 100) : 0;

      setStatistics([
        { id: '1', label: 'Total Tasks', value: totalTasks, change: pendingTasks, changeType: 'increase', icon: 'tasks' },
        { id: '2', label: 'Completed', value: completedTasks, change: completionRate, changeType: 'increase', icon: 'completed' },
        { id: '3', label: 'In Progress', value: inProgressTasks, change: progressRate, changeType: 'increase', icon: 'pending' },
        { id: '4', label: 'Overdue', value: overdueTasks, change: overdueRate, changeType: overdueTasks > 0 ? 'increase' : 'decrease', icon: 'overdue' },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
      console.error('Failed to load tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && accessToken) {
      loadTasks();
    }
  }, [isAuthenticated, accessToken]);

  useEffect(() => {
    console.log('🔐 Auth state changed:', { isAuthenticated, user: user?.username });
  }, [isAuthenticated, user]);

  const handleTaskStatusChange = async (taskId: string, status: Task['status']) => {
    if (!accessToken) return;

    const apiStatus = status === 'todo' ? 'pending' : status === 'in_progress' ? 'in_progress' : 'completed';

    try {
      await taskApi.updateTask(accessToken, parseInt(taskId), { status: apiStatus });
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId ? { ...task, status } : task
        )
      );
      await loadTasks();
    } catch (err) {
      console.error('Failed to update task:', err);
      alert('Failed to update task status');
    }
  };

  const handleTaskEdit = (task: Task) => {
    alert(`Edit functionality coming soon for: ${task.title}`);
  };

  const handleTaskDelete = async (taskId: string) => {
    if (!accessToken) return;

    if (confirm('Are you sure you want to delete this task?')) {
      try {
        await taskApi.deleteTask(accessToken, parseInt(taskId));
        setTasks((prev) => prev.filter((task) => task.id !== taskId));
        await loadTasks();
      } catch (err) {
        console.error('Failed to delete task:', err);
        alert('Failed to delete task');
      }
    }
  };

  const handleLogout = () => {
    console.log('📤 Dashboard logout button clicked');
    logout();
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
        {showRegister ? (
          <RegisterForm
            onSuccess={() => {
              setShowRegister(false);
            }}
            onSwitchToLogin={() => setShowRegister(false)}
          />
        ) : (
          <LoginForm
            onSuccess={() => {}}
            onSwitchToRegister={() => setShowRegister(true)}
          />
        )}
      </div>
    );
  }

  const dashboardUser: DashboardUser = {
    name: user?.username || 'User',
    email: user?.email || '',
    avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.username || 'User')}&background=random`,
    role: 'User',
  };

  if (isLoading && tasks.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading tasks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
          <div className="text-red-600 dark:text-red-400 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Connection Error</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
            Make sure the Task Management API is running on http://localhost:5003
          </p>
          <button
            onClick={loadTasks}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <Dashboard
      user={dashboardUser}
      tasks={tasks}
      statistics={statistics}
      onTaskStatusChange={handleTaskStatusChange}
      onTaskEdit={handleTaskEdit}
      onTaskDelete={handleTaskDelete}
      onLogout={handleLogout}
    />
  );
}
