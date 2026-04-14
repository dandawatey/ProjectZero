import React from 'react';
import { cn } from '../../design/cn';

export interface ProgressProps {
  value: number;
  max?: number;
  size?: 'xs' | 'sm' | 'md';
  variant?: 'primary' | 'success' | 'warning' | 'error';
  label?: string;
  showValue?: boolean;
  animate?: boolean;
}

const variantColors = {
  primary: 'bg-indigo-500',
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  error: 'bg-red-500',
};
const trackHeights = { xs: 'h-1', sm: 'h-2', md: 'h-3' };

export const Progress: React.FC<ProgressProps> = ({
  value, max = 100, size = 'sm', variant = 'primary', label, showValue = false, animate = true,
}) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="flex flex-col gap-1.5">
      {(label || showValue) && (
        <div className="flex justify-between text-xs text-slate-400">
          {label && <span>{label}</span>}
          {showValue && <span>{Math.round(pct)}%</span>}
        </div>
      )}
      <div className={cn('w-full bg-white/[0.08] rounded-full overflow-hidden', trackHeights[size])}>
        <div
          className={cn(variantColors[variant], 'h-full rounded-full', animate && 'transition-all duration-500 ease-out')}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};
