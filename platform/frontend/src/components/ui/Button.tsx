import React from 'react';
import { cn } from '../../design/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'glass';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variants = {
  primary: 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-glow border border-indigo-500/50',
  secondary: 'bg-white/[0.10] hover:bg-white/[0.16] text-slate-100 border border-white/[0.12]',
  ghost: 'bg-transparent hover:bg-white/[0.08] text-slate-300 hover:text-slate-100 border border-transparent',
  danger: 'bg-red-600/80 hover:bg-red-500 text-white border border-red-500/50',
  glass: 'bg-white/[0.08] backdrop-blur-[8px] hover:bg-white/[0.14] text-slate-100 border border-white/[0.12]',
};
const sizes = {
  sm: 'h-8 px-3 text-sm gap-1.5',
  md: 'h-10 px-4 text-sm gap-2',
  lg: 'h-12 px-6 text-base gap-2',
  icon: 'h-10 w-10 p-0',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading = false, leftIcon, rightIcon, className, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      ) : leftIcon}
      {size !== 'icon' && children}
      {!loading && rightIcon}
    </button>
  )
);
Button.displayName = 'Button';
