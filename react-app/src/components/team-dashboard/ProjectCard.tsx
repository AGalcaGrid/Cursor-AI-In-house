import { Badge } from '../shared';
import type { Project } from '../types';

interface ProjectCardProps {
  project: Project;
  onClick?: () => void;
  isSelected?: boolean;
}

const statusVariants: Record<Project['status'], 'success' | 'warning' | 'error' | 'info'> = {
  'on-track': 'success',
  'at-risk': 'warning',
  'delayed': 'error',
  'completed': 'info',
};

const priorityColors = {
  low: 'border-l-gray-400',
  medium: 'border-l-blue-500',
  high: 'border-l-orange-500',
  critical: 'border-l-red-500',
};

export function ProjectCard({ project, onClick, isSelected }: ProjectCardProps) {
  return (
    <div
      onClick={onClick}
      className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors
        border-l-4 ${priorityColors[project.priority]}
        ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900 dark:text-white truncate">
              {project.name}
            </h3>
            <Badge variant={statusVariants[project.status]} size="sm">
              {project.status.replace('-', ' ')}
            </Badge>
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
  );
}
