import type { Project } from '../types/project';
import Avatar from '../shared/Avatar';
import Badge from '../shared/Badge';
import { Calendar, CheckCircle, Clock, Users } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
  onClick?: () => void;
}

const statusConfig = {
  planning: { label: 'Planning', variant: 'info' as const },
  in_progress: { label: 'In Progress', variant: 'primary' as const },
  review: { label: 'Review', variant: 'warning' as const },
  completed: { label: 'Completed', variant: 'success' as const },
  on_hold: { label: 'On Hold', variant: 'default' as const },
};

export default function ProjectCard({ project, onClick }: ProjectCardProps) {
  const completedTasks = project.tasks.filter(t => t.status === 'done').length;
  const totalTasks = project.tasks.length;
  const status = statusConfig[project.status];

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-all cursor-pointer border-l-4"
      style={{ borderLeftColor: project.color }}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg">{project.name}</h3>
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">{project.description}</p>
        </div>
        <Badge variant={status.variant} size="sm">
          {status.label}
        </Badge>
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span className="font-medium">{project.progress}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{ width: `${project.progress}%`, backgroundColor: project.color }}
          />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <CheckCircle className="w-4 h-4" />
            <span>{completedTasks}/{totalTasks}</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{project.members.length}</span>
          </div>
        </div>

        {project.endDate && (
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>{new Date(project.endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex -space-x-2">
          {project.members.slice(0, 4).map((member) => (
            <Avatar
              key={member.id}
              name={member.name}
              size="sm"
              status={member.status}
            />
          ))}
          {project.members.length > 4 && (
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600 ring-2 ring-white">
              +{project.members.length - 4}
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 text-xs text-gray-400">
          <Clock className="w-3 h-3" />
          <span>Updated {new Date(project.tasks[0]?.updatedAt || project.startDate).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}
