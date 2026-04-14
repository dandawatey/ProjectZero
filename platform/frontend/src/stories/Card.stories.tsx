import type { Meta, StoryObj } from '@storybook/react';
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

const meta: Meta<typeof Card> = {
  title: 'Design System/Foundation/Card',
  component: Card,
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <span className="text-slate-100 font-semibold">Card Title</span>
        <Button variant="ghost" size="sm">Action</Button>
      </CardHeader>
      <CardBody>
        <p className="text-slate-400 text-sm">Card body content goes here. Describe the main content of the card.</p>
      </CardBody>
      <CardFooter>
        <div className="flex gap-2">
          <Button variant="primary" size="sm">Confirm</Button>
          <Button variant="ghost" size="sm">Cancel</Button>
        </div>
      </CardFooter>
    </Card>
  ),
};

export const Hoverable: Story = {
  render: () => (
    <Card hover className="w-80 cursor-pointer">
      <p className="text-slate-200 font-medium">Hover me</p>
      <p className="text-slate-400 text-sm mt-1">This card has hover effects.</p>
    </Card>
  ),
};
