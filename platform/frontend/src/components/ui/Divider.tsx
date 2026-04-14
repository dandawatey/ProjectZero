import React from 'react';
import { cn } from '../../design/cn';

export interface DividerProps { label?: string; className?: string; vertical?: boolean; }

export const Divider: React.FC<DividerProps> = ({ label, className, vertical = false }) => {
  if (vertical) return <div className={cn('w-px self-stretch bg-white/[0.10]', className)} />;
  if (!label) return <hr className={cn('border-0 border-t border-white/[0.10]', className)} />;
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <hr className="flex-1 border-0 border-t border-white/[0.10]" />
      <span className="text-xs text-slate-500 font-medium">{label}</span>
      <hr className="flex-1 border-0 border-t border-white/[0.10]" />
    </div>
  );
};
