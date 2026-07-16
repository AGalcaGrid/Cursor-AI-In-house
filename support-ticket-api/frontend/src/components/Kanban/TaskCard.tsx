import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Calendar, GripVertical, MoreHorizontal, Ticket } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { KanbanTask } from './types';
import { PRIORITY_CONFIG } from './types';
import Avatar from '../shared/Avatar';

interface TaskCardProps {
  task: KanbanTask;
  onEdit: (task: KanbanTask) => void;
  onDelete: (taskId: string) => void;
  isDragging?: boolean;
}

export default function TaskCard({ task, onEdit, onDelete, isDragging }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const priorityConfig = PRIORITY_CONFIG[task.priority];
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && task.status !== 'done';

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-3 cursor-pointer hover:shadow-md transition-shadow ${
        isDragging ? 'opacity-50 shadow-lg' : ''
      }`}
    >
      <div className="flex items-start gap-2">
        <button
          {...attributes}
          {...listeners}
          className="mt-1 p-1 text-gray-400 hover:text-gray-600 cursor-grab active:cursor-grabbing"
          aria-label="Drag to reorder"
        >
          <GripVertical className="w-4 h-4" />
        </button>

        <div className="flex-1 min-w-0">
          {/* Ticket badge */}
          {task.isFromTicket && task.ticketNumber && (
            <Link
              to={`/tickets/${task.ticketId}`}
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mb-1"
              onClick={(e) => e.stopPropagation()}
            >
              <Ticket className="w-3 h-3" />
              {task.ticketNumber}
            </Link>
          )}

          <div className="flex items-start justify-between gap-2">
            <h4
              className="font-medium text-gray-900 text-sm line-clamp-2 cursor-pointer hover:text-blue-600"
              onClick={() => !task.isFromTicket && onEdit(task)}
            >
              {task.isFromTicket && task.ticketId ? (
                <Link to={`/tickets/${task.ticketId}`} className="hover:underline">
                  {task.title}
                </Link>
              ) : (
                <span onClick={() => onEdit(task)}>{task.title}</span>
              )}
            </h4>
            <div className="relative group">
              <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                <MoreHorizontal className="w-4 h-4" />
              </button>
              <div className="absolute right-0 top-6 bg-white rounded-lg shadow-lg border border-gray-200 py-1 hidden group-hover:block z-10 min-w-[100px]">
                {task.isFromTicket && task.ticketId ? (
                  <Link
                    to={`/tickets/${task.ticketId}`}
                    className="block w-full px-3 py-1.5 text-left text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Ticket
                  </Link>
                ) : (
                  <>
                    <button
                      onClick={() => onEdit(task)}
                      className="w-full px-3 py-1.5 text-left text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(task.id)}
                      className="w-full px-3 py-1.5 text-left text-sm text-red-600 hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {task.description && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</p>
          )}

          {task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                >
                  {tag}
                </span>
              ))}
              {task.tags.length > 3 && (
                <span className="px-1.5 py-0.5 text-xs text-gray-400">
                  +{task.tags.length - 3}
                </span>
              )}
            </div>
          )}

          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 text-xs rounded ${priorityConfig.bgColor} ${priorityConfig.color}`}>
                {priorityConfig.label}
              </span>
              {task.dueDate && (
                <span className={`flex items-center gap-1 text-xs ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
                  <Calendar className="w-3 h-3" />
                  {formatDate(task.dueDate)}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              {task.assignee && (
                <Avatar name={task.assignee.name} size="xs" />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
