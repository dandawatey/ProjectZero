import React from 'react';
import { cn } from '../../design/cn';

export interface ToggleProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  description?: string;
  size?: 'sm' | 'md';
}

export const Toggle = React.forwardRef<HTMLInputElement, ToggleProps>(
  ({ label, description, size = 'md', className, id, ...props }, ref) => {
    const toggleId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    const trackSize = size === 'sm' ? 'w-8 h-4' : 'w-11 h-6';
    const thumbSize = size === 'sm' ? 'w-3 h-3 peer-checked:translate-x-4' : 'w-5 h-5 peer-checked:translate-x-5';
    return (
      <label htmlFor={toggleId} className="flex items-center gap-3 cursor-pointer">
        <div className={cn('relative', trackSize)}>
          <input ref={ref} type="checkbox" id={toggleId} className="sr-only peer" {...props} />
          <div className={cn(
            'absolute inset-0 rounded-full bg-white/[0.10] border border-white/[0.12]',
            'peer-checked:bg-indigo-600 peer-checked:border-indigo-500',
            'transition-all duration-200',
          )} />
          <div className={cn(
            'absolute top-0.5 left-0.5 rounded-full bg-white shadow',
            'translate-x-0 transition-transform duration-200',
            thumbSize,
          )} />
        </div>
        {(label || description) && (
          <div>
            {label && <p className="text-sm font-medium text-slate-200">{label}</p>}
            {description && <p className="text-xs text-slate-500">{description}</p>}
          </div>
        )}
      </label>
    );
  }
);
Toggle.displayName = 'Toggle';
