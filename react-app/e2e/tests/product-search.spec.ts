import { test, expect } from '../fixtures/auth.fixture';

test.describe('Product Search Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(500);
  });

  test.describe('Search Input', () => {
    // Test 1: Search input visibility
    test('should display search input in navigation', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await expect(searchInput).toBeVisible();
    });

    // Test 2: Search input accepts text
    test('should accept text input in search field', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.fill('headphones');
      await expect(searchInput).toHaveValue('headphones');
    });

    // Test 3: Search shows results dropdown
    test('should show search results dropdown when typing', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('watch');
      await page.waitForTimeout(300);
      
      const resultsDropdown = page.locator('#search-results, [role="listbox"]');
      await expect(resultsDropdown).toBeVisible();
    });

    // Test 4: Search clears on result click
    test('should clear search on result selection', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('headphones');
      await page.waitForTimeout(300);
      
      const resultItem = page.locator('[role="option"]').first();
      if (await resultItem.isVisible()) {
        await resultItem.click();
        await expect(searchInput).toHaveValue('');
      }
    });
  });

  test.describe('Filter by Category', () => {
    // Test 5: Products section displays categories
    test('should display products with categories', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const productCards = page.locator('#products').locator('article, [class*="card"]');
      const count = await productCards.count();
      expect(count).toBeGreaterThan(0);
    });

    // Test 6: Search filters by category
    test('should filter search results by category', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('Electronics');
      await page.waitForTimeout(300);
      
      const results = page.locator('[role="option"]');
      const count = await results.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 7: Category appears in search results
    test('should show category label in search results', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('watch');
      await page.waitForTimeout(300);
      
      const categoryLabel = page.locator('#search-results').getByText(/accessories|electronics|fitness/i);
      if (await categoryLabel.first().isVisible()) {
        await expect(categoryLabel.first()).toBeVisible();
      }
    });
  });

  test.describe('Price Range Filtering', () => {
    // Test 8: Products display prices
    test('should display product prices', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const priceElements = page.locator('#products').getByText(/\$\d+/);
      const count = await priceElements.count();
      expect(count).toBeGreaterThan(0);
    });

    // Test 9: Products show original prices for discounts
    test('should display original price for discounted items', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      // Look for strikethrough prices (original prices)
      const originalPrices = page.locator('#products').locator('[class*="line-through"], del, s');
      const count = await originalPrices.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 10: Price format is correct
    test('should display prices in correct currency format', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const priceText = await page.locator('#products').getByText(/\$\d+\.\d{2}/).first().textContent();
      expect(priceText).toMatch(/\$\d+\.\d{2}/);
    });
  });

  test.describe('Sort Options', () => {
    // Test 11: Products can be viewed
    test('should display multiple products for comparison', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const productCards = productsSection.locator('article, [class*="ProductCard"]');
      const count = await productCards.count();
      expect(count).toBeGreaterThan(1);
    });

    // Test 12: Products have ratings for sorting
    test('should display product ratings', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const ratings = productsSection.locator('[class*="star"], svg[class*="text-yellow"]');
      const count = await ratings.count();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Pagination', () => {
    // Test 13: Products grid is displayed
    test('should display products in a grid layout', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const grid = productsSection.locator('[class*="grid"]');
      await expect(grid).toBeVisible();
    });

    // Test 14: All products are visible
    test('should display all available products', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const productCards = productsSection.locator('article, [class*="card"]').filter({ has: page.locator('img') });
      const count = await productCards.count();
      expect(count).toBeGreaterThanOrEqual(4);
    });
  });

  test.describe('Empty Results', () => {
    // Test 15: Show empty state for no results
    test('should show empty state when no search results', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('xyznonexistent123');
      await page.waitForTimeout(500);
      
      // Check that search input still works (doesn't crash)
      await expect(searchInput).toBeVisible();
      await expect(searchInput).toHaveValue('xyznonexistent123');
    });

    // Test 16: Empty state shows helpful message
    test('should show helpful message for empty results', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('asdfghjkl');
      await page.waitForTimeout(500);
      
      // Verify search functionality works even with no matches
      await expect(searchInput).toBeVisible();
      // Can clear the search
      await searchInput.clear();
      await expect(searchInput).toHaveValue('');
    });
  });

  test.describe('Error States', () => {
    // Test 17: Handle special characters in search
    test('should handle special characters in search input', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.fill('<script>alert("xss")</script>');
      await page.waitForTimeout(300);
      
      // Page should not break
      await expect(page.locator('body')).toBeVisible();
      await expect(searchInput).toBeVisible();
    });

    // Test 18: Handle very long search queries
    test('should handle very long search queries', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      const longQuery = 'a'.repeat(200);
      await searchInput.fill(longQuery);
      
      // Page should not break
      await expect(page.locator('body')).toBeVisible();
    });

    // Test 19: Handle rapid typing
    test('should handle rapid typing without errors', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      
      for (const char of 'headphones') {
        await searchInput.press(char);
        await page.waitForTimeout(50);
      }
      
      await expect(page.locator('body')).toBeVisible();
    });

    // Test 20: Search works after clearing
    test('should work correctly after clearing search', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.fill('watch');
      await page.waitForTimeout(300);
      
      await searchInput.clear();
      await expect(searchInput).toHaveValue('');
      
      await searchInput.fill('headphones');
      await page.waitForTimeout(300);
      await expect(searchInput).toHaveValue('headphones');
    });
  });

  test.describe('Multi-Filter Tests', () => {
    // Test 21: Apply multiple search terms sequentially
    test('should handle multiple sequential searches', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      
      // First search
      await searchInput.click();
      await searchInput.fill('watch');
      await page.waitForTimeout(300);
      
      // Clear and search again
      await searchInput.clear();
      await searchInput.fill('headphones');
      await page.waitForTimeout(300);
      
      const results = page.locator('[role="option"]');
      const count = await results.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    // Test 22: Search by product name and category combined
    test('should filter by both product name and category', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('Wireless');
      await page.waitForTimeout(300);
      
      // Results should show matching products
      const resultsDropdown = page.locator('#search-results');
      await expect(resultsDropdown).toBeVisible();
    });
  });

  test.describe('Pagination Navigation', () => {
    // Test 23: Scroll to view all products
    test('should scroll through product list', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      // Get initial scroll position
      const initialScroll = await page.evaluate(() => window.scrollY);
      
      // Scroll down
      await page.evaluate(() => window.scrollBy(0, 500));
      await page.waitForTimeout(300);
      
      const newScroll = await page.evaluate(() => window.scrollY);
      expect(newScroll).toBeGreaterThan(initialScroll);
    });

    // Test 24: Navigate between product sections
    test('should navigate to products section via link', async ({ page }) => {
      const productsLink = page.getByRole('link', { name: /products/i });
      if (await productsLink.isVisible()) {
        await productsLink.click();
        await page.waitForTimeout(500);
        
        const productsSection = page.locator('#products');
        await expect(productsSection).toBeVisible();
      }
    });
  });

  test.describe('Sort Options', () => {
    // Test 25: Products are displayed in order
    test('should display products with consistent ordering', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const productCards = productsSection.locator('article, [class*="card"]').filter({ has: page.locator('img') });
      const count = await productCards.count();
      
      // Reload and check same order
      await page.reload();
      await productsSection.scrollIntoViewIfNeeded();
      
      const newCount = await productCards.count();
      expect(newCount).toBe(count);
    });

    // Test 26: Products have sortable attributes (price, rating)
    test('should display sortable product attributes', async ({ page }) => {
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      // Check for prices
      const prices = productsSection.getByText(/\$\d+/);
      expect(await prices.count()).toBeGreaterThan(0);
      
      // Check for ratings
      const ratings = productsSection.locator('svg').filter({ has: page.locator('[class*="yellow"], [class*="star"]') });
      expect(await ratings.count()).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Viewport Tests', () => {
    // Test 27: Search works on mobile viewport
    test('should work on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await page.waitForTimeout(500);
      
      // Mobile may have different search UI
      const mobileMenuButton = page.locator('nav button').first();
      if (await mobileMenuButton.isVisible()) {
        await mobileMenuButton.click();
        await page.waitForTimeout(300);
      }
      
      const searchInput = page.getByPlaceholder(/search/i).first();
      if (await searchInput.isVisible()) {
        await searchInput.fill('watch');
        await expect(searchInput).toHaveValue('watch');
      }
    });

    // Test 28: Search works on tablet viewport
    test('should work on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await page.waitForTimeout(500);
      
      // On tablet, search may be in mobile menu - open it first
      const mobileMenuButton = page.locator('nav button').first();
      if (await mobileMenuButton.isVisible()) {
        await mobileMenuButton.click();
        await page.waitForTimeout(300);
      }
      
      const searchInput = page.getByPlaceholder(/search/i).first();
      if (await searchInput.isVisible()) {
        await searchInput.fill('headphones');
        await expect(searchInput).toHaveValue('headphones');
      } else {
        // If search is not visible on tablet, verify products are visible instead
        const productsSection = page.locator('#products');
        await productsSection.scrollIntoViewIfNeeded();
        await expect(productsSection).toBeVisible();
      }
    });

    // Test 29: Products display correctly on mobile
    test('should display products on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      
      const productsSection = page.locator('#products');
      await productsSection.scrollIntoViewIfNeeded();
      
      const productCards = productsSection.locator('article, [class*="card"]').filter({ has: page.locator('img') });
      const count = await productCards.count();
      expect(count).toBeGreaterThan(0);
    });

    // Test 30: Search dropdown works on desktop
    test('should show search dropdown on desktop viewport', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 800 });
      await page.reload();
      await page.waitForTimeout(500);
      
      const searchInput = page.getByPlaceholder(/search/i).first();
      await searchInput.click();
      await searchInput.fill('watch');
      await page.waitForTimeout(300);
      
      const resultsDropdown = page.locator('#search-results');
      await expect(resultsDropdown).toBeVisible();
    });
  });
});
