import React, { useState } from 'react';
import { cn } from '../../design/cn';

export interface AccordionItem { id: string; title: string; content: React.ReactNode; }
export interface AccordionProps { items: AccordionItem[]; defaultOpen?: string; className?: string; }

export const Accordion: React.FC<AccordionProps> = ({ items, defaultOpen, className }) => {
  const [open, setOpen] = useState<string | null>(defaultOpen ?? null);
  return (
    <div className={cn('flex flex-col divide-y divide-white/[0.08]', className)}>
      {items.map(item => (
        <div key={item.id}>
          <button
            onClick={() => setOpen(open === item.id ? null : item.id)}
            className="w-full flex items-center justify-between py-4 text-sm font-medium text-slate-200 hover:text-white transition-colors"
            aria-expanded={open === item.id}
          >
            {item.title}
            <span className={cn('text-slate-400 transition-transform duration-200', open === item.id && 'rotate-180')}>▾</span>
          </button>
          {open === item.id && (
            <div className="pb-4 text-sm text-slate-400 animate-fade-in">{item.content}</div>
          )}
        </div>
      ))}
    </div>
  );
};
