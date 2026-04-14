import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../components/ui/Button';

const meta: Meta<typeof Button> = {
  title: 'Design System/Inputs/Button',
  component: Button,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'ghost', 'danger', 'glass'] },
    size: { control: 'select', options: ['sm', 'md', 'lg', 'icon'] },
    loading: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
};
export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { children: 'Primary Button', variant: 'primary' } };
export const Secondary: Story = { args: { children: 'Secondary Button', variant: 'secondary' } };
export const Ghost: Story = { args: { children: 'Ghost Button', variant: 'ghost' } };
export const Danger: Story = { args: { children: 'Danger Button', variant: 'danger' } };
export const Glass: Story = { args: { children: 'Glass Button', variant: 'glass' } };
export const Loading: Story = { args: { children: 'Loading...', loading: true } };
export const Disabled: Story = { args: { children: 'Disabled', disabled: true } };
export const Small: Story = { args: { children: 'Small', size: 'sm' } };
export const Large: Story = { args: { children: 'Large Button', size: 'lg' } };
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3 p-6">
      {(['primary', 'secondary', 'ghost', 'danger', 'glass'] as const).map(v => (
        <Button key={v} variant={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</Button>
      ))}
    </div>
  ),
};
