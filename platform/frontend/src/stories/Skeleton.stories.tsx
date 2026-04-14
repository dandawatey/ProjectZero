import type { Meta, StoryObj } from '@storybook/react';
import { Skeleton } from '../components/ui/Skeleton';

const meta: Meta<typeof Skeleton> = {
  title: 'Design System/Feedback/Skeleton',
  component: Skeleton,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Skeleton>;

export const Card: Story = {
  render: () => (
    <div className="p-6 bg-slate-950 w-80 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <Skeleton variant="circle" />
        <div className="flex-1 flex flex-col gap-2">
          <Skeleton variant="text" width="60%" height="14px" />
          <Skeleton variant="text" width="40%" height="12px" />
        </div>
      </div>
      <Skeleton variant="rect" height="120px" />
      <Skeleton variant="text" lines={3} />
    </div>
  ),
};
