import type { Meta, StoryObj } from '@storybook/react';
import { StatCard } from '../components/ui/StatCard';

const meta: Meta<typeof StatCard> = {
  title: 'Design System/Data Display/StatCard',
  component: StatCard,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof StatCard>;

export const Default: Story = {
  args: { title: 'Active Workflows', value: '42', delta: '12%', deltaPositive: true, description: 'vs last week' },
};
export const Negative: Story = {
  args: { title: 'Error Rate', value: '3.2%', delta: '0.8%', deltaPositive: false, description: 'last 24h' },
};
export const Grid: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-4 p-6 bg-slate-950 w-[600px]">
      <StatCard title="Active Workflows" value="42" delta="12%" deltaPositive />
      <StatCard title="Tickets Done" value="128" delta="8" deltaPositive />
      <StatCard title="Agents Running" value="7" delta="2" deltaPositive />
      <StatCard title="Errors" value="3" delta="1" deltaPositive={false} />
    </div>
  ),
};
