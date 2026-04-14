import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Factory Floor', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page);
  });

  test('factory floor page loads without 401', async ({ page }) => {
    // Navigate to factory floor
    await page.goto('/app/floor');
    await page.waitForLoadState('networkidle');

    // Should NOT show "Unauthorized" or redirect to login
    const pageText = await page.textContent('body');
    expect(pageText).not.toContain('Unauthorized');
    expect(page.url()).not.toContain('/login');
  });

  test('factory floor has content or empty state', async ({ page }) => {
    await page.goto('/app/floor');
    await page.waitForTimeout(3000);
    // Page should render something (not blank)
    const body = await page.textContent('body');
    expect(body?.length).toBeGreaterThan(10);
  });
});
