import React from 'react';
import { cn } from '../../design/cn';

export interface Column<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  render?: (row: T, i: number) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: keyof T | ((row: T) => string);
  loading?: boolean;
  emptyState?: React.ReactNode;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function Table<T extends object>({
  columns, data, rowKey, loading = false, emptyState, onRowClick, className,
}: TableProps<T>) {
  const getKey = (row: T, i: number) =>
    typeof rowKey === 'function' ? rowKey(row) : String(row[rowKey] ?? i);

  return (
    <div className={cn('w-full overflow-auto rounded-xl border border-white/[0.10]', className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/[0.08] bg-white/[0.04]">
            {columns.map(col => (
              <th key={String(col.key)} style={{ width: col.width }}
                className={cn('px-4 py-3 font-medium text-slate-400 text-left whitespace-nowrap',
                  col.align === 'center' && 'text-center',
                  col.align === 'right' && 'text-right',
                )}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="border-b border-white/[0.05]">
                {columns.map((col, j) => (
                  <td key={j} className="px-4 py-3">
                    <div className="h-4 bg-white/[0.06] rounded animate-pulse" />
                  </td>
                ))}
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr><td colSpan={columns.length} className="px-4 py-12 text-center text-slate-500">{emptyState ?? 'No data'}</td></tr>
          ) : (
            data.map((row, i) => (
              <tr key={getKey(row, i)}
                onClick={() => onRowClick?.(row)}
                className={cn(
                  'border-b border-white/[0.05] transition-colors duration-100',
                  onRowClick && 'cursor-pointer hover:bg-white/[0.04]',
                )}>
                {columns.map(col => (
                  <td key={String(col.key)}
                    className={cn('px-4 py-3 text-slate-200',
                      col.align === 'center' && 'text-center',
                      col.align === 'right' && 'text-right',
                    )}>
                    {col.render ? col.render(row, i) : String((row as Record<string, unknown>)[col.key as string] ?? '')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
