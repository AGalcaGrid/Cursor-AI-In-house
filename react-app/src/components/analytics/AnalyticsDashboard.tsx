import { useState, useEffect, useMemo } from 'react';
import { KPICard } from './KPICard';
import { DataTable } from './DataTable';
import { FilterBar } from './FilterControls';
import { MockLineChart, MockBarChart, MockDonutChart, MockAreaChart, KPISkeleton, ChartSkeleton, TableSkeleton } from './MockCharts';
import type { KPIData, DateRange, TableColumn, TableRow } from '../../types/analytics';

interface AnalyticsDashboardProps {
  isDarkMode?: boolean;
  onToggleDarkMode?: () => void;
}

const kpiData: KPIData[] = [
  { id: '1', title: 'Total Revenue', value: 284500, change: 12.5, changeType: 'increase', icon: 'revenue', prefix: '$' },
  { id: '2', title: 'Active Users', value: 45280, change: 8.2, changeType: 'increase', icon: 'users' },
  { id: '3', title: 'Total Orders', value: 12847, change: 3.1, changeType: 'decrease', icon: 'orders' },
  { id: '4', title: 'Conversion Rate', value: '3.24', change: 0.8, changeType: 'increase', icon: 'conversion', suffix: '%' },
  { id: '5', title: 'Page Views', value: 892400, change: 15.3, changeType: 'increase', icon: 'pageviews' },
  { id: '6', title: 'Avg. Session', value: '4:32', change: 2.1, changeType: 'neutral', icon: 'sessions' },
];

const tableColumns: TableColumn[] = [
  { key: 'product', label: 'Product', sortable: true },
  { key: 'category', label: 'Category', sortable: true },
  { 
    key: 'revenue', 
    label: 'Revenue', 
    sortable: true, 
    align: 'right',
    render: (value) => `$${Number(value).toLocaleString()}`
  },
  { 
    key: 'units', 
    label: 'Units Sold', 
    sortable: true, 
    align: 'right',
    render: (value) => Number(value).toLocaleString()
  },
  { 
    key: 'growth', 
    label: 'Growth', 
    sortable: true, 
    align: 'right',
    render: (value) => {
      const num = Number(value);
      return (
        <span className={num >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}>
          {num >= 0 ? '+' : ''}{num}%
        </span>
      );
    }
  },
  {
    key: 'status',
    label: 'Status',
    render: (value) => {
      const status = value as string;
      const colors: Record<string, string> = {
        'Active': 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
        'Pending': 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
        'Inactive': 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400',
      };
      return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || colors['Inactive']}`}>
          {status}
        </span>
      );
    }
  },
];

const tableData: TableRow[] = [
  { id: '1', product: 'Wireless Headphones', category: 'Electronics', revenue: 45200, units: 1204, growth: 12.5, status: 'Active' },
  { id: '2', product: 'Smart Watch Pro', category: 'Electronics', revenue: 38900, units: 892, growth: 8.3, status: 'Active' },
  { id: '3', product: 'Leather Backpack', category: 'Accessories', revenue: 28400, units: 567, growth: -2.1, status: 'Active' },
  { id: '4', product: 'Running Shoes', category: 'Footwear', revenue: 24100, units: 445, growth: 15.7, status: 'Active' },
  { id: '5', product: 'Yoga Mat Premium', category: 'Fitness', revenue: 18700, units: 623, growth: 22.4, status: 'Active' },
  { id: '6', product: 'Coffee Maker Deluxe', category: 'Home', revenue: 15300, units: 234, growth: -5.2, status: 'Pending' },
  { id: '7', product: 'Bluetooth Speaker', category: 'Electronics', revenue: 12800, units: 412, growth: 3.8, status: 'Active' },
  { id: '8', product: 'Desk Lamp LED', category: 'Home', revenue: 9400, units: 289, growth: 7.1, status: 'Active' },
  { id: '9', product: 'Water Bottle Steel', category: 'Fitness', revenue: 7200, units: 534, growth: 18.9, status: 'Active' },
  { id: '10', product: 'Phone Case Premium', category: 'Accessories', revenue: 5800, units: 892, growth: -8.4, status: 'Inactive' },
  { id: '11', product: 'Notebook Set', category: 'Office', revenue: 4200, units: 345, growth: 4.2, status: 'Active' },
  { id: '12', product: 'USB-C Hub', category: 'Electronics', revenue: 8900, units: 267, growth: 11.3, status: 'Active' },
];

const filterOptions = {
  category: [
    { value: 'all', label: 'All Categories' },
    { value: 'electronics', label: 'Electronics' },
    { value: 'accessories', label: 'Accessories' },
    { value: 'fitness', label: 'Fitness' },
    { value: 'home', label: 'Home' },
  ],
  status: [
    { value: 'all', label: 'All Status' },
    { value: 'active', label: 'Active' },
    { value: 'pending', label: 'Pending' },
    { value: 'inactive', label: 'Inactive' },
  ],
};

export function AnalyticsDashboard({ isDarkMode = false, onToggleDarkMode }: AnalyticsDashboardProps) {
  const [dateRange, setDateRange] = useState<DateRange>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date(),
    label: 'Last 30 days',
  });
  const [filters, setFilters] = useState({
    category: 'all',
    status: 'all',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [chartsLoaded, setChartsLoaded] = useState(false);

  // Simulate initial data loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
      setTimeout(() => setChartsLoaded(true), 300);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  // Filter table data based on selected filters
  const filteredTableData = useMemo(() => {
    return tableData.filter((row) => {
      const category = row.category as string;
      const status = row.status as string;
      const categoryMatch = filters.category === 'all' || 
        category.toLowerCase() === filters.category.toLowerCase();
      const statusMatch = filters.status === 'all' || 
        status.toLowerCase() === filters.status.toLowerCase();
      return categoryMatch && statusMatch;
    });
  }, [filters]);

  const handleFilterChange = (filterId: string, value: string) => {
    setFilters((prev) => ({ ...prev, [filterId]: value }));
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setChartsLoaded(false);
    setTimeout(() => {
      setIsLoading(false);
      setTimeout(() => setChartsLoaded(true), 300);
    }, 1500);
  };

  const handleExport = () => {
    const csvContent = [
      ['Product', 'Category', 'Revenue', 'Units', 'Growth', 'Status'],
      ...filteredTableData.map(row => [
        row.product, row.category, row.revenue, row.units, row.growth, row.status
      ])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analytics-export.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Apply dark mode
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Track your business performance</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Dark Mode Toggle */}
              {onToggleDarkMode && (
                <button
                  onClick={onToggleDarkMode}
                  className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                >
                  {isDarkMode ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                  )}
                </button>
              )}
              {/* Notifications */}
              <button className="relative p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              {/* User */}
              <img
                src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"
                alt="User"
                className="w-8 h-8 rounded-full object-cover"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black/20 dark:bg-black/40 z-50 flex items-center justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-xl flex items-center gap-3">
              <svg className="animate-spin w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-gray-900 dark:text-white font-medium">Loading...</span>
            </div>
          </div>
        )}

        {/* Filter Bar */}
        <section className="mb-6" aria-label="Filters">
          <FilterBar
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            filters={[
              { id: 'category', label: 'Category', value: filters.category, options: filterOptions.category },
              { id: 'status', label: 'Status', value: filters.status, options: filterOptions.status },
            ]}
            onFilterChange={handleFilterChange}
            onRefresh={handleRefresh}
            onExport={handleExport}
          />
        </section>

        {/* KPI Cards */}
        <section className="mb-6" aria-label="Key Performance Indicators">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {isLoading ? (
              Array.from({ length: 6 }).map((_, i) => <KPISkeleton key={i} />)
            ) : (
              kpiData.map((kpi) => (
                <KPICard key={kpi.id} data={kpi} />
              ))
            )}
          </div>
        </section>

        {/* Charts Row 1 */}
        <section className="mb-6" aria-label="Charts">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {isLoading ? (
              <>
                <ChartSkeleton height={320} />
                <ChartSkeleton height={320} />
              </>
            ) : (
              <>
                <MockAreaChart 
                  title="Revenue vs Expenses" 
                  height={280}
                  animated={chartsLoaded}
                  series={[
                    { name: 'Revenue', data: [20, 35, 30, 45, 40, 55, 50, 65, 60, 75, 70, 85], color: '#3B82F6' },
                    { name: 'Expenses', data: [15, 25, 20, 30, 25, 35, 30, 40, 35, 45, 40, 50], color: '#EF4444' },
                  ]}
                />
                <MockBarChart 
                  title="Sales by Category" 
                  height={280}
                  animated={chartsLoaded}
                  data={[
                    { label: 'Electronics', value: 45200, color: '#3B82F6' },
                    { label: 'Clothing', value: 38900, color: '#8B5CF6' },
                    { label: 'Home', value: 28400, color: '#EC4899' },
                    { label: 'Sports', value: 24100, color: '#F97316' },
                    { label: 'Books', value: 18700, color: '#22C55E' },
                  ]}
                />
              </>
            )}
          </div>
        </section>

        {/* Charts Row 2 */}
        <section className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {isLoading ? (
              <>
                <ChartSkeleton height={280} />
                <ChartSkeleton height={280} />
                <ChartSkeleton height={280} />
              </>
            ) : (
              <>
                <MockDonutChart 
                  title="Traffic Sources" 
                  height={240}
                  animated={chartsLoaded}
                  data={[
                    { label: 'Direct', value: 35, color: '#3B82F6' },
                    { label: 'Organic', value: 28, color: '#22C55E' },
                    { label: 'Referral', value: 22, color: '#F97316' },
                    { label: 'Social', value: 15, color: '#8B5CF6' },
                  ]}
                />
                <MockLineChart 
                  title="User Growth" 
                  height={240}
                  animated={chartsLoaded}
                  data={[30, 45, 35, 50, 40, 60, 55, 70, 65, 80, 75, 90]}
                  color="#22C55E"
                />
                <MockDonutChart 
                  title="Device Distribution" 
                  height={240}
                  animated={chartsLoaded}
                  data={[
                    { label: 'Desktop', value: 45, color: '#3B82F6' },
                    { label: 'Mobile', value: 38, color: '#22C55E' },
                    { label: 'Tablet', value: 17, color: '#F97316' },
                  ]}
                />
              </>
            )}
          </div>
        </section>

        {/* Data Table */}
        <section aria-label="Data Table">
          {isLoading ? (
            <TableSkeleton rows={8} />
          ) : (
            <DataTable
              columns={tableColumns}
              data={filteredTableData}
              pageSize={8}
              searchable
              onRowClick={(row) => alert(`Clicked: ${row.product}`)}
            />
          )}
        </section>
      </main>
    </div>
  );
}
