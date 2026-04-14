import type { Meta, StoryObj } from '@storybook/react';
import { GlassPanel } from '../components/ui/GlassPanel';

const meta: Meta<typeof GlassPanel> = {
  title: 'Design System/Foundation/GlassPanel',
  component: GlassPanel,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof GlassPanel>;

const Content = () => <div className="p-6 text-slate-200">Glass panel content</div>;

export const Default: Story = { args: { variant: 'default', children: <Content /> } };
export const Medium: Story = { args: { variant: 'medium', children: <Content /> } };
export const Strong: Story = { args: { variant: 'strong', children: <Content /> } };
export const Modal: Story = { args: { variant: 'modal', children: <Content /> } };
export const WithGlow: Story = { args: { variant: 'medium', glow: true, children: <Content /> } };
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4 p-8 bg-slate-950 min-w-[400px]">
      {(['default', 'medium', 'strong', 'modal'] as const).map(v => (
        <GlassPanel key={v} variant={v} className="p-4">
          <span className="text-slate-300 text-sm font-medium">variant: {v}</span>
        </GlassPanel>
      ))}
    </div>
  ),
};
