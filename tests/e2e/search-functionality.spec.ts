import { test, expect } from '@playwright/test';

test.describe('Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Universal Sacred Text Platform/);
  });

  test('should load the homepage successfully', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Sacred Text Research');
    await expect(page.locator('[data-testid="english-search-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="sanskrit-search-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-tab-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="chat-tab-button"]')).toBeVisible();
  });

  test('should handle empty search query', async ({ page }) => {
    // Clear any existing input
    const searchInput = page.locator('[data-testid="english-search-input"]');
    await searchInput.clear();
    
    // Since search is debounced and automatic, empty input should clear results
    // Check if search results are not visible or show welcome message
    const searchResults = page.locator('[data-testid="search-results"]');
    await expect(searchResults).not.toBeVisible();
  });
});