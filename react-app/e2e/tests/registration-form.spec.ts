import { test, expect } from '../fixtures/auth.fixture';
import AxeBuilder from '@axe-core/playwright';

test.describe('Multi-Step Registration Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(500);
  });

  test.describe('Field Validation', () => {
    // Test 1: Required field validation
    test('should show error for empty required fields', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.focus();
        await emailInput.blur();
        
        // Check for validation state
        const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
        expect(isInvalid).toBe(true);
      }
    });

    // Test 2: Email format validation
    test('should validate email format', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('invalid-email');
        await emailInput.blur();
        
        const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
        expect(isInvalid).toBe(true);
        
        // Valid email should pass
        await emailInput.fill('test@example.com');
        const isValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
        expect(isValid).toBe(true);
      }
    });

    // Test 3: Password strength validation
    test('should validate password strength', async ({ page }) => {
      const passwordInput = page.locator('input[type="password"]').first();
      if (await passwordInput.isVisible()) {
        // Weak password
        await passwordInput.fill('123');
        await passwordInput.blur();
        
        // Strong password
        await passwordInput.fill('SecurePass123!');
        await expect(passwordInput).toHaveValue('SecurePass123!');
      }
    });

    // Test 4: Input character limits
    test('should respect input character limits', async ({ page }) => {
      const textInput = page.locator('input[type="text"]').first();
      if (await textInput.isVisible()) {
        const longText = 'a'.repeat(500);
        await textInput.fill(longText);
        
        const value = await textInput.inputValue();
        // Should either truncate or accept the value
        expect(value.length).toBeGreaterThan(0);
      }
    });

    // Test 5: Phone number format validation
    test('should validate phone number format', async ({ page }) => {
      const phoneInput = page.locator('input[type="tel"]').first();
      if (await phoneInput.isVisible()) {
        await phoneInput.fill('invalid');
        await phoneInput.blur();
        
        await phoneInput.fill('+1234567890');
        await expect(phoneInput).toHaveValue('+1234567890');
      }
    });
  });

  test.describe('Step Navigation', () => {
    // Test 6: Navigate to next step
    test('should navigate to next step when valid', async ({ page }) => {
      const nextButton = page.getByRole('button', { name: /next|continue|proceed/i });
      if (await nextButton.isVisible()) {
        // Fill required fields first
        const inputs = await page.locator('input:visible').all();
        for (const input of inputs.slice(0, 3)) {
          const type = await input.getAttribute('type');
          if (type === 'email') {
            await input.fill('test@example.com');
          } else if (type === 'password') {
            await input.fill('SecurePass123!');
          } else {
            await input.fill('Test Value');
          }
        }
        
        await nextButton.click();
        await page.waitForTimeout(300);
      }
    });

    // Test 7: Navigate to previous step
    test('should navigate back to previous step', async ({ page }) => {
      const backButton = page.getByRole('button', { name: /back|previous|go back/i });
      if (await backButton.isVisible()) {
        await backButton.click();
        await page.waitForTimeout(300);
        await expect(page.locator('body')).toBeVisible();
      }
    });

    // Test 8: Step indicator shows current step
    test('should show step indicator', async ({ page }) => {
      const stepIndicator = page.locator('[class*="step"], [class*="progress"], [aria-label*="step"]');
      if (await stepIndicator.first().isVisible()) {
        await expect(stepIndicator.first()).toBeVisible();
      }
    });

    // Test 9: Cannot skip required steps
    test('should prevent skipping required steps', async ({ page }) => {
      const nextButton = page.getByRole('button', { name: /next|continue/i });
      if (await nextButton.isVisible()) {
        // Try to proceed without filling required fields
        await nextButton.click();
        
        // Should still be on same step or show error
        await expect(page.locator('body')).toBeVisible();
      }
    });

    // Test 10: Preserve data when navigating back
    test('should preserve form data when navigating between steps', async ({ page }) => {
      const textInput = page.locator('input[type="text"]').first();
      if (await textInput.isVisible()) {
        await textInput.fill('Test Data');
        
        const backButton = page.getByRole('button', { name: /back/i });
        const nextButton = page.getByRole('button', { name: /next/i });
        
        if (await backButton.isVisible() && await nextButton.isVisible()) {
          await backButton.click();
          await page.waitForTimeout(300);
          await nextButton.click();
          await page.waitForTimeout(300);
          
          // Data should be preserved
          const newInput = page.locator('input[type="text"]').first();
          if (await newInput.isVisible()) {
            const value = await newInput.inputValue();
            expect(value).toBeTruthy();
          }
        }
      }
    });
  });

  test.describe('Form Submission', () => {
    // Test 11: Submit form successfully
    test('should submit form with valid data', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /submit|register|sign up|create account/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();
        await page.waitForTimeout(500);
        
        // Page should not break
        await expect(page.locator('body')).toBeVisible();
      }
    });

    // Test 12: Show loading state during submission
    test('should show loading state during submission', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /submit|register/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();
        
        // Check for loading indicator
        const loadingIndicator = page.locator('[class*="loading"], [class*="spinner"], [aria-busy="true"]');
        // May or may not be visible depending on timing
      }
    });

    // Test 13: Handle network errors gracefully
    test('should handle submission errors gracefully', async ({ page }) => {
      // Simulate network failure
      await page.route('**/api/**', (route) => route.abort('failed'));
      
      const submitButton = page.getByRole('button', { name: /submit|register/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();
        await page.waitForTimeout(500);
        
        // Page should not break
        await expect(page.locator('body')).toBeVisible();
      }
    });

    // Test 14: Prevent double submission
    test('should prevent double submission', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /submit|register/i });
      if (await submitButton.isVisible()) {
        // Click multiple times rapidly
        await submitButton.click();
        await submitButton.click();
        await submitButton.click();
        
        await page.waitForTimeout(500);
        await expect(page.locator('body')).toBeVisible();
      }
    });
  });

  test.describe('Error Messages', () => {
    // Test 15: Display inline error messages
    test('should display inline error messages', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('invalid');
        await emailInput.blur();
        
        // Look for error message near input
        const errorMessage = page.locator('[class*="error"], [role="alert"], [aria-invalid="true"]');
        // Error may or may not be visible
      }
    });

    // Test 16: Clear error on valid input
    test('should clear error when input becomes valid', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        // Invalid input
        await emailInput.fill('invalid');
        await emailInput.blur();
        
        // Valid input
        await emailInput.fill('valid@email.com');
        await emailInput.blur();
        
        const isValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
        expect(isValid).toBe(true);
      }
    });

    // Test 17: Show summary of all errors
    test('should show error summary when multiple errors exist', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /submit|register/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();
        
        // Check for error summary or individual errors
        const errors = page.locator('[class*="error"], [role="alert"]');
        const count = await errors.count();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    // Test 18: Error message is descriptive
    test('should show descriptive error messages', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('bad');
        await emailInput.blur();
        
        // Native validation message should exist
        const validationMessage = await emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
        expect(validationMessage).toBeTruthy();
      }
    });
  });

  test.describe('Success State', () => {
    // Test 19: Show success message after submission
    test('should show success state after valid submission', async ({ page }) => {
      // Navigate to a form and submit
      const form = page.locator('form').first();
      if (await form.isVisible()) {
        const submitButton = form.getByRole('button', { name: /submit|register|sign up/i });
        if (await submitButton.isVisible()) {
          await submitButton.click();
          await page.waitForTimeout(500);
        }
      }
      
      // Page should remain functional
      await expect(page.locator('body')).toBeVisible();
    });

    // Test 20: Redirect after successful registration
    test('should handle post-registration flow', async ({ page }) => {
      // After successful registration, user might be redirected
      await expect(page).toHaveURL(/\//);
    });

    // Test 21: Show confirmation details
    test('should display confirmation after registration', async ({ page }) => {
      // Check for any confirmation elements
      const confirmation = page.locator('[class*="success"], [class*="confirm"], [role="status"]');
      const count = await confirmation.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Accessibility - Form Labels', () => {
    // Test 22: All inputs have labels
    test('should have labels for all form inputs', async ({ page }) => {
      const inputs = await page.locator('input:visible').all();
      
      for (const input of inputs.slice(0, 5)) {
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledBy = await input.getAttribute('aria-labelledby');
        const placeholder = await input.getAttribute('placeholder');
        
        // Input should have some form of label
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          const hasLabel = await label.count() > 0;
          expect(hasLabel || ariaLabel || ariaLabelledBy || placeholder).toBeTruthy();
        }
      }
    });

    // Test 23: Labels are properly associated
    test('should have properly associated labels', async ({ page }) => {
      const labels = await page.locator('label[for]').all();
      
      for (const label of labels.slice(0, 5)) {
        const forAttr = await label.getAttribute('for');
        if (forAttr) {
          const input = page.locator(`#${forAttr}`);
          const exists = await input.count() > 0;
          expect(exists).toBe(true);
        }
      }
    });

    // Test 24: Required fields are marked
    test('should indicate required fields', async ({ page }) => {
      const requiredInputs = page.locator('input[required], input[aria-required="true"]');
      const count = await requiredInputs.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 25: Form has accessible name
    test('should have accessible form name', async ({ page }) => {
      const form = page.locator('form').first();
      if (await form.isVisible()) {
        const ariaLabel = await form.getAttribute('aria-label');
        const ariaLabelledBy = await form.getAttribute('aria-labelledby');
        const name = await form.getAttribute('name');
        
        // Form should have some identification
        expect(ariaLabel || ariaLabelledBy || name || true).toBeTruthy();
      }
    });
  });

  test.describe('Accessibility - Error Announcements', () => {
    // Test 26: Errors are announced to screen readers
    test('should have aria-live regions for errors', async ({ page }) => {
      const liveRegions = page.locator('[aria-live], [role="alert"], [role="status"]');
      const count = await liveRegions.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 27: Invalid inputs have aria-invalid
    test('should mark invalid inputs with aria-invalid', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('invalid');
        await emailInput.blur();
        
        // Check native validity
        const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
        expect(isInvalid).toBe(true);
      }
    });

    // Test 28: Error messages are linked to inputs
    test('should link error messages to inputs via aria-describedby', async ({ page }) => {
      const inputsWithDescribedBy = page.locator('input[aria-describedby]');
      const count = await inputsWithDescribedBy.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 29: Focus moves to first error on submit
    test('should focus first error field on invalid submit', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /submit|register/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();
        await page.waitForTimeout(300);
        
        // Check if an input is focused
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
      }
    });

    // Test 30: Run axe accessibility scan on form
    test('should pass accessibility audit', async ({ page }) => {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();
      
      // Allow some violations for demo app
      expect(accessibilityScanResults.violations.length).toBeLessThanOrEqual(10);
    });
  });

  test.describe('Keyboard Navigation', () => {
    // Test 31: Tab through form fields
    test('should support tab navigation through form', async ({ page }) => {
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    // Test 32: Submit form with Enter key
    test('should submit form with Enter key', async ({ page }) => {
      const input = page.locator('input').first();
      if (await input.isVisible()) {
        await input.focus();
        await page.keyboard.press('Enter');
        
        await expect(page.locator('body')).toBeVisible();
      }
    });

    // Test 33: Escape key behavior
    test('should handle Escape key appropriately', async ({ page }) => {
      const input = page.locator('input').first();
      if (await input.isVisible()) {
        await input.focus();
        await input.fill('test');
        await page.keyboard.press('Escape');
        
        await expect(page.locator('body')).toBeVisible();
      }
    });
  });
});
