import React from 'react';
import { cn } from '../../design/cn';

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  description?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, description, className, id, ...props }, ref) => {
    const checkId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <label htmlFor={checkId} className="flex items-start gap-3 cursor-pointer group">
        <div className="relative mt-0.5">
          <input
            ref={ref}
            type="checkbox"
            id={checkId}
            className="sr-only peer"
            {...props}
          />
          <div className={cn(
            'w-4 h-4 rounded border border-white/[0.20] bg-white/[0.06]',
            'peer-checked:bg-indigo-600 peer-checked:border-indigo-600',
            'peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500',
            'transition-all duration-150',
            className,
          )}>
            <svg className="hidden peer-checked:block w-3 h-3 text-white absolute inset-0.5" viewBox="0 0 12 12" fill="none">
              <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
        {(label || description) && (
          <div>
            {label && <p className="text-sm font-medium text-slate-200">{label}</p>}
            {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
          </div>
        )}
      </label>
    );
  }
);
Checkbox.displayName = 'Checkbox';
