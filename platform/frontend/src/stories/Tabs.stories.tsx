import type { Meta, StoryObj } from '@storybook/react';
import { Tabs, TabList, Tab, TabPanel } from '../components/ui/Tabs';

const meta: Meta = {
  title: 'Design System/Navigation/Tabs',
  tags: ['autodocs'],
  parameters: { backgrounds: { default: 'dark' } },
};
export default meta;

export const Default: StoryObj = {
  render: () => (
    <div className="p-6 bg-slate-950 w-[500px]">
      <Tabs defaultValue="overview">
        <TabList>
          <Tab value="overview">Overview</Tab>
          <Tab value="agents">Agents</Tab>
          <Tab value="logs">Logs</Tab>
          <Tab value="settings" disabled>Settings</Tab>
        </TabList>
        <TabPanel value="overview"><p className="text-slate-400 text-sm">Overview content</p></TabPanel>
        <TabPanel value="agents"><p className="text-slate-400 text-sm">Agents content</p></TabPanel>
        <TabPanel value="logs"><p className="text-slate-400 text-sm">Logs content</p></TabPanel>
      </Tabs>
    </div>
  ),
};
