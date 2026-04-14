import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page);
  });

  const pages = [
    { path: '/app', label: 'Dashboard' },
    { path: '/app/agents', label: 'Agents' },
    { path: '/app/workflows', label: 'Workflows' },
    { path: '/app/approvals', label: 'Approvals' },
    { path: '/app/audit', label: 'Audit' },
    { path: '/app/activities', label: 'Activity' },
  ];

  for (const { path, label } of pages) {
    test(`${label} page loads without error`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      // No 500 error page
      const text = await page.textContent('body');
      expect(text).not.toContain('Internal Server Error');
      expect(text).not.toContain('Cannot GET');
      expect(page.url()).not.toContain('/login');
    });
  }
});
