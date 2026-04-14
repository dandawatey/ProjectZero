import type { Meta, StoryObj } from '@storybook/react';
import { Input } from '../components/ui/Input';

const meta: Meta<typeof Input> = {
  title: 'Design System/Inputs/Input',
  component: Input,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = { args: { label: 'Email', placeholder: 'you@example.com', type: 'email' } };
export const WithHelperText: Story = { args: { label: 'Username', helperText: 'Only letters and numbers', placeholder: 'john_doe' } };
export const WithError: Story = { args: { label: 'Password', error: 'Password too short', type: 'password', value: '123' } };
export const Disabled: Story = { args: { label: 'Disabled Field', disabled: true, value: 'Cannot edit' } };
