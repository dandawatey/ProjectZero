import { Page } from '@playwright/test';

export const TEST_USER = {
  email: 'e2e-test@example.com',
  password: 'TestPass123!',
};

export async function loginAs(page: Page, email = TEST_USER.email, password = TEST_USER.password) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  // Find email input — try common selectors
  const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
  const passwordInput = page.locator('input[type="password"]').first();
  const submitBtn = page.locator('button[type="submit"], button:has-text("Sign in"), button:has-text("Login"), button:has-text("Log in")').first();

  await emailInput.fill(email);
  await passwordInput.fill(password);
  await submitBtn.click();
  await page.waitForURL('**/app**', { timeout: 10000 }).catch(() => {});
}

export async function saveAuthState(page: Page) {
  await loginAs(page);
  await page.context().storageState({ path: 'tests/e2e/.auth/user.json' });
}
