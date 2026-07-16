import { test as base, expect, Page } from '@playwright/test';

// Test user data
export const testUsers = {
  validUser: {
    email: 'testuser@example.com',
    password: 'SecurePass123!',
    name: 'Test User',
  },
  invalidUser: {
    email: 'invalid@example.com',
    password: 'wrongpassword',
    name: 'Invalid User',
  },
};

// Test task data
export const testTasks = {
  basic: {
    title: 'Complete project documentation',
    description: 'Write comprehensive documentation for the new feature',
    priority: 'medium' as const,
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  },
  highPriority: {
    title: 'Fix critical bug',
    description: 'Resolve the authentication issue in production',
    priority: 'high' as const,
    dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  },
  lowPriority: {
    title: 'Update dependencies',
    description: 'Update npm packages to latest versions',
    priority: 'low' as const,
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  },
};

// Page Object Model for Dashboard
export class DashboardPage {
  constructor(private page: Page) {}

  // Navigation
  async goto() {
    await this.page.goto('/');
    await this.page.getByRole('button', { name: /open dashboard/i }).click();
    await this.page.waitForSelector('[data-testid="dashboard"]', { timeout: 5000 }).catch(() => {
      // Dashboard might not have testid, wait for sidebar instead
    });
  }

  // Sidebar interactions
  async toggleSidebar() {
    await this.page.getByRole('button', { name: /toggle sidebar/i }).click();
  }

  async navigateTo(item: string) {
    await this.page.getByRole('navigation').getByText(item, { exact: false }).click();
  }

  // Task interactions
  async getTaskCards() {
    return this.page.locator('article').filter({ has: this.page.locator('[class*="priority"]') });
  }

  async getTaskByTitle(title: string) {
    return this.page.locator('article').filter({ hasText: title });
  }

  async changeTaskStatus(taskTitle: string, newStatus: string) {
    const task = await this.getTaskByTitle(taskTitle);
    await task.getByRole('button', { name: /status/i }).click();
    await this.page.getByRole('menuitem', { name: newStatus }).click();
  }

  async deleteTask(taskTitle: string) {
    const task = await this.getTaskByTitle(taskTitle);
    await task.getByRole('button', { name: /delete/i }).click();
    await this.page.getByRole('button', { name: /confirm/i }).click();
  }

  // Filter interactions
  async filterByStatus(status: string) {
    await this.page.getByRole('button', { name: status }).click();
  }

  // Dark mode
  async toggleDarkMode() {
    await this.page.getByRole('button', { name: /dark mode|light mode|toggle theme/i }).click();
  }

  async isDarkMode() {
    return this.page.evaluate(() => document.documentElement.classList.contains('dark'));
  }

  // Statistics
  async getStatistics() {
    const stats = await this.page.locator('[aria-label*="statistic"], [class*="statistic"]').all();
    return stats;
  }
}

// Page Object Model for Analytics Dashboard
export class AnalyticsPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/');
    await this.page.getByRole('button', { name: /open analytics/i }).click();
  }

  async waitForChartsToLoad() {
    // Wait for skeleton loaders to disappear
    await this.page.waitForFunction(() => {
      const skeletons = document.querySelectorAll('.animate-pulse');
      return skeletons.length === 0;
    }, { timeout: 10000 });
  }

  async getKPICards() {
    return this.page.locator('article').filter({ has: this.page.locator('[class*="change"]') });
  }

  async filterByCategory(category: string) {
    await this.page.locator('select').first().selectOption(category);
  }

  async filterByStatus(status: string) {
    await this.page.locator('select').nth(1).selectOption(status);
  }

  async selectDateRange(range: string) {
    await this.page.getByRole('button', { name: /last \d+ days|today|yesterday/i }).click();
    await this.page.getByRole('button', { name: range }).click();
  }

  async exportData() {
    await this.page.getByRole('button', { name: /export/i }).click();
  }

  async refreshData() {
    await this.page.getByRole('button', { name: /refresh/i }).click();
  }

  async searchTable(query: string) {
    await this.page.getByPlaceholder(/search/i).fill(query);
  }

  async sortTableBy(column: string) {
    await this.page.getByRole('columnheader', { name: column }).click();
  }

  async getTableRowCount() {
    return this.page.locator('tbody tr').count();
  }

  async toggleDarkMode() {
    await this.page.getByRole('button', { name: /dark mode|light mode|toggle theme/i }).click();
  }
}

// Page Object Model for Settings
export class SettingsPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/');
    await this.page.getByRole('button', { name: /open dashboard/i }).click();
    await this.page.getByText('Settings').click();
  }

  async switchTab(tabName: string) {
    await this.page.getByRole('tab', { name: tabName }).click();
  }

  async updateProfile(data: { firstName?: string; lastName?: string; email?: string }) {
    if (data.firstName) {
      await this.page.getByLabel(/first name/i).fill(data.firstName);
    }
    if (data.lastName) {
      await this.page.getByLabel(/last name/i).fill(data.lastName);
    }
    if (data.email) {
      await this.page.getByLabel(/email/i).fill(data.email);
    }
  }

  async toggleNotification(setting: string) {
    await this.page.getByRole('switch', { name: new RegExp(setting, 'i') }).click();
  }

  async saveChanges() {
    await this.page.getByRole('button', { name: /save/i }).click();
  }

  async cancelChanges() {
    await this.page.getByRole('button', { name: /cancel/i }).click();
  }

  async hasUnsavedChanges() {
    return this.page.getByText(/unsaved changes/i).isVisible();
  }
}

// Extended test fixture with page objects
type TestFixtures = {
  dashboardPage: DashboardPage;
  analyticsPage: AnalyticsPage;
  settingsPage: SettingsPage;
};

export const test = base.extend<TestFixtures>({
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  analyticsPage: async ({ page }, use) => {
    await use(new AnalyticsPage(page));
  },
  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
});

export { expect };
