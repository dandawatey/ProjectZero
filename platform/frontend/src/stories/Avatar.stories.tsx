import type { Meta, StoryObj } from '@storybook/react';
import { Avatar } from '../components/ui/Avatar';

const meta: Meta<typeof Avatar> = {
  title: 'Design System/Data Display/Avatar',
  component: Avatar,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Avatar>;

export const WithName: Story = { args: { name: 'Yogesh Dandawate', size: 'md', status: 'online' } };
export const Sizes: Story = {
  render: () => (
    <div className="flex items-end gap-3 p-4">
      {(['xs', 'sm', 'md', 'lg', 'xl'] as const).map(s => (
        <Avatar key={s} name="YD" size={s} status="online" />
      ))}
    </div>
  ),
};
