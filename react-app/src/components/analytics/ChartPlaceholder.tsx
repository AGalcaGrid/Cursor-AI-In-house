import type { ChartType } from '../../types/analytics';

interface ChartPlaceholderProps {
  type: ChartType;
  title: string;
  height?: number;
  className?: string;
}

const chartIcons: Record<ChartType, React.ReactNode> = {
  line: (
    <svg className="w-16 h-16 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4v16" />
    </svg>
  ),
  bar: (
    <svg className="w-16 h-16 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  pie: (
    <svg className="w-16 h-16 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
    </svg>
  ),
  area: (
    <svg className="w-16 h-16 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 3v18h18" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 17l6-6 4 4 8-8" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 17l6-6 4 4 8-8v11H3z" fill="currentColor" fillOpacity={0.1} />
    </svg>
  ),
  donut: (
    <svg className="w-16 h-16 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="9" strokeWidth={1.5} />
      <circle cx="12" cy="12" r="5" strokeWidth={1.5} />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v4M21 12h-4" />
    </svg>
  ),
};

export function ChartPlaceholder({ type, title, height = 300, className = '' }: ChartPlaceholderProps) {
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>

      {/* Chart Area */}
      <div
        className="flex flex-col items-center justify-center p-6"
        style={{ height: `${height}px` }}
      >
        {chartIcons[type]}
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          {type.charAt(0).toUpperCase() + type.slice(1)} Chart
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          Connect a charting library to display data
        </p>

        {/* Simulated chart lines for visual effect */}
        <div className="w-full mt-6 px-4">
          {type === 'line' || type === 'area' ? (
            <div className="relative h-24">
              <svg className="w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
                <path
                  d="M0,80 Q50,60 100,70 T200,40 T300,50 T400,20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="text-blue-400 dark:text-blue-500"
                />
                {type === 'area' && (
                  <path
                    d="M0,80 Q50,60 100,70 T200,40 T300,50 T400,20 V100 H0 Z"
                    fill="currentColor"
                    className="text-blue-100 dark:text-blue-900/30"
                  />
                )}
              </svg>
            </div>
          ) : type === 'bar' ? (
            <div className="flex items-end justify-around h-24 gap-2">
              {[60, 80, 45, 90, 70, 55, 85].map((h, i) => (
                <div
                  key={i}
                  className="flex-1 bg-blue-400 dark:bg-blue-500 rounded-t opacity-60"
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>
          ) : (type === 'pie' || type === 'donut') ? (
            <div className="flex justify-center gap-2 mt-2">
              {['bg-blue-400', 'bg-emerald-400', 'bg-amber-400', 'bg-purple-400'].map((color, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <div className={`w-3 h-3 rounded-full ${color}`} />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {['Sales', 'Marketing', 'Support', 'Dev'][i]}
                  </span>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
