import React from 'react';
import { cn } from '../../design/cn';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  helperText?: string;
  error?: string;
  options: { value: string; label: string; disabled?: boolean }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, helperText, error, options, className, id, ...props }, ref) => {
    const selectId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1.5">
        {label && <label htmlFor={selectId} className="text-sm font-medium text-slate-300">{label}</label>}
        <select
          ref={ref}
          id={selectId}
          className={cn(
            'w-full h-10 px-3 rounded-lg text-sm text-slate-100',
            'bg-white/[0.06] border border-white/[0.12]',
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'appearance-none cursor-pointer',
            error && 'border-red-500/70',
            className,
          )}
          {...props}
        >
          {options.map(o => (
            <option key={o.value} value={o.value} disabled={o.disabled} className="bg-slate-800 text-slate-100">
              {o.label}
            </option>
          ))}
        </select>
        {(helperText || error) && (
          <p className={cn('text-xs', error ? 'text-red-400' : 'text-slate-500')}>{error ?? helperText}</p>
        )}
      </div>
    );
  }
);
Select.displayName = 'Select';
