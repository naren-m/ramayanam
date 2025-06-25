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

  test('should show and handle load more button when more results are available', async ({ page }) => {
    // Perform a search that would return multiple pages
    const searchInput = page.locator('[data-testid="english-search-input"]');
    await searchInput.fill('rama');
    await searchInput.press('Enter');
    
    // Wait for search results to load
    await page.waitForTimeout(2000);
    
    // Check if load more button is visible (only if there are more results)
    const loadMoreButton = page.locator('[data-testid="load-more-button"]');
    
    // Count initial results
    const initialResults = page.locator('[data-testid="verse-card"]');
    const initialCount = await initialResults.count();
    
    // If load more button is visible, test its functionality
    if (await loadMoreButton.isVisible()) {
      // Click load more button
      await loadMoreButton.click();
      
      // Wait for new results to load
      await page.waitForTimeout(2000);
      
      // Check that more results were loaded
      const newResults = page.locator('[data-testid="verse-card"]');
      const newCount = await newResults.count();
      
      expect(newCount).toBeGreaterThan(initialCount);
      
      // Check that button shows loading state when clicked
      if (await loadMoreButton.isVisible()) {
        await loadMoreButton.click();
        await expect(loadMoreButton).toContainText('Loading...');
      }
    }
  });
});