import type { Meta, StoryObj } from '@storybook/react';
import { Progress } from '../components/ui/Progress';

const meta: Meta<typeof Progress> = {
  title: 'Design System/Feedback/Progress',
  component: Progress,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Progress>;

export const Default: Story = { args: { value: 65, label: 'Loading', showValue: true } };
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4 p-6 bg-slate-950 w-80">
      {(['primary', 'success', 'warning', 'error'] as const).map(v => (
        <Progress key={v} value={Math.random() * 80 + 10} variant={v} label={v} showValue />
      ))}
    </div>
  ),
};
