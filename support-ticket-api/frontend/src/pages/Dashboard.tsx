import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService, ticketService } from '../services/api';
import type { DashboardStats, Ticket } from '../types';
import { 
  Ticket as TicketIcon, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Users,
  ArrowRight
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTickets, setRecentTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsData, ticketsData] = await Promise.all([
        adminService.dashboard(),
        ticketService.list({ limit: '5' }),
      ]);
      setStats(statsData);
      setRecentTickets(ticketsData.tickets || []);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading dashboard">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 dark:border-blue-400 border-t-transparent rounded-full"></div>
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Tickets',
      value: stats?.total_tickets || 0,
      icon: TicketIcon,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-900/30',
      textColor: 'text-blue-500 dark:text-blue-400',
    },
    {
      label: 'Open Tickets',
      value: stats?.open_tickets || 0,
      icon: Clock,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/30',
      textColor: 'text-yellow-500 dark:text-yellow-400',
    },
    {
      label: 'Resolved',
      value: stats?.resolved_tickets || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
      bgColor: 'bg-green-50 dark:bg-green-900/30',
      textColor: 'text-green-500 dark:text-green-400',
    },
    {
      label: 'SLA Breached',
      value: stats?.sla_breached || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
      bgColor: 'bg-red-50 dark:bg-red-900/30',
      textColor: 'text-red-500 dark:text-red-400',
    },
  ];

  const statusColors: Record<string, string> = {
    open: 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300',
    assigned: 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-300',
    in_progress: 'bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300',
    resolved: 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300',
    closed: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Overview of your support system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" role="region" aria-label="Statistics overview">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`} aria-hidden="true">
                  <Icon className={`w-6 h-6 ${stat.textColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tickets by Status */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 transition-colors">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-gray-400 dark:text-gray-500" aria-hidden="true" />
            Tickets by Status
          </h2>
          <div className="space-y-3" role="list" aria-label="Tickets grouped by status">
            {stats?.tickets_by_status && Object.entries(stats.tickets_by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between" role="listitem">
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[status] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}>
                    {status.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden" role="progressbar" aria-valuenow={count} aria-valuemax={stats?.total_tickets || 1}>
                    <div 
                      className="h-full bg-blue-500 dark:bg-blue-400 rounded-full transition-all"
                      style={{ width: `${(count / (stats?.total_tickets || 1)) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100 w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tickets by Priority */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 transition-colors">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-400 dark:text-gray-500" aria-hidden="true" />
            Tickets by Priority
          </h2>
          <div className="space-y-3" role="list" aria-label="Tickets grouped by priority">
            {stats?.tickets_by_priority && Object.entries(stats.tickets_by_priority).map(([priority, count]) => {
              const colors: Record<string, string> = {
                low: 'bg-gray-500',
                medium: 'bg-blue-500',
                high: 'bg-orange-500',
                urgent: 'bg-red-500',
              };
              return (
                <div key={priority} className="flex items-center justify-between" role="listitem">
                  <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">{priority}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden" role="progressbar" aria-valuenow={count} aria-valuemax={stats?.total_tickets || 1}>
                      <div 
                        className={`h-full ${colors[priority]} rounded-full transition-all`}
                        style={{ width: `${(count / (stats?.total_tickets || 1)) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 w-8 text-right">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Tickets */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 transition-colors">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Recent Tickets</h2>
          <Link 
            to="/tickets" 
            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
          >
            View all
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full" role="table" aria-label="Recent tickets">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <th className="pb-3" scope="col">Ticket</th>
                <th className="pb-3" scope="col">Status</th>
                <th className="pb-3" scope="col">Priority</th>
                <th className="pb-3" scope="col">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {recentTickets.map((ticket) => (
                <tr key={ticket.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="py-3">
                    <Link to={`/tickets/${ticket.id}`} className="hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{ticket.subject}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{ticket.ticket_number}</p>
                    </Link>
                  </td>
                  <td className="py-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[ticket.status] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">{ticket.priority}</span>
                  </td>
                  <td className="py-3">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
