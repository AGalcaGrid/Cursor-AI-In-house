import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from '@dnd-kit/core';
import { arrayMove, sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Search, Filter, Plus, X, RefreshCw, Ticket } from 'lucide-react';
import type { KanbanTask, KanbanColumn, TaskStatus, TaskPriority, TicketStatus } from './types';
import { COLUMN_CONFIG, PRIORITY_CONFIG, TICKET_TO_KANBAN_STATUS, KANBAN_TO_TICKET_STATUS } from './types';
import BoardColumn from './BoardColumn';
import TaskCard from './TaskCard';
import AddTaskModal from './AddTaskModal';
import EditTaskModal from './EditTaskModal';
import { ticketService, agentService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import type { Ticket as TicketType } from '../../types';

const STORAGE_KEY = 'kanban-board-state';

const MOCK_ASSIGNEES = [
  { id: 1, name: 'Sarah Johnson' },
  { id: 2, name: 'Michael Chen' },
  { id: 3, name: 'Emily Davis' },
  { id: 4, name: 'James Wilson' },
  { id: 5, name: 'Lisa Anderson' },
];

// Convert a ticket from API to KanbanTask
const ticketToKanbanTask = (ticket: TicketType): KanbanTask => ({
  id: `ticket-${ticket.id}`,
  ticketId: ticket.id,
  ticketNumber: ticket.ticket_number,
  title: ticket.subject,
  description: ticket.description,
  status: TICKET_TO_KANBAN_STATUS[ticket.status as TicketStatus] || 'todo',
  priority: ticket.priority as TaskPriority,
  assignee: ticket.assigned_agent ? {
    id: ticket.assigned_agent.id,
    name: ticket.assigned_agent.name,
  } : undefined,
  dueDate: ticket.sla_deadline,
  tags: [ticket.category],
  createdAt: ticket.created_at,
  updatedAt: ticket.updated_at,
  category: ticket.category,
  customerEmail: ticket.customer_email,
  isFromTicket: true,
});

export default function KanbanBoard() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<KanbanTask[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<TaskPriority | 'all'>('all');
  const [filterAssignee, setFilterAssignee] = useState<number | 'all'>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [activeTask, setActiveTask] = useState<KanbanTask | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addModalStatus, setAddModalStatus] = useState<TaskStatus>('todo');
  const [editingTask, setEditingTask] = useState<KanbanTask | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [assignees, setAssignees] = useState(MOCK_ASSIGNEES);

  // Fetch tickets and agents from API
  const fetchTickets = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch tickets and agents in parallel
      const [ticketResponse, agentsResponse] = await Promise.all([
        ticketService.list({ per_page: '100' }),
        agentService.list().catch(() => []) // Fallback to empty array if agents fetch fails
      ]);
      
      const ticketTasks = ticketResponse.tickets.map(ticketToKanbanTask);
      
      // Load any manual tasks from localStorage
      const saved = localStorage.getItem(STORAGE_KEY);
      let manualTasks: KanbanTask[] = [];
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          manualTasks = (parsed.tasks || []).filter((t: KanbanTask) => !t.isFromTicket);
        } catch {
          // Ignore parse errors
        }
      }
      
      // Combine ticket tasks with manual tasks
      setTasks([...ticketTasks, ...manualTasks]);
      
      // Build assignees list
      let allAssignees: { id: number; name: string }[] = [];
      
      // Add agents from API (if admin)
      if (agentsResponse.length > 0) {
        allAssignees = agentsResponse.map(agent => ({
          id: agent.id,
          name: agent.name
        }));
      }
      
      // Add assignees from tickets (for non-admins)
      ticketResponse.tickets.forEach(ticket => {
        if (ticket.assigned_agent && !allAssignees.find(a => a.id === ticket.assigned_agent!.id)) {
          allAssignees.push({
            id: ticket.assigned_agent.id,
            name: ticket.assigned_agent.name
          });
        }
      });
      
      // Add current user if they're an agent/admin and not already in list
      if (user && (user.role === 'agent' || user.role === 'admin')) {
        if (!allAssignees.find(a => a.id === user.id)) {
          allAssignees.unshift({ id: user.id, name: user.name });
        }
      }
      
      setAssignees(allAssignees.length > 0 ? allAssignees : MOCK_ASSIGNEES);
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
      // Fall back to localStorage only
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setTasks(parsed.tasks || []);
        } catch {
          setTasks([]);
        }
      }
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  // Load tickets on mount
  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  // Save manual tasks to localStorage (not ticket-based tasks)
  useEffect(() => {
    const manualTasks = tasks.filter(t => !t.isFromTicket);
    if (manualTasks.length > 0 || tasks.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        tasks: manualTasks,
        searchQuery,
        filterPriority,
        filterAssignee,
      }));
    }
  }, [tasks, searchQuery, filterPriority, filterAssignee]);

  // Sync ticket status change to backend
  const syncTicketStatus = useCallback(async (task: KanbanTask, newStatus: TaskStatus) => {
    if (!task.isFromTicket || !task.ticketId) return;
    
    const newTicketStatus = KANBAN_TO_TICKET_STATUS[newStatus];
    try {
      setIsSyncing(true);
      await ticketService.updateStatus(task.ticketId, newTicketStatus);
    } catch (error: unknown) {
      console.error('Failed to sync ticket status:', error);
      
      // Show user-friendly error message
      const err = error as { response?: { data?: { message?: string } } };
      const message = err.response?.data?.message || 'Failed to update ticket status';
      alert(message);
      
      // Revert the change on error
      fetchTickets();
    } finally {
      setIsSyncing(false);
    }
  }, [fetchTickets]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const matchesSearch = searchQuery === '' ||
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
      const matchesAssignee = filterAssignee === 'all' || task.assignee?.id === filterAssignee;

      return matchesSearch && matchesPriority && matchesAssignee;
    });
  }, [tasks, searchQuery, filterPriority, filterAssignee]);

  // Build columns from filtered tasks
  const columns: KanbanColumn[] = useMemo(() => {
    return (Object.keys(COLUMN_CONFIG) as TaskStatus[]).map((status) => ({
      id: status,
      title: COLUMN_CONFIG[status].title,
      color: COLUMN_CONFIG[status].color,
      tasks: filteredTasks.filter((task) => task.status === status),
    }));
  }, [filteredTasks]);

  const findTask = useCallback((id: string) => {
    return tasks.find((task) => task.id === id);
  }, [tasks]);

  const handleDragStart = (event: DragStartEvent) => {
    const task = findTask(event.active.id as string);
    setActiveTask(task || null);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeTaskItem = findTask(activeId);
    if (!activeTaskItem) return;

    // Check if dropping over a column
    const overColumn = columns.find((col) => col.id === overId);
    if (overColumn && activeTaskItem.status !== overColumn.id) {
      setTasks((prev) =>
        prev.map((task) =>
          task.id === activeId ? { ...task, status: overColumn.id, updatedAt: new Date().toISOString() } : task
        )
      );
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    const draggedTask = activeTask;
    setActiveTask(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    if (activeId === overId) return;

    const activeTaskItem = findTask(activeId);
    const overTask = findTask(overId);

    if (!activeTaskItem) return;

    // If dropping over another task in the same column, reorder
    if (overTask && activeTaskItem.status === overTask.status) {
      setTasks((prev) => {
        const columnTasks = prev.filter((t) => t.status === activeTaskItem.status);
        const otherTasks = prev.filter((t) => t.status !== activeTaskItem.status);

        const oldIndex = columnTasks.findIndex((t) => t.id === activeId);
        const newIndex = columnTasks.findIndex((t) => t.id === overId);

        const reordered = arrayMove(columnTasks, oldIndex, newIndex);
        return [...otherTasks, ...reordered];
      });
    }

    // If dropping over a column, move to that column and sync
    const overColumn = columns.find((col) => col.id === overId);
    if (overColumn && activeTaskItem.status !== overColumn.id) {
      const newStatus = overColumn.id;
      setTasks((prev) =>
        prev.map((task) =>
          task.id === activeId ? { ...task, status: newStatus, updatedAt: new Date().toISOString() } : task
        )
      );
      // Sync ticket status to backend
      if (draggedTask?.isFromTicket) {
        syncTicketStatus(draggedTask, newStatus);
      }
    }
  };

  const handleAddTask = (status: TaskStatus) => {
    setAddModalStatus(status);
    setShowAddModal(true);
  };

  const handleSubmitNewTask = (taskData: Omit<KanbanTask, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTask: KanbanTask = {
      ...taskData,
      id: `task-${Date.now()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setTasks((prev) => [...prev, newTask]);
  };

  const handleEditTask = (task: KanbanTask) => {
    setEditingTask(task);
  };

  const handleUpdateTask = (updatedTask: KanbanTask) => {
    setTasks((prev) =>
      prev.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleDeleteTask = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilterPriority('all');
    setFilterAssignee('all');
  };

  const hasActiveFilters = searchQuery !== '' || filterPriority !== 'all' || filterAssignee !== 'all';

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          <p className="text-gray-500">Loading tickets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            Kanban Board
            {isSyncing && <RefreshCw className="w-4 h-4 text-blue-600 animate-spin" />}
          </h1>
          <p className="text-gray-500 mt-1 flex items-center gap-2">
            <Ticket className="w-4 h-4" />
            Tickets sync automatically with the backend
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchTickets()}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            title="Refresh tickets"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => handleAddTask('todo')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Task
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
            hasActiveFilters ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-300 hover:bg-gray-50'
          }`}
        >
          <Filter className="w-4 h-4" />
          Filters
          {hasActiveFilters && (
            <span className="px-1.5 py-0.5 text-xs bg-blue-600 text-white rounded-full">
              {[searchQuery !== '', filterPriority !== 'all', filterAssignee !== 'all'].filter(Boolean).length}
            </span>
          )}
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6 flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value as TaskPriority | 'all')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              <option value="all">All Priorities</option>
              {Object.entries(PRIORITY_CONFIG).map(([key, config]) => (
                <option key={key} value={key}>{config.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
            <select
              value={filterAssignee}
              onChange={(e) => setFilterAssignee(e.target.value === 'all' ? 'all' : Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              <option value="all">All Assignees</option>
              {assignees.map((assignee) => (
                <option key={assignee.id} value={assignee.id}>{assignee.name}</option>
              ))}
            </select>
          </div>
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              <X className="w-4 h-4" />
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex-1 overflow-x-auto pb-4">
          <div className="flex gap-4 h-full min-h-[500px]">
            {columns.map((column) => (
              <BoardColumn
                key={column.id}
                column={column}
                onAddTask={handleAddTask}
                onEditTask={handleEditTask}
                onDeleteTask={handleDeleteTask}
              />
            ))}
          </div>
        </div>

        <DragOverlay>
          {activeTask && (
            <div className="rotate-3 opacity-90">
              <TaskCard
                task={activeTask}
                onEdit={() => {}}
                onDelete={() => {}}
                isDragging
              />
            </div>
          )}
        </DragOverlay>
      </DndContext>

      {/* Modals */}
      <AddTaskModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleSubmitNewTask}
        initialStatus={addModalStatus}
        assignees={assignees}
      />

      <EditTaskModal
        isOpen={!!editingTask}
        task={editingTask}
        onClose={() => setEditingTask(null)}
        onSubmit={handleUpdateTask}
        onDelete={handleDeleteTask}
        assignees={assignees}
      />
    </div>
  );
}
