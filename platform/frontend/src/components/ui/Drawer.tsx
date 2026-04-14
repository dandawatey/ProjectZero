import React, { useEffect } from 'react';
import { cn } from '../../design/cn';

export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  side?: 'left' | 'right';
  width?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({
  open, onClose, title, side = 'right', width = 'w-96', children, footer,
}) => {
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, [open, onClose]);

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-[300]" role="dialog" aria-modal>
          <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-[4px]" onClick={onClose} />
          <div className={cn(
            'absolute top-0 bottom-0 flex flex-col',
            'bg-slate-900/95 backdrop-blur-[24px] border-white/[0.12]',
            side === 'right' ? 'right-0 border-l' : 'left-0 border-r',
            width,
          )}>
            {title && (
              <div className="flex items-center justify-between p-5 border-b border-white/[0.08]">
                <h2 className="text-base font-semibold text-slate-100">{title}</h2>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-100 transition-colors text-xl leading-none">×</button>
              </div>
            )}
            <div className="flex-1 overflow-y-auto p-5">{children}</div>
            {footer && <div className="p-5 border-t border-white/[0.08]">{footer}</div>}
          </div>
        </div>
      )}
    </>
  );
};
