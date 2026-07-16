import type { Activity } from '../types/activity';
import { Card, CardHeader, CardBody } from '../shared/Card';
import Avatar from '../shared/Avatar';
import { 
  CheckCircle, 
  PlusCircle, 
  UserPlus, 
  MessageSquare, 
  FileUp, 
  RefreshCw,
  Calendar,
  FolderPlus,
  MoreHorizontal
} from 'lucide-react';

interface ActivityFeedProps {
  activities: Activity[];
  maxItems?: number;
  onViewAll?: () => void;
}

const activityIcons = {
  task_created: PlusCircle,
  task_completed: CheckCircle,
  task_assigned: UserPlus,
  comment_added: MessageSquare,
  project_created: FolderPlus,
  member_joined: UserPlus,
  file_uploaded: FileUp,
  status_changed: RefreshCw,
  deadline_updated: Calendar,
};

const activityColors = {
  task_created: 'text-blue-500 bg-blue-50',
  task_completed: 'text-green-500 bg-green-50',
  task_assigned: 'text-purple-500 bg-purple-50',
  comment_added: 'text-yellow-500 bg-yellow-50',
  project_created: 'text-indigo-500 bg-indigo-50',
  member_joined: 'text-pink-500 bg-pink-50',
  file_uploaded: 'text-cyan-500 bg-cyan-50',
  status_changed: 'text-orange-500 bg-orange-50',
  deadline_updated: 'text-red-500 bg-red-50',
};

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function ActivityFeed({ activities, maxItems = 10, onViewAll }: ActivityFeedProps) {
  const displayedActivities = activities.slice(0, maxItems);

  return (
    <Card padding="none">
      <CardHeader className="px-5 pt-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <p className="text-sm text-gray-500 mt-1">Latest updates from your team</p>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <MoreHorizontal className="w-5 h-5 text-gray-400" />
        </button>
      </CardHeader>
      <CardBody>
        <div className="divide-y divide-gray-100">
          {displayedActivities.map((activity) => {
            const Icon = activityIcons[activity.type];
            const colorClass = activityColors[activity.type];

            return (
              <div key={activity.id} className="flex gap-4 px-5 py-3 hover:bg-gray-50 transition-colors">
                <div className="flex-shrink-0">
                  <Avatar name={activity.user.name} size="sm" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2">
                    <div className={`p-1 rounded ${colorClass}`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">
                        <span className="font-medium">{activity.user.name}</span>
                        {' '}{activity.description}
                      </p>
                      {(activity.projectName || activity.taskName) && (
                        <p className="text-xs text-gray-500 mt-0.5">
                          {activity.projectName && <span>in {activity.projectName}</span>}
                          {activity.projectName && activity.taskName && ' • '}
                          {activity.taskName && <span>{activity.taskName}</span>}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <span className="text-xs text-gray-400">{formatTimeAgo(activity.timestamp)}</span>
                </div>
              </div>
            );
          })}
        </div>
        
        {activities.length > maxItems && onViewAll && (
          <div className="px-5 pb-4">
            <button
              onClick={onViewAll}
              className="w-full py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              View all activity
            </button>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
