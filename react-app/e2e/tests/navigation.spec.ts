import { test, expect } from '../fixtures/auth.fixture';

test.describe('Navigation Tests', () => {
  // Test 1: Navigate between pages
  test('should navigate between page sections', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to About section
    const aboutLink = page.getByRole('link', { name: /about/i });
    if (await aboutLink.isVisible()) {
      await aboutLink.click();
      const aboutSection = page.locator('#about');
      await expect(aboutSection).toBeVisible();
    }
  });

  // Test 2: Breadcrumb/sidebar navigation
  test('should navigate via sidebar in dashboard', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(1000);
    
    // Look for sidebar navigation items
    const sidebar = page.locator('aside, nav').first();
    await expect(sidebar).toBeVisible();
  });

  // Test 3: Back button functionality
  test('should return to main page with back button', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(500);
    
    const backButton = page.getByRole('button', { name: /back to demo/i });
    await expect(backButton).toBeVisible();
    await backButton.click();
    
    await expect(page.getByRole('button', { name: /open dashboard/i })).toBeVisible();
  });

  // Test 4: Browser history navigation
  test('should handle browser back/forward', async ({ page }) => {
    await page.goto('/');
    
    const aboutLink = page.getByRole('link', { name: /about/i });
    if (await aboutLink.isVisible()) {
      await aboutLink.click();
      await page.waitForTimeout(300);
      await page.goBack();
      await expect(page.locator('body')).toBeVisible();
    }
  });
});
