import { Page, expect } from '@playwright/test';

/**
 * Wait for page to be fully loaded
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
}

/**
 * Wait for element to be visible with custom timeout
 */
export async function waitForElement(
  page: Page,
  selector: string,
  timeout = 5000
): Promise<void> {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

/**
 * Take screenshot with timestamp
 */
export async function takeScreenshot(page: Page, name: string): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ path: `screenshots/${name}-${timestamp}.png` });
}

/**
 * Clear local storage
 */
export async function clearStorage(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

/**
 * Set viewport size helper
 */
export async function setViewport(
  page: Page,
  device: 'mobile' | 'tablet' | 'desktop'
): Promise<void> {
  const viewports = {
    mobile: { width: 375, height: 667 },
    tablet: { width: 768, height: 1024 },
    desktop: { width: 1280, height: 800 },
  };
  await page.setViewportSize(viewports[device]);
}

/**
 * Check if element exists
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  const element = page.locator(selector);
  return (await element.count()) > 0;
}

/**
 * Wait for navigation to complete
 */
export async function waitForNavigation(page: Page, url: string): Promise<void> {
  await page.waitForURL(url);
}

/**
 * Fill form field with validation
 */
export async function fillField(
  page: Page,
  selector: string,
  value: string
): Promise<void> {
  const field = page.locator(selector);
  await field.fill(value);
  await expect(field).toHaveValue(value);
}

/**
 * Click and wait for response
 */
export async function clickAndWait(
  page: Page,
  selector: string,
  waitTime = 500
): Promise<void> {
  await page.locator(selector).click();
  await page.waitForTimeout(waitTime);
}

/**
 * Check accessibility of element
 */
export async function checkAccessibility(page: Page, selector: string): Promise<{
  hasAriaLabel: boolean;
  hasRole: boolean;
  isKeyboardAccessible: boolean;
}> {
  const element = page.locator(selector);
  const ariaLabel = await element.getAttribute('aria-label');
  const role = await element.getAttribute('role');
  const tabIndex = await element.getAttribute('tabindex');
  
  return {
    hasAriaLabel: !!ariaLabel,
    hasRole: !!role,
    isKeyboardAccessible: tabIndex !== '-1',
  };
}

/**
 * Simulate network conditions
 */
export async function simulateSlowNetwork(page: Page): Promise<void> {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput: (500 * 1024) / 8,
    uploadThroughput: (500 * 1024) / 8,
    latency: 400,
  });
}

/**
 * Get all console errors
 */
export function setupConsoleErrorCapture(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}
