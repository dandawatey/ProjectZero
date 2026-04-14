import React from 'react';
import { cn } from '../../design/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  dot?: boolean;
}

const variants = {
  default: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  success: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  error:   'bg-red-500/20 text-red-300 border-red-500/30',
  info:    'bg-blue-500/20 text-blue-300 border-blue-500/30',
  neutral: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
};
const sizes = { sm: 'text-xs px-2 py-0.5', md: 'text-sm px-2.5 py-1' };

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', size = 'sm', dot = false, className, children, ...props }) => (
  <span
    className={cn(
      'inline-flex items-center gap-1.5 rounded-full border font-medium',
      variants[variant], sizes[size], className,
    )}
    {...props}
  >
    {dot && <span className={cn('w-1.5 h-1.5 rounded-full bg-current')} />}
    {children}
  </span>
);
