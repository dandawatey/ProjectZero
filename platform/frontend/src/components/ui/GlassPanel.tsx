import React from 'react';
import { cn } from '../../design/cn';

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'medium' | 'strong' | 'modal';
  rounded?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
  glow?: boolean;
  glowColor?: 'primary' | 'accent';
  noBorder?: boolean;
}

const variantClasses = {
  default: 'bg-white/[0.08] backdrop-blur-[16px] border border-white/[0.10]',
  medium:  'bg-white/[0.12] backdrop-blur-[16px] border border-white/[0.16]',
  strong:  'bg-white/[0.18] backdrop-blur-[16px] border border-white/[0.20]',
  modal:   'bg-slate-900/80 backdrop-blur-[24px] border border-white/[0.12]',
};
const roundedClasses = {
  none: 'rounded-none', sm: 'rounded-md', md: 'rounded-xl', lg: 'rounded-2xl', xl: 'rounded-3xl',
};

export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ variant = 'default', rounded = 'md', glow = false, glowColor = 'primary', noBorder = false, className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        variantClasses[variant],
        roundedClasses[rounded],
        glow && glowColor === 'primary' && 'shadow-glow',
        glow && glowColor === 'accent' && 'shadow-glow-accent',
        noBorder && 'border-0',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
);
GlassPanel.displayName = 'GlassPanel';
