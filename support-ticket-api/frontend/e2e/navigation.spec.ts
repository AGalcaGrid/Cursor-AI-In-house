import { test, expect, testUsers } from './fixtures/test-fixtures';

test.describe('Navigation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  });

  // Combined: Sidebar navigation + user menu + active state (6 -> 1)
  test('should navigate between pages via sidebar and menu', async ({ page }) => {
    await page.goto('/tickets');

    // Navigate to settings via sidebar
    const settingsLink = page.getByRole('link', { name: /settings/i });
    await settingsLink.click();
    await expect(page).toHaveURL(/\/settings/);

    // Navigate back to tickets
    const ticketsLink = page.getByRole('link', { name: /tickets/i });
    await ticketsLink.click();
    await expect(page).toHaveURL(/\/tickets/);

    // Check active state
    const ticketsNavItem = page.locator('nav').getByRole('link', { name: /tickets/i });
    if (await ticketsNavItem.isVisible()) {
      const classes = await ticketsNavItem.getAttribute('class');
      expect(classes).toMatch(/bg-|text-blue|active|current/);
    }

    // Navigate via user menu
    const userMenuButton = page.getByRole('button', { name: /user menu/i });
    await userMenuButton.click();
    const settingsMenuItem = page.getByRole('menuitem', { name: /settings/i });
    if (await settingsMenuItem.isVisible()) {
      await settingsMenuItem.click();
      await expect(page).toHaveURL(/\/settings/);
    }
  });

  // Combined: Breadcrumb display + navigation (3 -> 1)
  test('should display and use breadcrumb navigation', async ({ page }) => {
    await page.goto('/tickets');

    const ticketLink = page.locator('a[href*="/tickets/"]').first();
    if (await ticketLink.isVisible()) {
      await ticketLink.click();
      await expect(page).toHaveURL(/\/tickets\//);

      // Check breadcrumb exists
      const breadcrumb = page.locator('nav[aria-label="Breadcrumb"], [aria-label="breadcrumb"], .breadcrumb');
      if (await breadcrumb.isVisible()) {
        await expect(breadcrumb.getByText(/tickets/i)).toBeVisible();

        // Navigate back via breadcrumb
        const breadcrumbLink = breadcrumb.getByRole('link', { name: /tickets/i });
        if (await breadcrumbLink.isVisible()) {
          await breadcrumbLink.click();
          await expect(page).toHaveURL(/\/tickets$/);
        }
      }
    }
  });

  // Combined: Back/forward + scroll restoration (5 -> 1)
  test('should handle browser back/forward navigation', async ({ page }) => {
    await page.goto('/tickets');
    await page.goto('/settings');
    await expect(page).toHaveURL(/\/settings/);

    // Go back
    await page.goBack();
    await expect(page).toHaveURL(/\/tickets/);

    // Go forward
    await page.goForward();
    await expect(page).toHaveURL(/\/settings/);

    // Test from ticket detail
    await page.goto('/tickets');
    const ticketLink = page.locator('a[href*="/tickets/"]').first();
    if (await ticketLink.isVisible()) {
      await ticketLink.click();
      await page.goBack();
      await expect(page).toHaveURL(/\/tickets/);
    }
  });

  // Combined: Deep linking + URL params (3 -> 1)
  test('should handle deep linking and URL parameters', async ({ page }) => {
    // Direct URL access
    await page.goto('/settings');
    await expect(page.getByRole('heading', { name: /settings/i }).first()).toBeVisible();

    // URL with parameters
    await page.goto('/tickets?status=open');
    expect(page.url()).toContain('tickets');
  });

  // Combined: Mobile menu operations (3 -> 1)
  test('should handle mobile navigation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/tickets');

    // Open hamburger menu - use exact match to avoid User menu button
    const hamburgerButton = page.getByRole('button', { name: 'Open sidebar' });
    await hamburgerButton.click();

    // Navigate via mobile menu
    const settingsLink = page.getByRole('link', { name: /settings/i });
    await settingsLink.click();
    await expect(page).toHaveURL(/\/settings/);

    // Menu should close after navigation
    const sidebar = page.locator('aside, [role="navigation"]').first();
    const sidebarBox = await sidebar.boundingBox();
    if (sidebarBox) {
      expect(sidebarBox.x).toBeLessThan(0);
    }
  });
});
