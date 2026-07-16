import { test, expect } from '../fixtures/auth.fixture';

const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 800 },
};

test.describe('Responsive Design Tests', () => {
  // Test 1: Mobile viewport layout
  test('should display mobile layout correctly', async ({ page }) => {
    await page.setViewportSize(viewports.mobile);
    await page.goto('/');
    
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalScroll).toBe(false);
  });

  // Test 2: Mobile navigation
  test('should show mobile menu on small screens', async ({ page }) => {
    await page.setViewportSize(viewports.mobile);
    await page.goto('/');
    
    // Look for mobile menu button (hamburger icon) in sidebar or header
    const menuButton = page.locator('button[aria-label*="menu" i], aside button, header button').first();
    await expect(menuButton).toBeVisible();
  });

  // Test 3: Tablet viewport layout
  test('should display tablet layout correctly', async ({ page }) => {
    await page.setViewportSize(viewports.tablet);
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(1000);
    
    // On tablet, main content should be visible
    const mainContent = page.locator('main, [class*="main"]').first();
    await expect(mainContent).toBeVisible();
  });

  // Test 4: Desktop viewport layout
  test('should display desktop layout correctly', async ({ page }) => {
    await page.setViewportSize(viewports.desktop);
    await page.goto('/');
    
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    
    const navItems = nav.locator('a, button').filter({ hasText: /home|products|dashboard/i });
    const count = await navItems.count();
    expect(count).toBeGreaterThan(0);
  });

  // Test 5: Desktop sidebar expanded
  test('should show expanded sidebar on desktop', async ({ page }) => {
    await page.setViewportSize(viewports.desktop);
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(1000);
    
    // On desktop (1280px > 1024px lg breakpoint), sidebar should be visible
    const sidebar = page.locator('aside').first();
    await expect(sidebar).toBeVisible();
  });

  // Test 6: Orientation change - portrait to landscape
  test('should adapt layout on orientation change', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // Portrait
    await page.goto('/');
    
    await page.setViewportSize({ width: 667, height: 375 }); // Landscape
    await page.waitForTimeout(300);
    
    await expect(page.locator('body')).toBeVisible();
    
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalScroll).toBe(false);
  });

  // Test 7: Tablet orientation change
  test('should handle tablet orientation change', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // Portrait
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(1000);
    
    await page.setViewportSize({ width: 1024, height: 768 }); // Landscape (equals lg breakpoint)
    await page.waitForTimeout(500);
    
    // Content should still be visible after orientation change
    await expect(page.locator('body')).toBeVisible();
  });

  // Test 8: Rapid orientation changes
  test('should not break on rapid orientation changes', async ({ page }) => {
    await page.goto('/');
    
    for (let i = 0; i < 3; i++) {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(100);
      await page.setViewportSize({ width: 667, height: 375 });
      await page.waitForTimeout(100);
    }
    
    await expect(page.locator('body')).toBeVisible();
  });
});
