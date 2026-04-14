import React from 'react';
import { cn } from '../../design/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}
export interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

const paddings = { none: 'p-0', sm: 'p-4', md: 'p-6', lg: 'p-8' };

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ padding = 'md', hover = false, className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'bg-white/[0.08] backdrop-blur-[16px] border border-white/[0.10] rounded-xl',
        'shadow-glass',
        hover && 'transition-all duration-200 hover:bg-white/[0.12] hover:border-white/[0.18] hover:shadow-glass-md cursor-pointer',
        paddings[padding],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
);
Card.displayName = 'Card';

export const CardHeader: React.FC<CardHeaderProps> = ({ className, ...props }) => (
  <div className={cn('flex items-center justify-between pb-4 border-b border-white/[0.08] mb-4', className)} {...props} />
);

export const CardBody: React.FC<CardBodyProps> = ({ className, ...props }) => (
  <div className={cn('', className)} {...props} />
);

export const CardFooter: React.FC<CardFooterProps> = ({ className, ...props }) => (
  <div className={cn('pt-4 border-t border-white/[0.08] mt-4', className)} {...props} />
);
