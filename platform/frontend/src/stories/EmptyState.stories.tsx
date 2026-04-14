import type { Meta, StoryObj } from '@storybook/react';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';

const meta: Meta<typeof EmptyState> = {
  title: 'Design System/Feedback/EmptyState',
  component: EmptyState,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;

export const Default: StoryObj = {
  render: () => (
    <div className="bg-slate-950 p-8 w-[500px]">
      <EmptyState
        icon="🤖"
        title="No agents running"
        description="Start a workflow to see agents in action here."
        action={<Button>Start Workflow</Button>}
      />
    </div>
  ),
};
