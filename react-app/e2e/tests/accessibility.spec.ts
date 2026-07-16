import { test, expect } from '../fixtures/auth.fixture';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  // Test 1: Keyboard navigation
  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  // Test 2: Screen reader compatibility (ARIA labels)
  test('should have proper ARIA labels and roles', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav, [role="navigation"]');
    await expect(nav.first()).toBeVisible();
    
    const buttons = await page.locator('button').all();
    for (const button of buttons.slice(0, 5)) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      expect(text?.trim() || ariaLabel).toBeTruthy();
    }
  });

  // Test 3: Alt text for images
  test('should have alt text for all images', async ({ page }) => {
    await page.goto('/');
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });

  // Test 4: Color contrast (using axe-core)
  test('should have proper color contrast', async ({ page }) => {
    await page.goto('/');
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .analyze();
    expect(accessibilityScanResults.violations.length).toBeLessThanOrEqual(5);
  });

  // Test 5: Heading hierarchy
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    const h1 = page.locator('h1');
    await expect(h1.first()).toBeVisible();
    const headings = await page.locator('h1, h2, h3').all();
    expect(headings.length).toBeGreaterThan(0);
  });

  // Test 6: Focus indicators
  test('should have visible focus indicators', async ({ page }) => {
    await page.goto('/');
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    const styles = await focusedElement.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return { outline: computed.outline, boxShadow: computed.boxShadow };
    });
    expect(styles.outline !== 'none' || styles.boxShadow !== 'none').toBe(true);
  });
});
