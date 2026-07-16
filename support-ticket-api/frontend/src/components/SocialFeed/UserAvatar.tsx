import { CheckCircle } from 'lucide-react';
import type { FeedUser } from './types';

interface UserAvatarProps {
  user: FeedUser;
  size?: 'sm' | 'md' | 'lg';
  showName?: boolean;
  showUsername?: boolean;
  timestamp?: string;
}

const sizeClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
};

export default function UserAvatar({ 
  user, 
  size = 'md', 
  showName = false, 
  showUsername = false,
  timestamp 
}: UserAvatarProps) {
  const initials = user.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const formatTimestamp = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="flex items-center gap-3">
      <div className={`relative flex-shrink-0 ${sizeClasses[size]} rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium`}>
        {user.avatar ? (
          <img 
            src={user.avatar} 
            alt={user.name} 
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          initials
        )}
      </div>
      
      {(showName || showUsername) && (
        <div className="flex flex-col min-w-0">
          {showName && (
            <div className="flex items-center gap-1">
              <span className="font-semibold text-gray-900 truncate">{user.name}</span>
              {user.verified && (
                <CheckCircle className="w-4 h-4 text-blue-500 flex-shrink-0" />
              )}
            </div>
          )}
          <div className="flex items-center gap-1 text-sm text-gray-500">
            {showUsername && <span>@{user.username}</span>}
            {timestamp && (
              <>
                {showUsername && <span>·</span>}
                <span>{formatTimestamp(timestamp)}</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
