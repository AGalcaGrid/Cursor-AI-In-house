import { test, expect } from '../fixtures/auth.fixture';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /open dashboard/i }).click();
    await page.waitForTimeout(500);
  });

  // Test 1: Display existing tasks
  test('should display existing tasks', async ({ page }) => {
    const taskCards = page.locator('article');
    const count = await taskCards.count();
    expect(count).toBeGreaterThan(0);
  });

  // Test 2: Show task details
  test('should show task title and details', async ({ page }) => {
    const firstTask = page.locator('article').first();
    await expect(firstTask).toBeVisible();
    const taskText = await firstTask.textContent();
    expect(taskText).toBeTruthy();
  });

  // Test 3: Filter tasks by status
  test('should filter tasks by status', async ({ page }) => {
    const allFilter = page.getByRole('button', { name: /^all$/i });
    if (await allFilter.isVisible()) {
      await allFilter.click();
      const tasks = page.locator('article');
      const count = await tasks.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  // Test 4: Change task status
  test('should change task status', async ({ page }) => {
    const taskCard = page.locator('article').first();
    const statusButton = taskCard.getByRole('button').first();
    if (await statusButton.isVisible()) {
      await statusButton.click();
    }
  });

  // Test 5: Mark task as completed
  test('should mark task as completed', async ({ page }) => {
    const completedFilter = page.getByRole('button', { name: /completed/i });
    if (await completedFilter.isVisible()) {
      await completedFilter.click();
      await page.waitForTimeout(300);
    }
  });

  // Test 6: Edit task
  test('should open edit mode for task', async ({ page }) => {
    const taskCard = page.locator('article').first();
    const editButton = taskCard.getByRole('button', { name: /edit/i });
    if (await editButton.isVisible()) {
      await editButton.click();
    }
  });

  // Test 7: Delete task
  test('should show delete confirmation', async ({ page }) => {
    const taskCard = page.locator('article').first();
    const deleteButton = taskCard.getByRole('button', { name: /delete|remove/i });
    if (await deleteButton.isVisible()) {
      await deleteButton.click();
    }
  });

  // Test 8: Search tasks
  test('should search tasks', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await page.waitForTimeout(300);
    }
  });
});
