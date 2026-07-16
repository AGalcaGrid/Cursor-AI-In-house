import { useState } from 'react';
import type { TaskStats, WeeklyProgress } from '../types';

interface ProgressChartProps {
  taskStats: TaskStats[];
  weeklyProgress: WeeklyProgress[];
  totalTasks: number;
  completedTasks: number;
}

export function ProgressChart({
  taskStats,
  weeklyProgress,
  totalTasks,
  completedTasks,
}: ProgressChartProps) {
  const [view, setView] = useState<'donut' | 'bar'>('donut');

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  const maxWeeklyValue = Math.max(...weeklyProgress.flatMap((w) => [w.completed, w.created]), 1);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Task Progress</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {completedTasks} of {totalTasks} tasks completed
          </p>
        </div>
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setView('donut')}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors
              ${view === 'donut' 
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm' 
                : 'text-gray-600 dark:text-gray-300'}`}
          >
            Overview
          </button>
          <button
            onClick={() => setView('bar')}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors
              ${view === 'bar' 
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm' 
                : 'text-gray-600 dark:text-gray-300'}`}
          >
            Weekly
          </button>
        </div>
      </div>

      {view === 'donut' ? (
        <div className="flex flex-col lg:flex-row items-center gap-8">
          <div className="relative w-48 h-48">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="currentColor"
                strokeWidth="12"
                className="text-gray-200 dark:text-gray-700"
              />
              {taskStats.reduce((acc, stat, index) => {
                const previousPercentage = taskStats
                  .slice(0, index)
                  .reduce((sum, s) => sum + s.percentage, 0);
                const circumference = 2 * Math.PI * 40;
                const strokeDasharray = `${(stat.percentage / 100) * circumference} ${circumference}`;
                const strokeDashoffset = -((previousPercentage / 100) * circumference);

                acc.push(
                  <circle
                    key={stat.label}
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke={stat.color}
                    strokeWidth="12"
                    strokeDasharray={strokeDasharray}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    className="transition-all duration-500"
                  />
                );
                return acc;
              }, [] as React.ReactElement[])}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-gray-900 dark:text-white">
                {completionRate}%
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">Complete</span>
            </div>
          </div>

          <div className="flex-1 space-y-3">
            {taskStats.map((stat) => (
              <div key={stat.label} className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: stat.color }}
                />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {stat.label}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {stat.value} ({stat.percentage}%)
                    </span>
                  </div>
                  <div className="mt-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${stat.percentage}%`, backgroundColor: stat.color }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-gray-600 dark:text-gray-400">Completed</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-gray-600 dark:text-gray-400">Created</span>
            </div>
          </div>

          <div className="flex items-end gap-2 h-48">
            {weeklyProgress.map((day) => (
              <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full flex gap-1 items-end h-40">
                  <div
                    className="flex-1 bg-green-500 rounded-t transition-all duration-500"
                    style={{ height: `${(day.completed / maxWeeklyValue) * 100}%` }}
                    title={`${day.completed} completed`}
                  />
                  <div
                    className="flex-1 bg-blue-500 rounded-t transition-all duration-500"
                    style={{ height: `${(day.created / maxWeeklyValue) * 100}%` }}
                    title={`${day.created} created`}
                  />
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">{day.day}</span>
              </div>
            ))}
          </div>

          <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            <span>
              Total Completed: {weeklyProgress.reduce((sum, d) => sum + d.completed, 0)}
            </span>
            <span>
              Total Created: {weeklyProgress.reduce((sum, d) => sum + d.created, 0)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
