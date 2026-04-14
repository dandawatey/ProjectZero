import React from 'react';
import { cn } from '../../design/cn';

export interface AvatarProps {
  src?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status?: 'online' | 'offline' | 'busy' | 'away';
  className?: string;
}

const sizes = { xs: 'w-6 h-6 text-xs', sm: 'w-8 h-8 text-sm', md: 'w-10 h-10 text-sm', lg: 'w-12 h-12 text-base', xl: 'w-16 h-16 text-lg' };
const statusColors = { online: 'bg-emerald-500', offline: 'bg-slate-500', busy: 'bg-red-500', away: 'bg-amber-500' };

function initials(name: string) {
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
}

export const Avatar: React.FC<AvatarProps> = ({ src, name, size = 'md', status, className }) => (
  <div className={cn('relative inline-flex', className)}>
    <div className={cn('rounded-full overflow-hidden bg-indigo-600/60 flex items-center justify-center text-white font-semibold border border-white/[0.12]', sizes[size])}>
      {src ? <img src={src} alt={name} className="w-full h-full object-cover" /> : name ? initials(name) : '?'}
    </div>
    {status && (
      <span className={cn('absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-slate-900', statusColors[status])} />
    )}
  </div>
);
