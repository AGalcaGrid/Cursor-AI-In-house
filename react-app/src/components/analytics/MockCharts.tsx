import { useState, useEffect } from 'react';

interface MockLineChartProps {
  title: string;
  data?: number[];
  height?: number;
  color?: string;
  showGrid?: boolean;
  animated?: boolean;
}

export function MockLineChart({ 
  title, 
  data = [30, 45, 35, 50, 40, 60, 55, 70, 65, 80, 75, 90],
  height = 300,
  color = '#3B82F6',
  showGrid = true,
  animated = true
}: MockLineChartProps) {
  const [animatedData, setAnimatedData] = useState(animated ? data.map(() => 0) : data);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setAnimatedData(data), 100);
      return () => clearTimeout(timer);
    }
  }, [data, animated]);

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = animatedData.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 80 - 10;
    return `${x},${y}`;
  }).join(' ');

  const areaPoints = `0,100 ${points} 100,100`;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{data[data.length - 1].toLocaleString()}</span>
          <span className="text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30 px-2 py-0.5 rounded-full">
            +12.5%
          </span>
        </div>
      </div>
      <div className="p-4" style={{ height: `${height}px` }}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
          {showGrid && (
            <g className="text-gray-200 dark:text-gray-700">
              {[0, 25, 50, 75, 100].map((y) => (
                <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="currentColor" strokeWidth="0.2" />
              ))}
              {[0, 25, 50, 75, 100].map((x) => (
                <line key={x} x1={x} y1="0" x2={x} y2="100" stroke="currentColor" strokeWidth="0.2" />
              ))}
            </g>
          )}
          <defs>
            <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon
            points={areaPoints}
            fill={`url(#gradient-${title})`}
            className="transition-all duration-1000 ease-out"
          />
          <polyline
            points={points}
            fill="none"
            stroke={color}
            strokeWidth="0.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-all duration-1000 ease-out"
          />
          {animatedData.map((value, index) => {
            const x = (index / (data.length - 1)) * 100;
            const y = 100 - ((value - min) / range) * 80 - 10;
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="1.5"
                fill={color}
                className="transition-all duration-1000 ease-out"
              />
            );
          })}
        </svg>
        <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month) => (
            <span key={month}>{month}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

interface MockBarChartProps {
  title: string;
  data?: { label: string; value: number; color?: string }[];
  height?: number;
  animated?: boolean;
}

export function MockBarChart({
  title,
  data = [
    { label: 'Electronics', value: 45200, color: '#3B82F6' },
    { label: 'Clothing', value: 38900, color: '#8B5CF6' },
    { label: 'Home', value: 28400, color: '#EC4899' },
    { label: 'Sports', value: 24100, color: '#F97316' },
    { label: 'Books', value: 18700, color: '#22C55E' },
  ],
  height = 300,
  animated = true
}: MockBarChartProps) {
  const [animatedValues, setAnimatedValues] = useState(animated ? data.map(() => 0) : data.map(d => d.value));

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setAnimatedValues(data.map(d => d.value)), 100);
      return () => clearTimeout(timer);
    }
  }, [data, animated]);

  const max = Math.max(...data.map(d => d.value));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>
      <div className="p-5" style={{ height: `${height}px` }}>
        <div className="flex items-end justify-around h-full gap-3">
          {data.map((item, index) => (
            <div key={item.label} className="flex flex-col items-center flex-1">
              <div className="w-full flex flex-col items-center justify-end" style={{ height: 'calc(100% - 40px)' }}>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  ${(animatedValues[index] / 1000).toFixed(0)}k
                </span>
                <div
                  className="w-full max-w-12 rounded-t-lg transition-all duration-1000 ease-out"
                  style={{
                    height: `${(animatedValues[index] / max) * 100}%`,
                    backgroundColor: item.color || '#3B82F6',
                    minHeight: '4px'
                  }}
                />
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400 mt-2 truncate max-w-full">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface MockDonutChartProps {
  title: string;
  data?: { label: string; value: number; color: string }[];
  height?: number;
  animated?: boolean;
}

export function MockDonutChart({
  title,
  data = [
    { label: 'Direct', value: 35, color: '#3B82F6' },
    { label: 'Organic', value: 28, color: '#22C55E' },
    { label: 'Referral', value: 22, color: '#F97316' },
    { label: 'Social', value: 15, color: '#8B5CF6' },
  ],
  height = 280,
  animated = true
}: MockDonutChartProps) {
  const [animationProgress, setAnimationProgress] = useState(animated ? 0 : 1);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setAnimationProgress(1), 100);
      return () => clearTimeout(timer);
    }
  }, [animated]);

  const total = data.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -90;

  const segments = data.map((item) => {
    const angle = (item.value / total) * 360 * animationProgress;
    const startAngle = currentAngle;
    currentAngle += angle;
    
    const startRad = (startAngle * Math.PI) / 180;
    const endRad = ((startAngle + angle) * Math.PI) / 180;
    
    const x1 = 50 + 40 * Math.cos(startRad);
    const y1 = 50 + 40 * Math.sin(startRad);
    const x2 = 50 + 40 * Math.cos(endRad);
    const y2 = 50 + 40 * Math.sin(endRad);
    
    const largeArc = angle > 180 ? 1 : 0;
    
    return {
      ...item,
      path: `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`
    };
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>
      <div className="p-5 flex items-center gap-6" style={{ height: `${height}px` }}>
        <div className="relative flex-shrink-0" style={{ width: '160px', height: '160px' }}>
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-0">
            {segments.map((segment, index) => (
              <path
                key={index}
                d={segment.path}
                fill={segment.color}
                className="transition-all duration-1000 ease-out"
                style={{ opacity: animationProgress }}
              />
            ))}
            <circle cx="50" cy="50" r="25" className="fill-white dark:fill-gray-800" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{total}%</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
            </div>
          </div>
        </div>
        <div className="flex-1 space-y-3">
          {data.map((item) => (
            <div key={item.label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-gray-600 dark:text-gray-400">{item.label}</span>
              </div>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface MockAreaChartProps {
  title: string;
  series?: { name: string; data: number[]; color: string }[];
  height?: number;
  animated?: boolean;
}

export function MockAreaChart({
  title,
  series = [
    { name: 'Revenue', data: [20, 35, 30, 45, 40, 55, 50, 65, 60, 75, 70, 85], color: '#3B82F6' },
    { name: 'Expenses', data: [15, 25, 20, 30, 25, 35, 30, 40, 35, 45, 40, 50], color: '#EF4444' },
  ],
  height = 300,
  animated = true
}: MockAreaChartProps) {
  const [animationProgress, setAnimationProgress] = useState(animated ? 0 : 1);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setAnimationProgress(1), 100);
      return () => clearTimeout(timer);
    }
  }, [animated]);

  const allValues = series.flatMap(s => s.data);
  const max = Math.max(...allValues);
  const min = Math.min(...allValues);
  const range = max - min || 1;

  const getPoints = (data: number[]) => {
    return data.map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const animatedValue = min + (value - min) * animationProgress;
      const y = 100 - ((animatedValue - min) / range) * 80 - 10;
      return `${x},${y}`;
    }).join(' ');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
        <div className="flex items-center gap-4">
          {series.map((s) => (
            <div key={s.name} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
              <span className="text-xs text-gray-500 dark:text-gray-400">{s.name}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="p-4" style={{ height: `${height}px` }}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
          <g className="text-gray-200 dark:text-gray-700">
            {[0, 25, 50, 75, 100].map((y) => (
              <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="currentColor" strokeWidth="0.2" />
            ))}
          </g>
          {series.map((s, idx) => (
            <g key={s.name}>
              <defs>
                <linearGradient id={`area-gradient-${idx}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={s.color} stopOpacity="0.3" />
                  <stop offset="100%" stopColor={s.color} stopOpacity="0" />
                </linearGradient>
              </defs>
              <polygon
                points={`0,100 ${getPoints(s.data)} 100,100`}
                fill={`url(#area-gradient-${idx})`}
                className="transition-all duration-1000 ease-out"
              />
              <polyline
                points={getPoints(s.data)}
                fill="none"
                stroke={s.color}
                strokeWidth="0.8"
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </g>
          ))}
        </svg>
        <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month) => (
            <span key={month}>{month}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

// Skeleton Loaders
export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-pulse">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
      <div className="p-5" style={{ height: `${height}px` }}>
        <div className="w-full h-full bg-gray-100 dark:bg-gray-700/50 rounded-lg" />
      </div>
    </div>
  );
}

export function KPISkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        <div className="w-16 h-5 bg-gray-200 dark:bg-gray-700 rounded-full" />
      </div>
      <div className="mt-4">
        <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
        <div className="h-4 w-20 bg-gray-100 dark:bg-gray-700/50 rounded" />
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-pulse">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>
      <div className="p-5 space-y-4">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="h-4 flex-1 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
