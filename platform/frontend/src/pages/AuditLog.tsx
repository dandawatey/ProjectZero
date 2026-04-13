import React from 'react';
import { useAuditLog } from '../hooks/useWorkflows';

export default function AuditLog() {
  const { data: entries, isLoading, error } = useAuditLog();

  if (isLoading) return <p className="p-6 text-gray-500">Loading audit log...</p>;
  if (error) return <p className="p-6 text-red-600">Error: {(error as Error).message}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Audit Log</h1>

      <div className="bg-white rounded-lg shadow-sm border overflow-x-auto max-h-[calc(100vh-200px)] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 sticky top-0">
            <tr>
              <th className="px-4 py-2">Timestamp</th>
              <th className="px-4 py-2">Action</th>
              <th className="px-4 py-2">Actor</th>
              <th className="px-4 py-2">Resource</th>
              <th className="px-4 py-2">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {(entries ?? []).map((entry, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-xs text-gray-500 whitespace-nowrap">
                  {entry.timestamp ? new Date(String(entry.timestamp)).toLocaleString() : '-'}
                </td>
                <td className="px-4 py-2 font-medium">{String(entry.action ?? '-')}</td>
                <td className="px-4 py-2 text-xs">{String(entry.actor ?? entry.user ?? '-')}</td>
                <td className="px-4 py-2 text-xs font-mono">{String(entry.resource ?? entry.resource_id ?? '-')}</td>
                <td className="px-4 py-2 text-xs text-gray-600 max-w-[300px] truncate">
                  {typeof entry.details === 'object'
                    ? JSON.stringify(entry.details)
                    : String(entry.details ?? '-')}
                </td>
              </tr>
            ))}
            {(!entries || entries.length === 0) && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No audit entries</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
