import React from 'react';
import { cn } from '../../design/cn';

export interface AppShellProps {
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  sidebarWidth?: string;
  collapsedSidebar?: boolean;
}

export const AppShell: React.FC<AppShellProps> = ({
  sidebar, header, footer, children, className, sidebarWidth = 'w-64', collapsedSidebar = false,
}) => (
  <div className={cn('flex h-screen bg-slate-950 text-slate-100 overflow-hidden', className)}>
    {sidebar && (
      <aside className={cn(
        'flex-shrink-0 border-r border-white/[0.08]',
        'bg-slate-900/60 backdrop-blur-[16px]',
        'transition-all duration-300',
        collapsedSidebar ? 'w-16' : sidebarWidth,
      )}>
        {sidebar}
      </aside>
    )}
    <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
      {header && (
        <header className="flex-shrink-0 h-16 border-b border-white/[0.08] bg-slate-900/60 backdrop-blur-[16px] flex items-center px-6">
          {header}
        </header>
      )}
      <main className="flex-1 overflow-y-auto">{children}</main>
      {footer && (
        <footer className="flex-shrink-0 border-t border-white/[0.08] bg-slate-900/40 px-6 py-3">
          {footer}
        </footer>
      )}
    </div>
  </div>
);
