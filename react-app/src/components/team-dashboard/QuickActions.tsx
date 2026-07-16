interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  color: string;
  description?: string;
}

interface QuickActionsProps {
  onAction: (actionId: string) => void;
}

const defaultActions: QuickAction[] = [
  {
    id: 'new-task',
    label: 'New Task',
    description: 'Create a new task',
    color: 'bg-blue-500 hover:bg-blue-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
    ),
  },
  {
    id: 'new-project',
    label: 'New Project',
    description: 'Start a new project',
    color: 'bg-purple-500 hover:bg-purple-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
      </svg>
    ),
  },
  {
    id: 'invite-member',
    label: 'Invite Member',
    description: 'Add team member',
    color: 'bg-green-500 hover:bg-green-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
  },
  {
    id: 'schedule-meeting',
    label: 'Schedule Meeting',
    description: 'Set up a team meeting',
    color: 'bg-orange-500 hover:bg-orange-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    id: 'upload-file',
    label: 'Upload File',
    description: 'Share a document',
    color: 'bg-indigo-500 hover:bg-indigo-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    id: 'generate-report',
    label: 'Generate Report',
    description: 'Create progress report',
    color: 'bg-teal-500 hover:bg-teal-600',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
];

export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Common tasks at your fingertips
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {defaultActions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action.id)}
            className={`${action.color} text-white rounded-xl p-4 
              flex flex-col items-center gap-2 transition-all duration-200
              hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 
              focus:ring-offset-2 focus:ring-blue-500`}
            aria-label={action.description}
          >
            <span className="p-2 bg-white/20 rounded-lg">
              {action.icon}
            </span>
            <span className="text-sm font-medium text-center">{action.label}</span>
          </button>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Keyboard shortcuts available
          </span>
          <button
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 
              dark:hover:text-blue-300 font-medium"
          >
            View all
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <kbd className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded border 
            border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300">
            ⌘ + N
          </kbd>
          <span className="text-xs text-gray-500 dark:text-gray-400">New Task</span>
          <kbd className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded border 
            border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 ml-2">
            ⌘ + P
          </kbd>
          <span className="text-xs text-gray-500 dark:text-gray-400">New Project</span>
        </div>
      </div>
    </div>
  );
}
