import { test as base, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Test user credentials - matching demo accounts from Login.tsx
export const testUsers = {
  customer: {
    email: 'customer@example.com',
    password: 'Customer123!',
    name: 'Test Customer',
  },
  agent: {
    email: 'agent@support.com',
    password: 'Agent123!',
    name: 'Test Agent',
  },
  admin: {
    email: 'admin@support.com',
    password: 'Admin123!',
    name: 'Test Admin',
  },
};

// Extended test fixture with accessibility helper
export const test = base.extend<{
  checkA11y: (disabledRules?: string[]) => Promise<void>;
}>({
  checkA11y: async ({ page }, use) => {
    const checkA11y = async (disabledRules: string[] = []) => {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .disableRules(disabledRules)
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    };
    await use(checkA11y);
  },
});

export { expect };

// Helper to generate unique test data
export const generateTestData = {
  ticket: () => ({
    subject: `Test Ticket ${Date.now()}`,
    description: `This is a test ticket created at ${new Date().toISOString()}`,
    priority: 'medium' as const,
    category: 'technical' as const,
  }),
  user: () => ({
    name: `Test User ${Date.now()}`,
    email: `testuser${Date.now()}@test.com`,
    password: 'Test123!@#',
  }),
};

// Viewport sizes for responsive testing
export const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 },
  largeDesktop: { width: 1920, height: 1080 },
};
