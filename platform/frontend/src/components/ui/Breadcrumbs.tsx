import React from 'react';
import { cn } from '../../design/cn';

export interface BreadcrumbItem { label: string; href?: string; }
export interface BreadcrumbsProps { items: BreadcrumbItem[]; className?: string; }

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className }) => (
  <nav aria-label="Breadcrumb" className={cn('flex items-center gap-1.5 text-sm', className)}>
    {items.map((item, i) => (
      <React.Fragment key={i}>
        {i > 0 && <span className="text-slate-600">/</span>}
        {item.href && i < items.length - 1 ? (
          <a href={item.href} className="text-slate-400 hover:text-slate-200 transition-colors">{item.label}</a>
        ) : (
          <span className={cn(i === items.length - 1 ? 'text-slate-100 font-medium' : 'text-slate-400')}>
            {item.label}
          </span>
        )}
      </React.Fragment>
    ))}
  </nav>
);
