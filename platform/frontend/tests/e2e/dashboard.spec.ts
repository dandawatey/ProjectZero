import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page);
  });

  test('dashboard renders after login', async ({ page }) => {
    await expect(page).toHaveURL(/\/app/);
    // Dashboard title or stat cards should be visible
    const content = page.locator('h1, [class*="dashboard"], [class*="Dashboard"]');
    await expect(content.first()).toBeVisible({ timeout: 8000 });
  });

  test('stat cards are visible', async ({ page }) => {
    // Look for numeric stat cards (Active, Completed, Failed, etc.)
    const cards = page.locator('[class*="rounded"][class*="border"], [class*="card"]');
    await expect(cards.first()).toBeVisible({ timeout: 8000 });
  });

  test('projects section renders', async ({ page }) => {
    // Projects or "No projects yet" should be visible
    const projectsSection = page.locator('text=Projects, text=No projects, [class*="project"]').first();
    await expect(projectsSection).toBeVisible({ timeout: 8000 });
  });

  test('navigation sidebar is visible', async ({ page }) => {
    await expect(page.locator('nav, aside').first()).toBeVisible();
  });

  test('new product button exists', async ({ page }) => {
    const btn = page.locator('a:has-text("New Product"), button:has-text("New Product")').first();
    await expect(btn).toBeVisible({ timeout: 5000 });
  });
});
