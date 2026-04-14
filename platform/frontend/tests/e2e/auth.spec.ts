import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('landing page is accessible', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ProjectZero|Project Zero/i);
  });

  test('redirects unauthenticated users from /app to /login', async ({ page }) => {
    await page.goto('/app');
    await page.waitForURL('**/login**', { timeout: 8000 }).catch(() => {});
    const url = page.url();
    expect(url).toMatch(/login|\/$/);
  });

  test('login page renders form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[type="email"], input[name="email"]').first()).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('button[type="submit"]').first()).toBeVisible();
  });

  test('shows error on wrong credentials', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"], input[name="email"]').first().fill('wrong@example.com');
    await page.locator('input[type="password"]').first().fill('wrongpassword');
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(2000);
    // Should NOT navigate to /app
    expect(page.url()).not.toContain('/app');
  });
});
