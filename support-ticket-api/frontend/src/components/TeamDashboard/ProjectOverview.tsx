import type { Project, ProjectStats } from '../types/project';
import { Card, CardHeader, CardBody } from '../shared/Card';
import ProjectCard from './ProjectCard';
import { FolderKanban, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface ProjectOverviewProps {
  projects: Project[];
  stats: ProjectStats;
  onProjectClick?: (project: Project) => void;
}

export default function ProjectOverview({ projects, stats, onProjectClick }: ProjectOverviewProps) {
  const statCards = [
    {
      label: 'Total Tasks',
      value: stats.totalTasks,
      icon: FolderKanban,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Completed',
      value: stats.completedTasks,
      icon: CheckCircle2,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
    },
    {
      label: 'In Progress',
      value: stats.inProgressTasks,
      icon: TrendingUp,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'Overdue',
      value: stats.overdueTasks,
      icon: AlertTriangle,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card key={stat.label} padding="md">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-5 h-5 text-${stat.color.replace('bg-', '')}`} style={{ color: stat.color.includes('blue') ? '#3b82f6' : stat.color.includes('green') ? '#22c55e' : stat.color.includes('purple') ? '#a855f7' : '#ef4444' }} />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card padding="none">
        <CardHeader className="px-5 pt-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Active Projects</h2>
            <p className="text-sm text-gray-500 mt-1">
              {projects.filter(p => p.status === 'in_progress').length} projects in progress
            </p>
          </div>
        </CardHeader>
        <CardBody className="px-5 pb-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.slice(0, 4).map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => onProjectClick?.(project)}
              />
            ))}
          </div>
          {projects.length > 4 && (
            <button className="mt-4 w-full py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              View all {projects.length} projects
            </button>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
