import { useState } from 'react';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  tasksAssigned: number;
  tasksCompleted: number;
  email: string;
}

interface TeamMembersProps {
  members: TeamMember[];
  onMemberClick?: (memberId: string) => void;
  maxDisplay?: number;
}

const statusColors = {
  online: 'bg-green-500',
  away: 'bg-yellow-500',
  busy: 'bg-red-500',
  offline: 'bg-gray-400',
};

const statusLabels = {
  online: 'Online',
  away: 'Away',
  busy: 'Busy',
  offline: 'Offline',
};

export function TeamMembers({ members, onMemberClick, maxDisplay = 8 }: TeamMembersProps) {
  const [showAll, setShowAll] = useState(false);
  const [hoveredMember, setHoveredMember] = useState<string | null>(null);

  const displayedMembers = showAll ? members : members.slice(0, maxDisplay);
  const remainingCount = members.length - maxDisplay;

  const onlineCount = members.filter((m) => m.status === 'online').length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Team Members</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {onlineCount} of {members.length} online
          </p>
        </div>
        <button
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          onClick={() => setShowAll(!showAll)}
        >
          {showAll ? 'Show Less' : 'View All'}
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        {displayedMembers.map((member) => (
          <div
            key={member.id}
            className="relative group"
            onMouseEnter={() => setHoveredMember(member.id)}
            onMouseLeave={() => setHoveredMember(null)}
          >
            <button
              onClick={() => onMemberClick?.(member.id)}
              className="relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full"
              aria-label={`${member.name} - ${statusLabels[member.status]}`}
            >
              <img
                src={member.avatar}
                alt={member.name}
                className="w-12 h-12 rounded-full object-cover ring-2 ring-white dark:ring-gray-800 
                  transition-transform group-hover:scale-110"
              />
              <span
                className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-white dark:border-gray-800
                  ${statusColors[member.status]}`}
                aria-hidden="true"
              />
            </button>

            {hoveredMember === member.id && (
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-10 
                bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg py-2 px-3 
                whitespace-nowrap shadow-lg animate-fade-in">
                <p className="font-medium">{member.name}</p>
                <p className="text-gray-300">{member.role}</p>
                <p className="text-gray-400 mt-1">
                  {member.tasksCompleted}/{member.tasksAssigned} tasks done
                </p>
                <div className="flex gap-2 mt-2 pt-2 border-t border-gray-700">
                  <button
                    onClick={(e) => { e.stopPropagation(); window.location.href = `mailto:${member.email}`; }}
                    className="flex items-center gap-1 px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white text-xs"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Email
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); alert(`Starting chat with ${member.name}`); }}
                    className="flex items-center gap-1 px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-white text-xs"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    Chat
                  </button>
                </div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
                  <div className="border-4 border-transparent border-t-gray-900 dark:border-t-gray-700" />
                </div>
              </div>
            )}
          </div>
        ))}

        {!showAll && remainingCount > 0 && (
          <button
            onClick={() => setShowAll(true)}
            className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-700 
              flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-300
              hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            +{remainingCount}
          </button>
        )}
      </div>

      {showAll && (
        <div className="mt-6 space-y-3">
          {members.map((member) => (
            <div
              key={member.id}
              onClick={() => onMemberClick?.(member.id)}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 
                cursor-pointer transition-colors"
            >
              <div className="relative">
                <img
                  src={member.avatar}
                  alt={member.name}
                  className="w-10 h-10 rounded-full object-cover"
                />
                <span
                  className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800
                    ${statusColors[member.status]}`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 dark:text-white truncate">{member.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{member.role}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {member.tasksCompleted}/{member.tasksAssigned}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">tasks</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
