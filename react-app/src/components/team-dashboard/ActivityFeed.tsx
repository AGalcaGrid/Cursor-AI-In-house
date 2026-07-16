import { useState } from 'react';

interface Activity {
  id: string;
  type: 'task_created' | 'task_completed' | 'comment' | 'mention' | 'file_upload' | 'status_change' | 'member_joined';
  user: {
    name: string;
    avatar: string;
  };
  content: string;
  target?: string;
  timestamp: string;
  metadata?: {
    oldStatus?: string;
    newStatus?: string;
    fileName?: string;
    taskName?: string;
  };
}

interface ActivityFeedProps {
  activities: Activity[];
  onActivityClick?: (activityId: string) => void;
  maxDisplay?: number;
}

const activityIcons = {
  task_created: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  ),
  task_completed: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  comment: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  ),
  mention: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
    </svg>
  ),
  file_upload: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  ),
  status_change: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
    </svg>
  ),
  member_joined: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
    </svg>
  ),
};

const activityColors = {
  task_created: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  task_completed: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  comment: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  mention: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400',
  file_upload: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
  status_change: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  member_joined: 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400',
};

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString();
}

export function ActivityFeed({ activities, onActivityClick, maxDisplay = 10 }: ActivityFeedProps) {
  const [showAll, setShowAll] = useState(false);
  const [filter, setFilter] = useState<'all' | 'tasks' | 'comments' | 'files'>('all');

  const filteredActivities = activities.filter((activity) => {
    if (filter === 'all') return true;
    if (filter === 'tasks') return ['task_created', 'task_completed', 'status_change'].includes(activity.type);
    if (filter === 'comments') return ['comment', 'mention'].includes(activity.type);
    if (filter === 'files') return activity.type === 'file_upload';
    return true;
  });

  const displayedActivities = showAll ? filteredActivities : filteredActivities.slice(0, maxDisplay);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {activities.length} activities this week
            </p>
          </div>
          <div className="flex gap-1 overflow-x-auto">
            {(['all', 'tasks', 'comments', 'files'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 text-xs font-medium rounded-full whitespace-nowrap transition-colors
                  ${filter === f
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                  }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-100 dark:divide-gray-700 max-h-96 overflow-y-auto">
        {displayedActivities.map((activity) => (
          <div
            key={activity.id}
            onClick={() => onActivityClick?.(activity.id)}
            className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
          >
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="relative">
                  <img
                    src={activity.user.avatar}
                    alt={activity.user.name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                  <span
                    className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center
                      ${activityColors[activity.type]}`}
                  >
                    {activityIcons[activity.type]}
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-white">
                  <span className="font-medium">{activity.user.name}</span>{' '}
                  <span className="text-gray-600 dark:text-gray-400">{activity.content}</span>
                  {activity.target && (
                    <span className="font-medium text-blue-600 dark:text-blue-400">
                      {' '}{activity.target}
                    </span>
                  )}
                </p>
                {activity.metadata?.taskName && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 truncate">
                    Task: {activity.metadata.taskName}
                  </p>
                )}
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  {formatTimeAgo(activity.timestamp)}
                </p>
              </div>
            </div>
          </div>
        ))}

        {displayedActivities.length === 0 && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No activities found
          </div>
        )}
      </div>

      {filteredActivities.length > maxDisplay && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setShowAll(!showAll)}
            className="w-full py-2 text-sm font-medium text-blue-600 hover:text-blue-700 
              dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
          >
            {showAll ? 'Show Less' : `View All ${filteredActivities.length} Activities`}
          </button>
        </div>
      )}
    </div>
  );
}
