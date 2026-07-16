import { useState } from 'react';

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


function TrendIndicator({ change, isPositive }: { change: number; isPositive: boolean }) {
  if (change === 0) return null;
  
  return (
    <span className={`flex items-center text-xs font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
      {isPositive ? (
        <svg className="w-3 h-3 mr-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-3 h-3 mr-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      )}
      {Math.abs(change)}%
    </span>
  );
}

interface ProjectOverviewProps {
  projects: Project[];
  onProjectSelect?: (projectId: string) => void;
  selectedProjectId?: string;
}

const statusColors = {
  'on-track': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  'at-risk': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  'delayed': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  'completed': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
};

const priorityColors = {
  low: 'border-l-gray-400',
  medium: 'border-l-blue-500',
  high: 'border-l-orange-500',
  critical: 'border-l-red-500',
};

export function ProjectOverview({ projects, onProjectSelect, selectedProjectId }: ProjectOverviewProps) {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const filteredProjects = projects.filter((project) => {
    if (filter === 'all') return true;
    if (filter === 'active') return project.status !== 'completed';
    if (filter === 'completed') return project.status === 'completed';
    return true;
  });

  const stats = {
    total: projects.length,
    completed: projects.filter((p) => p.status === 'completed').length,
    inProgress: projects.filter((p) => p.status !== 'completed').length,
    atRisk: projects.filter((p) => p.status === 'at-risk' || p.status === 'delayed').length,
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Project Overview</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Track progress across all team projects
            </p>
          </div>
          <div className="flex gap-2">
            {(['all', 'active', 'completed'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors
                  ${filter === f
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              <TrendIndicator change={8} isPositive={true} />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Projects</p>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.completed}</p>
              <TrendIndicator change={12} isPositive={true} />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.inProgress}</p>
              <TrendIndicator change={5} isPositive={true} />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.atRisk}</p>
              <TrendIndicator change={3} isPositive={false} />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">At Risk</p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
        {filteredProjects.map((project) => (
          <div
            key={project.id}
            onClick={() => onProjectSelect?.(project.id)}
            className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors
              border-l-4 ${priorityColors[project.priority]}
              ${selectedProjectId === project.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-gray-900 dark:text-white truncate">
                    {project.name}
                  </h3>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColors[project.status]}`}>
                    {project.status.replace('-', ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                  {project.description}
                </p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                  <span>{project.tasksCompleted}/{project.totalTasks} tasks</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                  {project.progress}%
                </span>
                <div className="w-24 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500
                      ${project.progress >= 100 ? 'bg-green-500' : 
                        project.progress >= 70 ? 'bg-blue-500' : 
                        project.progress >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.min(project.progress, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
        {filteredProjects.length === 0 && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No projects found
          </div>
        )}
      </div>
    </div>
  );
}
