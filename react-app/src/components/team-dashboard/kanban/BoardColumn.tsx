import { TaskCard } from './TaskCard';
import type { KanbanTask } from './TaskCard';

export interface KanbanColumn {
  id: 'todo' | 'in-progress' | 'done';
  title: string;
  color: string;
}

interface BoardColumnProps {
  column: KanbanColumn;
  tasks: KanbanTask[];
  isDropTarget: boolean;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
  onTaskDragStart: (taskId: string) => void;
  onTaskDragEnd: () => void;
  onTaskClick: (taskId: string) => void;
  onAddTask: () => void;
}

export function BoardColumn({
  column,
  tasks,
  isDropTarget,
  onDragOver,
  onDragLeave,
  onDrop,
  onTaskDragStart,
  onTaskDragEnd,
  onTaskClick,
  onAddTask,
}: BoardColumnProps) {
  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={`bg-gray-100 dark:bg-gray-800 rounded-xl p-4 min-h-[400px] transition-all
        ${isDropTarget ? 'ring-2 ring-blue-500 ring-opacity-50 bg-blue-50 dark:bg-blue-900/20' : ''}`}
    >
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${column.color}`} />
          <h3 className="font-semibold text-gray-900 dark:text-white">{column.title}</h3>
          <span className="px-2 py-0.5 text-xs font-medium bg-gray-200 dark:bg-gray-700 
            text-gray-600 dark:text-gray-300 rounded-full">
            {tasks.length}
          </span>
        </div>
        <button
          onClick={onAddTask}
          className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label={`Add task to ${column.title}`}
        >
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Tasks */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onDragStart={() => onTaskDragStart(task.id)}
            onDragEnd={onTaskDragEnd}
            onClick={() => onTaskClick(task.id)}
          />
        ))}

        {/* Drop Placeholder */}
        {isDropTarget && (
          <div className="border-2 border-dashed border-blue-400 dark:border-blue-500 
            rounded-lg p-4 text-center text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20">
            Drop task here
          </div>
        )}

        {/* Empty State */}
        {tasks.length === 0 && !isDropTarget && (
          <div className="text-center py-8 text-gray-400 dark:text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-sm">No tasks</p>
          </div>
        )}
      </div>
    </div>
  );
}
