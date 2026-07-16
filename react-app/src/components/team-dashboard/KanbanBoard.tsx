import { useState } from 'react';
import { AddTaskModal } from './kanban';
import type { KanbanTask } from './kanban';

interface KanbanColumn {
  id: 'todo' | 'in-progress' | 'done';
  title: string;
  color: string;
}

const priorityConfig = {
  low: { label: 'Low', color: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300' },
  medium: { label: 'Medium', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  high: { label: 'High', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' },
  critical: { label: 'Critical', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
};

interface KanbanBoardProps {
  tasks?: KanbanTask[];
  onTaskMove?: (taskId: string, newStatus: KanbanTask['status']) => void;
  onTaskClick?: (taskId: string) => void;
  onAddTask?: (task: Omit<KanbanTask, 'id'>) => void;
}

const columns: KanbanColumn[] = [
  { id: 'todo', title: 'To Do', color: 'bg-gray-500' },
  { id: 'in-progress', title: 'In Progress', color: 'bg-blue-500' },
  { id: 'done', title: 'Done', color: 'bg-green-500' },
];

const sampleTasks: KanbanTask[] = [
  {
    id: '1',
    title: 'Design new landing page',
    description: 'Create wireframes and mockups for the new marketing landing page',
    status: 'todo',
    priority: 'high',
    dueDate: '2026-03-05',
    assignee: { id: '3', name: 'Jordan Kim', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face' },
    tags: ['design', 'marketing'],
  },
  {
    id: '2',
    title: 'Implement user authentication',
    description: 'Set up OAuth2 with Google and GitHub providers',
    status: 'todo',
    priority: 'critical',
    dueDate: '2026-03-01',
    assignee: { id: '2', name: 'Alex Rivera', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face' },
    tags: ['backend', 'security'],
  },
  {
    id: '3',
    title: 'Write API documentation',
    description: 'Document all REST endpoints with examples',
    status: 'todo',
    priority: 'medium',
    dueDate: '2026-03-10',
    tags: ['documentation'],
  },
  {
    id: '4',
    title: 'Build dashboard components',
    description: 'Create reusable chart and stat components',
    status: 'in-progress',
    priority: 'high',
    dueDate: '2026-02-28',
    assignee: { id: '7', name: 'Jamie Wilson', avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face' },
    tags: ['frontend', 'components'],
  },
  {
    id: '5',
    title: 'Database optimization',
    description: 'Optimize slow queries and add indexes',
    status: 'in-progress',
    priority: 'medium',
    assignee: { id: '4', name: 'Taylor Morgan', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face' },
    tags: ['backend', 'performance'],
  },
  {
    id: '6',
    title: 'Set up CI/CD pipeline',
    description: 'Configure GitHub Actions for automated testing and deployment',
    status: 'done',
    priority: 'high',
    dueDate: '2026-02-20',
    assignee: { id: '6', name: 'Morgan Lee', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face' },
    tags: ['devops'],
  },
  {
    id: '7',
    title: 'User testing session',
    description: 'Conduct usability testing with 5 participants',
    status: 'done',
    priority: 'medium',
    assignee: { id: '1', name: 'Sarah Chen', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face' },
    tags: ['research', 'ux'],
  },
];

function TaskCard({
  task,
  onDragStart,
  onDragEnd,
  onClick,
}: {
  task: KanbanTask;
  onDragStart: () => void;
  onDragEnd: () => void;
  onClick: () => void;
}) {
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && task.status !== 'done';
  const daysUntilDue = task.dueDate
    ? Math.ceil((new Date(task.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 
        p-4 cursor-grab active:cursor-grabbing shadow-sm hover:shadow-md transition-all
        hover:border-blue-300 dark:hover:border-blue-600"
    >
      {/* Priority & Tags */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${priorityConfig[task.priority].color}`}>
          {priorityConfig[task.priority].label}
        </span>
        {task.tags?.slice(0, 2).map((tag) => (
          <span
            key={tag}
            className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Title */}
      <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
        {task.title}
      </h4>

      {/* Description */}
      {task.description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
          {task.description}
        </p>
      )}

      {/* Footer: Assignee & Due Date */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
        {/* Assignee */}
        {task.assignee ? (
          <div className="flex items-center gap-2">
            <img
              src={task.assignee.avatar}
              alt={task.assignee.name}
              className="w-6 h-6 rounded-full object-cover"
            />
            <span className="text-xs text-gray-600 dark:text-gray-400 truncate max-w-[80px]">
              {task.assignee.name.split(' ')[0]}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
              <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <span className="text-xs text-gray-400">Unassigned</span>
          </div>
        )}

        {/* Due Date */}
        {task.dueDate && (
          <div
            className={`flex items-center gap-1 text-xs ${
              isOverdue
                ? 'text-red-600 dark:text-red-400'
                : daysUntilDue !== null && daysUntilDue <= 3
                ? 'text-orange-600 dark:text-orange-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>
              {isOverdue
                ? 'Overdue'
                : daysUntilDue === 0
                ? 'Today'
                : daysUntilDue === 1
                ? 'Tomorrow'
                : new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export function KanbanBoard({ tasks = sampleTasks, onTaskMove, onTaskClick, onAddTask }: KanbanBoardProps) {
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);
  const [localTasks, setLocalTasks] = useState<KanbanTask[]>(tasks);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<KanbanTask['priority'] | 'all'>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalInitialStatus, setModalInitialStatus] = useState<KanbanTask['status']>('todo');

  const handleDragStart = (taskId: string) => {
    setDraggedTaskId(taskId);
  };

  const handleDragEnd = () => {
    setDraggedTaskId(null);
    setDragOverColumn(null);
  };

  const handleDragOver = (e: React.DragEvent, columnId: string) => {
    e.preventDefault();
    setDragOverColumn(columnId);
  };

  const handleDragLeave = () => {
    setDragOverColumn(null);
  };

  const handleDrop = (e: React.DragEvent, columnId: KanbanTask['status']) => {
    e.preventDefault();
    if (draggedTaskId) {
      setLocalTasks((prev) =>
        prev.map((task) =>
          task.id === draggedTaskId ? { ...task, status: columnId } : task
        )
      );
      onTaskMove?.(draggedTaskId, columnId);
    }
    setDraggedTaskId(null);
    setDragOverColumn(null);
  };

  const handleOpenModal = (status: KanbanTask['status']) => {
    setModalInitialStatus(status);
    setIsModalOpen(true);
  };

  const handleAddTask = (taskData: Omit<KanbanTask, 'id'>) => {
    const newTask: KanbanTask = {
      ...taskData,
      id: Date.now().toString(),
    };
    setLocalTasks((prev) => [...prev, newTask]);
    onAddTask?.(taskData);
  };

  const filteredTasks = localTasks.filter((task) => {
    const matchesSearch = searchQuery === '' || 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  const getTasksByStatus = (status: KanbanTask['status']) =>
    filteredTasks.filter((task) => task.status === status);

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Kanban Board</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {filteredTasks.length} of {localTasks.length} tasks
          </p>
        </div>
        <button
          onClick={() => handleOpenModal('todo')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium 
            rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Task
        </button>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        {/* Search */}
        <div className="relative flex-1">
          <svg 
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
              bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
              focus:ring-2 focus:ring-blue-500 focus:border-transparent
              placeholder-gray-400 dark:placeholder-gray-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Priority Filter */}
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as KanbanTask['priority'] | 'all')}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
            bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
            focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {columns.map((column) => {
          const columnTasks = getTasksByStatus(column.id);
          const isDropTarget = dragOverColumn === column.id && draggedTaskId;

          return (
            <div
              key={column.id}
              onDragOver={(e) => handleDragOver(e, column.id)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, column.id)}
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
                    {columnTasks.length}
                  </span>
                </div>
                <button
                  onClick={() => handleOpenModal(column.id)}
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
                {columnTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onDragStart={() => handleDragStart(task.id)}
                    onDragEnd={handleDragEnd}
                    onClick={() => onTaskClick?.(task.id)}
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
                {columnTasks.length === 0 && !isDropTarget && (
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
        })}
      </div>

      {/* Drag Indicator */}
      {draggedTaskId && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-gray-900 dark:bg-gray-700 
          text-white px-4 py-2 rounded-lg shadow-lg text-sm z-50">
          Drag to move task between columns
        </div>
      )}

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddTask}
        initialStatus={modalInitialStatus}
      />
    </div>
  );
}
