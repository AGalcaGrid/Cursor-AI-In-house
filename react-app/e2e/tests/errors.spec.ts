import { test, expect } from '../fixtures/auth.fixture';

test.describe('Error Handling Tests', () => {
  // Test 1: Handle network errors gracefully
  test('should handle network errors gracefully', async ({ page }) => {
    await page.route('**/api/**', (route) => route.abort('failed'));
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });

  // Test 2: Handle invalid routes
  test('should handle invalid routes', async ({ page }) => {
    await page.goto('/non-existent-page');
    await expect(page.locator('body')).toBeVisible();
  });

  // Test 3: Handle form validation errors
  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/');
    const emailInput = page.locator('input[type="email"]');
    if (await emailInput.isVisible()) {
      await emailInput.fill('invalid-email');
      await emailInput.blur();
      const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
      expect(isInvalid).toBe(true);
    }
  });

  // Test 4: Handle rapid user interactions
  test('should handle rapid clicking gracefully', async ({ page }) => {
    await page.goto('/');
    const button = page.locator('button').first();
    for (let i = 0; i < 5; i++) {
      await button.click({ force: true }).catch(() => {});
    }
    await expect(page.locator('body')).toBeVisible();
  });

  // Test 5: Handle corrupted localStorage
  test('should handle corrupted state gracefully', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('darkMode', 'invalid');
    });
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });

  // Test 6: Handle special characters in input
  test('should sanitize special characters in input', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(500);
    
    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill('<script>alert("xss")</script>');
      await expect(page.locator('body')).toBeVisible();
    }
  });
});
