import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from '../components/ui/Badge';

const meta: Meta<typeof Badge> = {
  title: 'Design System/Feedback/Badge',
  component: Badge,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Badge>;

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2 p-4">
      {(['default', 'success', 'warning', 'error', 'info', 'neutral'] as const).map(v => (
        <Badge key={v} variant={v} dot>{v}</Badge>
      ))}
    </div>
  ),
};
