import type { Preview } from '@storybook/react';
import '../src/index.css';

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0f172a' },
        { name: 'dark-mid', value: '#1e293b' },
        { name: 'light', value: '#f8fafc' },
      ],
    },
    layout: 'centered',
    docs: {
      theme: {
        base: 'dark',
        brandTitle: 'ProjectZero Design System',
        brandUrl: '/',
      },
    },
  },
};
export default preview;
