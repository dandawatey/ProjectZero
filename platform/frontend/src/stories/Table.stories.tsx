import type { Meta, StoryObj } from '@storybook/react';
import { Table } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';

const meta: Meta = {
  title: 'Design System/Data Display/Table',
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;

interface Row { id: string; name: string; status: string; progress: number; }
const data: Row[] = [
  { id: 'PRJ0-1', name: 'Feature Development', status: 'success', progress: 100 },
  { id: 'PRJ0-2', name: 'API Integration', status: 'warning', progress: 65 },
  { id: 'PRJ0-3', name: 'Design System', status: 'info', progress: 40 },
  { id: 'PRJ0-4', name: 'Testing Suite', status: 'error', progress: 10 },
];

export const Default: StoryObj = {
  render: () => (
    <div className="p-6 bg-slate-950 w-[700px]">
      <Table<Row>
        columns={[
          { key: 'id', header: 'Ticket', width: '100px' },
          { key: 'name', header: 'Name' },
          { key: 'status', header: 'Status', render: row => <Badge variant={row.status as any}>{row.status}</Badge> },
          { key: 'progress', header: 'Progress', render: row => `${row.progress}%`, align: 'right' },
        ]}
        data={data}
        rowKey="id"
      />
    </div>
  ),
};

export const Loading: StoryObj = {
  render: () => (
    <div className="p-6 bg-slate-950 w-[700px]">
      <Table columns={[{ key: 'id', header: 'ID' }, { key: 'name', header: 'Name' }, { key: 'status', header: 'Status' }]} data={[]} rowKey="id" loading />
    </div>
  ),
};
