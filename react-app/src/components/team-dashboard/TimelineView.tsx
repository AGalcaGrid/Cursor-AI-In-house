import { useState } from 'react';

interface Milestone {
  id: string;
  title: string;
  date: string;
  status: 'completed' | 'in-progress' | 'upcoming';
  description?: string;
  assignee?: {
    name: string;
    avatar: string;
  };
}

interface TimelineViewProps {
  milestones: Milestone[];
  onMilestoneClick?: (milestoneId: string) => void;
}

const statusColors = {
  completed: 'bg-green-500',
  'in-progress': 'bg-blue-500',
  upcoming: 'bg-gray-400',
};

const statusBgColors = {
  completed: 'bg-green-100 dark:bg-green-900/30',
  'in-progress': 'bg-blue-100 dark:bg-blue-900/30',
  upcoming: 'bg-gray-100 dark:bg-gray-700/50',
};

const statusTextColors = {
  completed: 'text-green-700 dark:text-green-400',
  'in-progress': 'text-blue-700 dark:text-blue-400',
  upcoming: 'text-gray-600 dark:text-gray-400',
};

export function TimelineView({ milestones, onMilestoneClick }: TimelineViewProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const sortedMilestones = [...milestones].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  const completedCount = milestones.filter((m) => m.status === 'completed').length;
  const progressPercentage = milestones.length > 0 
    ? Math.round((completedCount / milestones.length) * 100) 
    : 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Project Timeline</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {completedCount} of {milestones.length} milestones completed
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {progressPercentage}%
          </span>
        </div>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

        <div className="space-y-4">
          {sortedMilestones.map((milestone, index) => (
            <div
              key={milestone.id}
              className="relative pl-10 cursor-pointer"
              onClick={() => {
                setExpandedId(expandedId === milestone.id ? null : milestone.id);
                onMilestoneClick?.(milestone.id);
              }}
            >
              {/* Timeline dot */}
              <div
                className={`absolute left-2.5 w-3 h-3 rounded-full ${statusColors[milestone.status]} 
                  ring-4 ring-white dark:ring-gray-800 transition-transform
                  ${expandedId === milestone.id ? 'scale-125' : ''}`}
              />

              {/* Milestone card */}
              <div
                className={`p-4 rounded-lg ${statusBgColors[milestone.status]} 
                  hover:shadow-md transition-all duration-200
                  ${expandedId === milestone.id ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className={`font-medium ${statusTextColors[milestone.status]}`}>
                        {milestone.title}
                      </h3>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded-full capitalize
                          ${statusBgColors[milestone.status]} ${statusTextColors[milestone.status]}`}
                      >
                        {milestone.status.replace('-', ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(milestone.date).toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </p>
                  </div>

                  {milestone.assignee && (
                    <img
                      src={milestone.assignee.avatar}
                      alt={milestone.assignee.name}
                      className="w-8 h-8 rounded-full object-cover ring-2 ring-white dark:ring-gray-800"
                      title={milestone.assignee.name}
                    />
                  )}
                </div>

                {/* Expanded content */}
                {expandedId === milestone.id && milestone.description && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {milestone.description}
                    </p>
                    {milestone.assignee && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                        Assigned to: {milestone.assignee.name}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Connector line to next milestone */}
              {index < sortedMilestones.length - 1 && (
                <div className="absolute left-3.5 top-full h-4 w-0.5 bg-gray-200 dark:bg-gray-700" />
              )}
            </div>
          ))}
        </div>
      </div>

      {milestones.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No milestones defined yet
        </div>
      )}
    </div>
  );
}
