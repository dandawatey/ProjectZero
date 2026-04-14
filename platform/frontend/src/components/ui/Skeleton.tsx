import React from 'react';
import { cn } from '../../design/cn';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'rect' | 'circle';
  width?: string;
  height?: string;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'rect', width, height, lines = 1, className, style, ...props
}) => {
  if (variant === 'text' && lines > 1) {
    return (
      <div className="flex flex-col gap-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className={cn(
            'animate-pulse bg-white/[0.08] rounded',
            i === lines - 1 ? 'w-3/4 h-3' : 'w-full h-3',
          )} />
        ))}
      </div>
    );
  }
  return (
    <div
      className={cn(
        'animate-pulse bg-white/[0.08]',
        variant === 'circle' ? 'rounded-full' : 'rounded-lg',
        variant === 'text' ? 'h-3 rounded' : '',
        className,
      )}
      style={{ width: width ?? (variant === 'circle' ? '2.5rem' : undefined), height: height ?? (variant === 'circle' ? '2.5rem' : undefined), ...style }}
      {...props}
    />
  );
};
