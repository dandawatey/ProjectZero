import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Agents Page', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page);
  });

  test('agents page loads', async ({ page }) => {
    await page.goto('/app/agents');
    await page.waitForLoadState('networkidle');
    expect(page.url()).not.toContain('/login');
  });

  test('registry tab is visible', async ({ page }) => {
    await page.goto('/app/agents');
    await page.waitForTimeout(2000);
    const registryTab = page.locator('button:has-text("Registry"), [role="tab"]:has-text("Registry")').first();
    await expect(registryTab).toBeVisible({ timeout: 8000 });
  });

  test('execution history tab is visible', async ({ page }) => {
    await page.goto('/app/agents');
    const historyTab = page.locator('button:has-text("Execution"), [role="tab"]:has-text("Execution")').first();
    await expect(historyTab).toBeVisible({ timeout: 8000 });
  });
});
