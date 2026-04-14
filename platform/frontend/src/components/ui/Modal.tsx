import React, { useEffect } from 'react';
import { cn } from '../../design/cn';
import { Button } from './Button';

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
  hideClose?: boolean;
}

const sizes = {
  sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-lg', xl: 'max-w-2xl', full: 'max-w-5xl',
};

export const Modal: React.FC<ModalProps> = ({
  open, onClose, title, description, size = 'md', children, footer, hideClose = false,
}) => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[400] flex items-center justify-center p-4" role="dialog" aria-modal>
      <div
        className="absolute inset-0 bg-slate-950/70 backdrop-blur-[4px]"
        onClick={onClose}
        aria-hidden
      />
      <div className={cn(
        'relative w-full bg-slate-900/90 backdrop-blur-[24px]',
        'border border-white/[0.12] rounded-2xl shadow-glass-lg',
        'flex flex-col max-h-[90vh] overflow-hidden',
        sizes[size],
      )}>
        {(title || !hideClose) && (
          <div className="flex items-start justify-between p-6 pb-4 border-b border-white/[0.08]">
            <div>
              {title && <h2 className="text-lg font-semibold text-slate-100">{title}</h2>}
              {description && <p className="mt-1 text-sm text-slate-400">{description}</p>}
            </div>
            {!hideClose && (
              <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close modal">
                <span className="text-xl leading-none">×</span>
              </Button>
            )}
          </div>
        )}
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
        {footer && (
          <div className="p-6 pt-4 border-t border-white/[0.08] flex justify-end gap-3">{footer}</div>
        )}
      </div>
    </div>
  );
};
