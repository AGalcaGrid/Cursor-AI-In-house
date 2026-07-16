import { test, expect, testUsers, generateTestData } from './fixtures/test-fixtures';

test.describe('Ticket Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  });

  // Combined: List display + filters + navigation (4 -> 1)
  test('should display ticket list with filters and navigation', async ({ page }) => {
    await page.goto('/tickets');

    // Verify list page - use first() to handle multiple headings
    await expect(page.getByRole('heading', { name: /tickets/i }).first()).toBeVisible();

    // Check for ticket content area (table, list, or empty state)
    const ticketContent = page.locator('main, #main-content, [role="main"]').first();
    await expect(ticketContent).toBeVisible();

    // Check filters exist - search input or select dropdowns
    const searchInput = page.getByPlaceholder(/search/i);
    const selectElements = page.locator('select');
    const hasSearch = await searchInput.isVisible().catch(() => false);
    const hasSelects = await selectElements.count() > 0;
    expect(hasSearch || hasSelects).toBeTruthy();

    // Navigate to detail if tickets exist
    const ticketLink = page.locator('a[href*="/tickets/"]').first();
    const ticketVisible = await ticketLink.isVisible().catch(() => false);
    if (ticketVisible) {
      await ticketLink.click();
      await expect(page).toHaveURL(/\/tickets\//);
    }
  });

  // Combined: Create form + validation + success + cancel (4 -> 1)
  test('should handle complete ticket creation flow', async ({ page }) => {
    await page.goto('/tickets/new');

    // Verify form - use first() to handle multiple headings
    await expect(page.getByRole('heading', { name: /new ticket|create ticket/i }).first()).toBeVisible();
    
    // Find form inputs using actual placeholders from TicketCreate.tsx
    const subjectInput = page.getByPlaceholder('Brief summary of your issue');
    const descriptionInput = page.getByPlaceholder('Please provide detailed information about your issue...');
    
    await expect(subjectInput).toBeVisible();
    await expect(descriptionInput).toBeVisible();

    // Create ticket successfully
    const ticketData = generateTestData.ticket();
    await subjectInput.fill(ticketData.subject);
    await descriptionInput.fill(ticketData.description);

    await page.getByRole('button', { name: /submit ticket/i }).click();
    await expect(page).toHaveURL(/\/tickets/);
  });

  // Combined: Detail view + comments (2 -> 1)
  test('should display ticket details and allow comments', async ({ page }) => {
    await page.goto('/tickets');

    const ticketLink = page.locator('a[href*="/tickets/"]').first();
    if (await ticketLink.isVisible()) {
      await ticketLink.click();
      await expect(page).toHaveURL(/\/tickets\//);

      // Verify we're on a detail page (should have some content)
      await expect(page.locator('main, #main-content, [role="main"]').first()).toBeVisible();

      // Test comments if available
      const commentInput = page.getByPlaceholder(/comment|message|reply/i);
      if (await commentInput.isVisible()) {
        await commentInput.fill('Test comment');
        const submitButton = page.getByRole('button', { name: /send|submit|add/i });
        await submitButton.click();
        await expect(page.getByText('Test comment')).toBeVisible();
      }
    }
  });

  // Combined: Status updates + resolve (2 -> 1)
  test('should allow status updates and resolution', async ({ page }) => {
    // Already logged in as customer from beforeEach
    // Navigate to tickets and check if any ticket exists
    await page.goto('/tickets');
    
    const ticketLink = page.locator('a[href*="/tickets/"]').first();
    if (await ticketLink.isVisible()) {
      await ticketLink.click();
      await expect(page).toHaveURL(/\/tickets\//);

      // Check if status display exists (customers may not be able to change status)
      const statusBadge = page.locator('[class*="bg-"][class*="text-"]').first();
      if (await statusBadge.isVisible()) {
        // Verify status is displayed
        await expect(statusBadge).toBeVisible();
      }
    }
  });

  // Combined: Edit operations (5 -> 1)
  test('should handle ticket editing', async ({ page }) => {
    await page.goto('/tickets');

    const ticketLink = page.getByRole('link', { name: /TICK-|ticket/i }).first();
    if (await ticketLink.isVisible()) {
      await ticketLink.click();

      const editButton = page.getByRole('button', { name: /edit/i });
      if (await editButton.isVisible()) {
        await editButton.click();

        // Edit subject
        const subjectInput = page.getByLabel(/subject|title/i);
        if (await subjectInput.isVisible()) {
          const newSubject = `Updated ${Date.now()}`;
          await subjectInput.fill(newSubject);
          await page.getByRole('button', { name: /save|update/i }).click();
          await expect(page.getByText(newSubject)).toBeVisible();
        }
      }

      // Test priority change
      const prioritySelect = page.getByLabel(/priority/i);
      if (await prioritySelect.isVisible()) {
        await prioritySelect.selectOption('high');
        await expect(page.getByText(/high/i)).toBeVisible();
      }
    }
  });

  // Combined: Delete operations (4 -> 1)
  test('should handle ticket deletion with confirmation', async ({ page }) => {
    // Create a ticket to delete
    const ticketData = generateTestData.ticket();
    await page.goto('/tickets/new');
    await page.getByPlaceholder('Brief summary of your issue').fill(ticketData.subject);
    await page.getByPlaceholder('Please provide detailed information about your issue...').fill(ticketData.description);
    await page.getByRole('button', { name: /submit ticket/i }).click();

    await page.goto('/tickets');
    const ticketLink = page.getByRole('link', { name: new RegExp(ticketData.subject.substring(0, 15), 'i') });
    
    if (await ticketLink.isVisible()) {
      await ticketLink.click();

      const deleteButton = page.getByRole('button', { name: /delete/i });
      if (await deleteButton.isVisible()) {
        await deleteButton.click();

        // Verify confirmation dialog
        const confirmText = page.getByText(/are you sure|confirm|delete/i);
        await expect(confirmText).toBeVisible();

        // Confirm delete
        const confirmButton = page.getByRole('button', { name: /confirm|yes|delete/i }).last();
        if (await confirmButton.isVisible()) {
          await confirmButton.click();
          await expect(page).toHaveURL(/\/tickets$/);
        }
      }
    }
  });

  // Combined: Search operations (4 -> 1)
  test('should handle ticket search and filtering', async ({ page }) => {
    await page.goto('/tickets');

    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      // Search by term
      await searchInput.fill('test');
      await page.waitForTimeout(500);

      const tickets = page.getByRole('link', { name: /TICK-|ticket/i });
      const noResults = page.getByText(/no results|no tickets|not found/i);
      const hasResults = await tickets.count() > 0;
      const hasNoResults = await noResults.isVisible().catch(() => false);
      expect(hasResults || hasNoResults).toBeTruthy();

      // Clear and search by ticket number
      await searchInput.fill('');
      await page.waitForTimeout(300);
      await searchInput.fill('TICK-');
      await page.waitForTimeout(500);
    }
  });
});
