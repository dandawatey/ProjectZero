import React, { createContext, useContext, useState } from 'react';
import { cn } from '../../design/cn';

interface TabsCtx { active: string; setActive: (v: string) => void; }
const TabsContext = createContext<TabsCtx>({ active: '', setActive: () => {} });

export interface TabsProps { defaultValue: string; children: React.ReactNode; className?: string; }
export interface TabListProps { children: React.ReactNode; className?: string; }
export interface TabProps { value: string; children: React.ReactNode; disabled?: boolean; }
export interface TabPanelProps { value: string; children: React.ReactNode; className?: string; }

export const Tabs: React.FC<TabsProps> = ({ defaultValue, children, className }) => {
  const [active, setActive] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      <div className={cn('flex flex-col', className)}>{children}</div>
    </TabsContext.Provider>
  );
};

export const TabList: React.FC<TabListProps> = ({ children, className }) => (
  <div role="tablist" className={cn('flex gap-1 p-1 bg-white/[0.05] border border-white/[0.08] rounded-xl', className)}>
    {children}
  </div>
);

export const Tab: React.FC<TabProps> = ({ value, children, disabled = false }) => {
  const { active, setActive } = useContext(TabsContext);
  const isActive = active === value;
  return (
    <button
      role="tab"
      aria-selected={isActive}
      disabled={disabled}
      onClick={() => setActive(value)}
      className={cn(
        'flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
        isActive ? 'bg-white/[0.12] text-slate-100 shadow-glass' : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.06]',
        disabled && 'opacity-50 cursor-not-allowed',
      )}
    >
      {children}
    </button>
  );
};

export const TabPanel: React.FC<TabPanelProps> = ({ value, children, className }) => {
  const { active } = useContext(TabsContext);
  if (active !== value) return null;
  return <div role="tabpanel" className={cn('mt-4', className)}>{children}</div>;
};
