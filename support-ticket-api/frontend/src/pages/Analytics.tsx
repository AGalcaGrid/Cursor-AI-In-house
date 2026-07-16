import { useState, useEffect } from 'react';
import {
  Ticket,
  Clock,
  CheckCircle,
  AlertTriangle,
  Users,
  TrendingUp,
  Timer,
  Target,
  Download,
  RefreshCw
} from 'lucide-react';

import ChartPlaceholder from '../components/Analytics/ChartPlaceholder';
import KPICard from '../components/Analytics/KPICard';
import DateRangeSelector from '../components/Analytics/DateRangeSelector';
import FilterControls from '../components/Analytics/FilterControls';
import DataTable from '../components/Analytics/DataTable';

// Mock data types
interface TicketMetric {
  id: string;
  ticket_number: string;
  subject: string;
  status: string;
  priority: string;
  response_time: string;
  resolution_time: string;
  agent: string;
}

export default function Analytics() {
  const [isLoading, setIsLoading] = useState(true);
  const [_dateRange, setDateRange] = useState({ start: '', end: '', preset: '30d' as const });
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Mock KPI data
  const [kpiData] = useState({
    totalTickets: 1247,
    totalTicketsChange: 12.5,
    avgResponseTime: '2.4h',
    avgResponseTimeChange: -8.3,
    resolutionRate: 94.2,
    resolutionRateChange: 3.1,
    customerSatisfaction: 4.7,
    customerSatisfactionChange: 0.2,
    openTickets: 156,
    openTicketsChange: -5.2,
    slaCompliance: 97.8,
    slaComplianceChange: 1.4,
    avgResolutionTime: '18.5h',
    avgResolutionTimeChange: -12.1,
    activeAgents: 24,
    activeAgentsChange: 0,
  });

  // Mock table data
  const [tableData] = useState<TicketMetric[]>([
    { id: '1', ticket_number: 'TICK-20240115-0001', subject: 'Login issues', status: 'resolved', priority: 'high', response_time: '1.2h', resolution_time: '4.5h', agent: 'John Doe' },
    { id: '2', ticket_number: 'TICK-20240115-0002', subject: 'Payment failed', status: 'in_progress', priority: 'urgent', response_time: '0.5h', resolution_time: '-', agent: 'Jane Smith' },
    { id: '3', ticket_number: 'TICK-20240115-0003', subject: 'Feature request', status: 'open', priority: 'low', response_time: '3.1h', resolution_time: '-', agent: 'Unassigned' },
    { id: '4', ticket_number: 'TICK-20240115-0004', subject: 'Account locked', status: 'resolved', priority: 'high', response_time: '0.8h', resolution_time: '2.1h', agent: 'John Doe' },
    { id: '5', ticket_number: 'TICK-20240115-0005', subject: 'Billing question', status: 'closed', priority: 'medium', response_time: '2.0h', resolution_time: '6.3h', agent: 'Jane Smith' },
  ]);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleDateRangeChange = (start: string, end: string, preset: string) => {
    setDateRange({ start, end, preset: preset as any });
    // In real app, refetch data with new date range
  };

  const handleClearFilters = () => {
    setStatusFilter('');
    setPriorityFilter('');
    setCategoryFilter('');
  };

  const handleExport = () => {
    // In real app, trigger CSV/Excel export
    console.log('Exporting data...');
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };

  const tableColumns = [
    { key: 'ticket_number' as const, label: 'Ticket #', sortable: true },
    { key: 'subject' as const, label: 'Subject', sortable: true },
    { 
      key: 'status' as const, 
      label: 'Status', 
      sortable: true,
      render: (value: string) => {
        const colors: Record<string, string> = {
          open: 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300',
          in_progress: 'bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300',
          resolved: 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300',
          closed: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
        };
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${colors[value] || colors.open}`}>
            {value.replace('_', ' ')}
          </span>
        );
      }
    },
    { 
      key: 'priority' as const, 
      label: 'Priority', 
      sortable: true,
      render: (value: string) => {
        const colors: Record<string, string> = {
          low: 'text-gray-600 dark:text-gray-400',
          medium: 'text-blue-600 dark:text-blue-400',
          high: 'text-orange-600 dark:text-orange-400',
          urgent: 'text-red-600 dark:text-red-400',
        };
        return (
          <span className={`font-medium capitalize ${colors[value] || ''}`}>
            {value}
          </span>
        );
      }
    },
    { key: 'response_time' as const, label: 'Response Time', sortable: true },
    { key: 'resolution_time' as const, label: 'Resolution Time', sortable: true },
    { key: 'agent' as const, label: 'Agent', sortable: true },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading analytics">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 dark:border-blue-400 border-t-transparent rounded-full"></div>
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Analytics</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Track performance metrics and trends</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Refresh data"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Download className="w-4 h-4" />
            Export Report
          </button>
          <DateRangeSelector onRangeChange={handleDateRangeChange} />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Tickets"
          value={kpiData.totalTickets.toLocaleString()}
          change={kpiData.totalTicketsChange}
          icon={Ticket}
          iconColor="text-blue-600 dark:text-blue-400"
          iconBgColor="bg-blue-100 dark:bg-blue-900/30"
        />
        <KPICard
          title="Avg Response Time"
          value={kpiData.avgResponseTime}
          change={kpiData.avgResponseTimeChange}
          icon={Timer}
          iconColor="text-green-600 dark:text-green-400"
          iconBgColor="bg-green-100 dark:bg-green-900/30"
        />
        <KPICard
          title="Resolution Rate"
          value={`${kpiData.resolutionRate}%`}
          change={kpiData.resolutionRateChange}
          icon={Target}
          iconColor="text-purple-600 dark:text-purple-400"
          iconBgColor="bg-purple-100 dark:bg-purple-900/30"
        />
        <KPICard
          title="Customer Satisfaction"
          value={`${kpiData.customerSatisfaction}/5`}
          change={kpiData.customerSatisfactionChange}
          changeLabel="vs last month"
          icon={TrendingUp}
          iconColor="text-yellow-600 dark:text-yellow-400"
          iconBgColor="bg-yellow-100 dark:bg-yellow-900/30"
        />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Open Tickets"
          value={kpiData.openTickets}
          change={kpiData.openTicketsChange}
          icon={Clock}
          iconColor="text-orange-600 dark:text-orange-400"
          iconBgColor="bg-orange-100 dark:bg-orange-900/30"
        />
        <KPICard
          title="SLA Compliance"
          value={`${kpiData.slaCompliance}%`}
          change={kpiData.slaComplianceChange}
          icon={CheckCircle}
          iconColor="text-green-600 dark:text-green-400"
          iconBgColor="bg-green-100 dark:bg-green-900/30"
        />
        <KPICard
          title="Avg Resolution Time"
          value={kpiData.avgResolutionTime}
          change={kpiData.avgResolutionTimeChange}
          icon={AlertTriangle}
          iconColor="text-red-600 dark:text-red-400"
          iconBgColor="bg-red-100 dark:bg-red-900/30"
        />
        <KPICard
          title="Active Agents"
          value={kpiData.activeAgents}
          change={kpiData.activeAgentsChange}
          icon={Users}
          iconColor="text-indigo-600 dark:text-indigo-400"
          iconBgColor="bg-indigo-100 dark:bg-indigo-900/30"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartPlaceholder
          type="line"
          title="Ticket Volume Trend"
          subtitle="Daily ticket submissions over time"
        />
        <ChartPlaceholder
          type="bar"
          title="Tickets by Category"
          subtitle="Distribution across categories"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartPlaceholder
          type="pie"
          title="Status Distribution"
          subtitle="Current ticket status breakdown"
        />
        <div className="lg:col-span-2">
          <ChartPlaceholder
            type="area"
            title="Response Time Trends"
            subtitle="Average response and resolution times"
          />
        </div>
      </div>

      {/* Filters */}
      <FilterControls
        statusFilter={statusFilter}
        priorityFilter={priorityFilter}
        categoryFilter={categoryFilter}
        onStatusChange={setStatusFilter}
        onPriorityChange={setPriorityFilter}
        onCategoryChange={setCategoryFilter}
        onClearFilters={handleClearFilters}
      />

      {/* Data Table */}
      <DataTable
        title="Ticket Performance Metrics"
        columns={tableColumns}
        data={tableData}
        onExport={handleExport}
      />
    </div>
  );
}
