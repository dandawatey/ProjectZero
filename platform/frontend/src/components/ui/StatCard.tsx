import React from 'react';
import { cn } from '../../design/cn';

export interface StatCardProps {
  title: string;
  value: string | number;
  delta?: string;
  deltaPositive?: boolean;
  icon?: React.ReactNode;
  description?: string;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title, value, delta, deltaPositive = true, icon, description, className,
}) => (
  <div className={cn(
    'bg-white/[0.08] backdrop-blur-[16px] border border-white/[0.10] rounded-xl p-5',
    'shadow-glass hover:shadow-glass-md hover:bg-white/[0.11] transition-all duration-200',
    className,
  )}>
    <div className="flex items-start justify-between">
      <p className="text-sm font-medium text-slate-400">{title}</p>
      {icon && <div className="p-2 rounded-lg bg-white/[0.08] text-indigo-400">{icon}</div>}
    </div>
    <div className="mt-3 flex items-end gap-2">
      <span className="text-2xl font-bold text-slate-100">{value}</span>
      {delta && (
        <span className={cn('text-xs font-medium mb-0.5', deltaPositive ? 'text-emerald-400' : 'text-red-400')}>
          {deltaPositive ? '↑' : '↓'} {delta}
        </span>
      )}
    </div>
    {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
  </div>
);
