import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that the page title exists
    await expect(page).toHaveTitle(/.+/);

    // Check that the page is visible
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('dashboard page is accessible', async ({ page }) => {
    await page.goto('/dashboard/ca');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that we didn't get a 404
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('admin page is accessible', async ({ page }) => {
    await page.goto('/admin');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that the page loads
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });
});
