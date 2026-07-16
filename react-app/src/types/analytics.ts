export interface KPIData {
  id: string;
  title: string;
  value: string | number;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: 'revenue' | 'users' | 'orders' | 'conversion' | 'pageviews' | 'sessions';
  prefix?: string;
  suffix?: string;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  label?: string;
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (value: unknown, row: TableRow) => React.ReactNode;
}

export interface TableRow {
  id: string;
  [key: string]: unknown;
}

export interface DateRange {
  start: Date;
  end: Date;
  label?: string;
}

export interface FilterOption {
  value: string;
  label: string;
}

export interface AnalyticsFilter {
  id: string;
  label: string;
  type: 'select' | 'multiselect' | 'search';
  options?: FilterOption[];
  value: string | string[];
}

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'donut';

export interface ChartConfig {
  type: ChartType;
  title: string;
  data: ChartDataPoint[] | TimeSeriesData[];
  height?: number;
  showLegend?: boolean;
  colors?: string[];
}
