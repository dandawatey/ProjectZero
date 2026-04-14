import React from 'react';
import { cn } from '../../design/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
  leftElement?: React.ReactNode;
  rightElement?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, helperText, error, leftElement, rightElement, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-slate-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftElement && <span className="absolute left-3 text-slate-400">{leftElement}</span>}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full h-10 px-3 rounded-lg text-sm text-slate-100 placeholder:text-slate-500',
              'bg-white/[0.06] border border-white/[0.12]',
              'backdrop-blur-[8px]',
              'transition-colors duration-150',
              'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              error && 'border-red-500/70 focus:ring-red-500',
              leftElement && 'pl-9',
              rightElement && 'pr-9',
              className,
            )}
            {...props}
          />
          {rightElement && <span className="absolute right-3 text-slate-400">{rightElement}</span>}
        </div>
        {(helperText || error) && (
          <p className={cn('text-xs', error ? 'text-red-400' : 'text-slate-500')}>
            {error ?? helperText}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';
