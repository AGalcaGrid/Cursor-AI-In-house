import { Card, CardHeader, CardBody } from '../shared/Card';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface ChartData {
  label: string;
  completed: number;
  total: number;
}

interface ProgressChartProps {
  data: ChartData[];
  title?: string;
  subtitle?: string;
}

export default function ProgressChart({ data, title = 'Weekly Progress', subtitle }: ProgressChartProps) {
  const maxValue = Math.max(...data.map(d => d.total));
  
  const totalCompleted = data.reduce((sum, d) => sum + d.completed, 0);
  const totalTasks = data.reduce((sum, d) => sum + d.total, 0);
  const completionRate = totalTasks > 0 ? Math.round((totalCompleted / totalTasks) * 100) : 0;
  
  const previousWeekRate = 72;
  const trend = completionRate - previousWeekRate;

  return (
    <Card padding="none">
      <CardHeader className="px-5 pt-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-gray-900">{completionRate}%</span>
          <div className={`flex items-center gap-0.5 text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>{Math.abs(trend)}%</span>
          </div>
        </div>
      </CardHeader>
      <CardBody className="px-5 pb-5">
        <div className="flex items-end justify-between gap-2 h-48">
          {data.map((item, index) => {
            const completedHeight = maxValue > 0 ? (item.completed / maxValue) * 100 : 0;
            const remainingHeight = maxValue > 0 ? ((item.total - item.completed) / maxValue) * 100 : 0;
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex flex-col justify-end h-40 gap-0.5">
                  <div
                    className="w-full bg-gray-200 rounded-t transition-all duration-300"
                    style={{ height: `${remainingHeight}%` }}
                    title={`Remaining: ${item.total - item.completed}`}
                  />
                  <div
                    className="w-full bg-blue-500 rounded-b transition-all duration-300"
                    style={{ height: `${completedHeight}%` }}
                    title={`Completed: ${item.completed}`}
                  />
                </div>
                <span className="text-xs text-gray-500 font-medium">{item.label}</span>
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded" />
            <span className="text-gray-600">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-200 rounded" />
            <span className="text-gray-600">Remaining</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
