import React from 'react';
import { cn } from '../../design/cn';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action, className }) => (
  <div className={cn('flex flex-col items-center justify-center py-16 px-6 text-center', className)}>
    {icon && (
      <div className="mb-4 p-4 rounded-2xl bg-white/[0.06] text-slate-400 text-3xl">
        {icon}
      </div>
    )}
    <h3 className="text-base font-semibold text-slate-200">{title}</h3>
    {description && <p className="mt-2 text-sm text-slate-500 max-w-sm">{description}</p>}
    {action && <div className="mt-6">{action}</div>}
  </div>
);
