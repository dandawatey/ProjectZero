import React, { createContext, useContext, useState, useCallback } from 'react';
import { cn } from '../../design/cn';

type ToastVariant = 'success' | 'error' | 'warning' | 'info';
interface ToastItem { id: string; message: string; variant: ToastVariant; }

const variantStyles: Record<ToastVariant, string> = {
  success: 'bg-emerald-900/80 border-emerald-500/40 text-emerald-200',
  error:   'bg-red-900/80 border-red-500/40 text-red-200',
  warning: 'bg-amber-900/80 border-amber-500/40 text-amber-200',
  info:    'bg-indigo-900/80 border-indigo-500/40 text-indigo-200',
};
const icons: Record<ToastVariant, string> = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };

const ToastContext = createContext<{ toast: (msg: string, v?: ToastVariant) => void } | null>(null);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const toast = useCallback((message: string, variant: ToastVariant = 'info') => {
    const id = Math.random().toString(36).slice(2);
    setToasts(t => [...t, { id, message, variant }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[500] flex flex-col gap-2 pointer-events-none">
        {toasts.map(t => (
          <div key={t.id} className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-[16px]',
            'shadow-glass-md animate-slide-up pointer-events-auto min-w-[280px]',
            variantStyles[t.variant],
          )}>
            <span className="text-base font-bold">{icons[t.variant]}</span>
            <span className="text-sm font-medium">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx.toast;
};
