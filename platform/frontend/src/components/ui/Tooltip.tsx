import React, { useState } from 'react';
import { cn } from '../../design/cn';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
}

const placements = {
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
  left: 'right-full top-1/2 -translate-y-1/2 mr-2',
  right: 'left-full top-1/2 -translate-y-1/2 ml-2',
};

export const Tooltip: React.FC<TooltipProps> = ({ content, children, placement = 'top', delay = 300 }) => {
  const [visible, setVisible] = useState(false);
  let timer: ReturnType<typeof setTimeout>;

  return (
    <span className="relative inline-flex"
      onMouseEnter={() => { timer = setTimeout(() => setVisible(true), delay); }}
      onMouseLeave={() => { clearTimeout(timer); setVisible(false); }}>
      {children}
      {visible && (
        <span className={cn(
          'absolute z-[100] px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap pointer-events-none',
          'bg-slate-800 text-slate-100 border border-white/[0.12] shadow-glass animate-fade-in',
          placements[placement],
        )}>
          {content}
        </span>
      )}
    </span>
  );
};
