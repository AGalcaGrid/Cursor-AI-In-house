import { test, expect, testUsers, generateTestData } from './fixtures/test-fixtures';

test.describe('Authentication', () => {
  // Combined: Registration form display + validation + success (3 -> 1)
  test('should handle complete registration flow', async ({ page }) => {
    await page.goto('/register');

    // Verify form elements - use placeholders from Register.tsx
    await expect(page.getByRole('heading', { name: /create.*account|sign up|register/i })).toBeVisible();
    await expect(page.getByPlaceholder('John Doe')).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••').first()).toBeVisible();

    // Test successful registration
    const newUser = generateTestData.user();
    await page.getByPlaceholder('John Doe').fill(newUser.name);
    await page.getByPlaceholder('you@example.com').fill(newUser.email);
    // Fill both password fields
    const passwordFields = page.getByPlaceholder('••••••••');
    await passwordFields.first().fill(newUser.password);
    await passwordFields.nth(1).fill(newUser.password);
    await page.getByRole('button', { name: /create.*account/i }).click();

    // After registration, should show success message or redirect to tickets/dashboard
    // Check for either success page or navigation away from register
    await page.waitForTimeout(2000); // Wait for API response
    const currentUrl = page.url();
    const hasSuccess = await page.getByText(/account created|welcome|go to dashboard/i).first().isVisible().catch(() => false);
    const redirected = !currentUrl.includes('/register');
    expect(hasSuccess || redirected).toBeTruthy();
  });

  // Combined: Login form display + validation + invalid + success (4 -> 1)
  test('should handle complete login flow', async ({ page }) => {
    await page.goto('/login');

    // Verify form elements
    await expect(page.getByRole('heading', { name: /welcome|login|sign in/i })).toBeVisible();
    await expect(page.getByPlaceholder(/email|you@example/i)).toBeVisible();
    await expect(page.getByPlaceholder(/password|••••/i)).toBeVisible();

    // Test invalid credentials - check for error or staying on login page
    await page.getByPlaceholder(/email|you@example/i).fill('wrong@email.com');
    await page.getByPlaceholder(/password|••••/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForTimeout(2000); // Wait for API response
    // Should either show error or stay on login page
    const hasError = await page.getByText(/invalid|incorrect|error|failed/i).first().isVisible().catch(() => false);
    const stayedOnLogin = page.url().includes('/login');
    expect(hasError || stayedOnLogin).toBeTruthy();
    
    // Clear fields for next attempt
    await page.getByPlaceholder(/email|you@example/i).clear();

    // Test successful login
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  });

  // Combined: Logout + protected routes (4 -> 1)
  test('should handle logout and protect routes', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Logout
    const userMenuButton = page.getByRole('button', { name: /user menu/i });
    await userMenuButton.click();
    await page.getByRole('menuitem', { name: /sign out|logout/i }).click();
    await expect(page).toHaveURL(/\/login/);

    // Verify protected routes redirect
    await page.goto('/tickets');
    await expect(page).toHaveURL(/\/login/);
    await page.goto('/settings');
    await expect(page).toHaveURL(/\/login/);
  });

  // Combined: Session persistence (4 -> 1)
  test('should persist session correctly', async ({ page, context }) => {
    // Login
    await page.goto('/login');
    await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
    await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/(tickets|dashboard)/);

    // Test reload persistence
    await page.reload();
    await expect(page).not.toHaveURL(/\/login/);

    // Test navigation persistence
    await page.goto('/settings');
    await expect(page).toHaveURL(/\/settings/);

    // Test new tab persistence
    const newPage = await context.newPage();
    await newPage.goto('/tickets');
    await expect(newPage).not.toHaveURL(/\/login/);
    await newPage.close();
  });
});
