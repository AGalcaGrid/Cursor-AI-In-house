import { test, expect, testUsers, viewports } from './fixtures/test-fixtures';

test.describe('Responsive Design Tests', () => {
  // Combined: Mobile viewport tests (5 -> 1)
  test('should display correctly on mobile viewport', async ({ page }) => {
    await page.setViewportSize(viewports.mobile);

    // Check form fits mobile
    await page.goto('/login');
    const form = page.locator('form');
    const formBox = await form.boundingBox();
    expect(formBox?.width).toBeLessThanOrEqual(viewports.mobile.width);

    // Login and check mobile layout
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Hamburger menu should be visible - use exact match
    const hamburgerButton = page.getByRole('button', { name: 'Open sidebar' });
    await expect(hamburgerButton).toBeVisible();

    // Sidebar should be hidden by default
    const sidebar = page.locator('aside, [role="navigation"]').first();
    const sidebarBox = await sidebar.boundingBox();
    if (sidebarBox) {
      expect(sidebarBox.x).toBeLessThan(0);
    }

    // Open sidebar via hamburger
    await hamburgerButton.click();
    await expect(sidebar).toBeVisible();
  });

  // Combined: Tablet viewport tests (2 -> 1)
  test('should display correctly on tablet viewport', async ({ page }) => {
    await page.setViewportSize(viewports.tablet);

    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Sidebar should be visible but condensed
    const sidebar = page.locator('aside, [role="navigation"]').first();
    await expect(sidebar).toBeVisible();
    const sidebarBox = await sidebar.boundingBox();
    expect(sidebarBox?.width).toBeLessThan(200);

    // Check grid layout on settings
    await page.goto('/settings');
    const gridContainer = page.locator('.grid');
    if (await gridContainer.first().isVisible()) {
      const gridBox = await gridContainer.first().boundingBox();
      expect(gridBox?.width).toBeGreaterThan(400);
    }
  });

  // Combined: Desktop viewport tests (3 -> 1)
  test('should display correctly on desktop viewport', async ({ page }) => {
    await page.setViewportSize(viewports.desktop);

    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Full sidebar should be visible
    const sidebar = page.locator('aside, [role="navigation"]').first();
    await expect(sidebar).toBeVisible();
    const sidebarBox = await sidebar.boundingBox();
    expect(sidebarBox?.width).toBeGreaterThanOrEqual(200);

    // Hamburger should be hidden on desktop
    const hamburgerButton = page.getByRole('button', { name: 'Open sidebar' });
    await expect(hamburgerButton).not.toBeVisible();
  });

  // Combined: Large desktop + max-width (2 -> 1)
  test('should maintain constraints on large desktop', async ({ page }) => {
    await page.setViewportSize(viewports.largeDesktop);

    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    await page.goto('/tickets');

    // Content should have max-width constraint or be visible
    const mainContent = page.locator('#main-content, main, [role="main"]').first();
    await expect(mainContent).toBeVisible();
    const contentBox = await mainContent.boundingBox();
    // On large desktop, content should not span full width (should have some constraint)
    if (contentBox) {
      expect(contentBox.width).toBeLessThan(viewports.largeDesktop.width);
    }
  });

  // Combined: Orientation + touch targets (3 -> 1)
  test('should handle orientation changes and touch targets', async ({ page }) => {
    // Start in portrait
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/login');

    // Check touch target sizes
    const submitButton = page.getByRole('button', { name: /login|sign in/i });
    const buttonBox = await submitButton.boundingBox();
    expect(buttonBox?.height).toBeGreaterThanOrEqual(40);
    expect(buttonBox?.width).toBeGreaterThanOrEqual(44);

    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Hamburger visible in portrait - use exact match
    const hamburgerButton = page.getByRole('button', { name: 'Open sidebar' });
    await expect(hamburgerButton).toBeVisible();

    // Switch to landscape
    await page.setViewportSize({ width: 667, height: 375 });
    await page.waitForTimeout(300);
  });
});
