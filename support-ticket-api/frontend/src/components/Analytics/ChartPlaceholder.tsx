import { BarChart3, LineChart, PieChart, TrendingUp } from 'lucide-react';

type ChartType = 'line' | 'bar' | 'pie' | 'area';

interface ChartPlaceholderProps {
  type: ChartType;
  title: string;
  subtitle?: string;
  height?: string;
}

export default function ChartPlaceholder({ 
  type, 
  title, 
  subtitle,
  height = 'h-64' 
}: ChartPlaceholderProps) {
  const icons = {
    line: LineChart,
    bar: BarChart3,
    pie: PieChart,
    area: TrendingUp,
  };

  const Icon = icons[type];

  // Generate mock chart visualization based on type
  const renderMockChart = () => {
    switch (type) {
      case 'line':
        return (
          <svg className="w-full h-full" viewBox="0 0 400 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" className="text-blue-500" style={{ stopColor: 'currentColor', stopOpacity: 0.3 }} />
                <stop offset="100%" className="text-blue-500" style={{ stopColor: 'currentColor', stopOpacity: 0 }} />
              </linearGradient>
            </defs>
            <path
              d="M0,150 Q50,120 100,130 T200,80 T300,100 T400,60"
              fill="none"
              className="stroke-blue-500 dark:stroke-blue-400"
              strokeWidth="3"
            />
            <path
              d="M0,150 Q50,120 100,130 T200,80 T300,100 T400,60 L400,200 L0,200 Z"
              fill="url(#lineGradient)"
            />
            {/* Data points */}
            {[
              { x: 0, y: 150 },
              { x: 100, y: 130 },
              { x: 200, y: 80 },
              { x: 300, y: 100 },
              { x: 400, y: 60 },
            ].map((point, i) => (
              <circle
                key={i}
                cx={point.x}
                cy={point.y}
                r="5"
                className="fill-blue-500 dark:fill-blue-400"
              />
            ))}
          </svg>
        );

      case 'bar':
        const bars = [65, 85, 45, 90, 70, 55, 80];
        return (
          <svg className="w-full h-full" viewBox="0 0 400 200" preserveAspectRatio="none">
            {bars.map((height, i) => (
              <g key={i}>
                <rect
                  x={i * 55 + 15}
                  y={200 - height * 1.8}
                  width="40"
                  height={height * 1.8}
                  rx="4"
                  className="fill-blue-500 dark:fill-blue-400 opacity-80 hover:opacity-100 transition-opacity"
                />
              </g>
            ))}
          </svg>
        );

      case 'pie':
        return (
          <svg className="w-full h-full" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="80" className="fill-blue-500 dark:fill-blue-400" />
            <path
              d="M100,100 L100,20 A80,80 0 0,1 172,140 Z"
              className="fill-green-500 dark:fill-green-400"
            />
            <path
              d="M100,100 L172,140 A80,80 0 0,1 60,160 Z"
              className="fill-yellow-500 dark:fill-yellow-400"
            />
            <path
              d="M100,100 L60,160 A80,80 0 0,1 28,60 Z"
              className="fill-purple-500 dark:fill-purple-400"
            />
            <circle cx="100" cy="100" r="40" className="fill-white dark:fill-gray-800" />
          </svg>
        );

      case 'area':
        return (
          <svg className="w-full h-full" viewBox="0 0 400 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id="areaGradient1" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" className="text-blue-500" style={{ stopColor: 'currentColor', stopOpacity: 0.5 }} />
                <stop offset="100%" className="text-blue-500" style={{ stopColor: 'currentColor', stopOpacity: 0.1 }} />
              </linearGradient>
              <linearGradient id="areaGradient2" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" className="text-green-500" style={{ stopColor: 'currentColor', stopOpacity: 0.5 }} />
                <stop offset="100%" className="text-green-500" style={{ stopColor: 'currentColor', stopOpacity: 0.1 }} />
              </linearGradient>
            </defs>
            <path
              d="M0,180 Q100,140 200,150 T400,100 L400,200 L0,200 Z"
              fill="url(#areaGradient1)"
            />
            <path
              d="M0,160 Q100,100 200,120 T400,70 L400,200 L0,200 Z"
              fill="url(#areaGradient2)"
            />
          </svg>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <Icon className="w-5 h-5 text-gray-500 dark:text-gray-400" aria-hidden="true" />
        </div>
      </div>
      <div className={`${height} flex items-center justify-center`}>
        {renderMockChart()}
      </div>
    </div>
  );
}
