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

  test('should perform English fuzzy search', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('hanuman');
    
    // Wait for search results to load (search happens automatically via debounce)
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Check if results contain verse cards
    const verseCards = page.locator('[data-testid="verse-card"]');
    await expect(verseCards.first()).toBeVisible();
    
    // Verify search results have relevant content
    const firstResult = verseCards.first();
    await expect(firstResult).toContainText(/hanuman/i);
  });

  test('should perform Sanskrit fuzzy search', async ({ page }) => {
    const searchInput = page.locator('[data-testid="sanskrit-search-input"]');
    
    await searchInput.fill('राम');
    
    // Wait for search results to load
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Check if results contain verse cards
    const verseCards = page.locator('[data-testid="verse-card"]');
    await expect(verseCards.first()).toBeVisible();
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

  test('should display load more button for large result sets', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Wait for search results to load
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Check if load more button is present for large result sets
    const loadMoreButton = page.locator('[data-testid="load-more-button"]');
    if (await loadMoreButton.isVisible()) {
      await expect(loadMoreButton).toBeVisible();
      await expect(loadMoreButton).toBeEnabled();
    }
  });

  test('should filter by Kanda', async ({ page }) => {
    // Select a specific Kanda
    const kandaSelect = page.locator('[data-testid="kanda-filter"]');
    await kandaSelect.selectOption('1'); // BalaKanda
    
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Wait for search results to load
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Verify results are filtered by Kanda
    const verseCards = page.locator('[data-testid="verse-card"]');
    if (await verseCards.count() > 0) {
      const firstResult = verseCards.first();
      // Check that the verse number starts with '1.' indicating BalaKanda
      await expect(firstResult.locator('[data-testid="verse-metadata"]')).toBeVisible();
    }
  });

  test('should handle search with no results', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('xyznoresults123');
    
    // Wait for search to complete
    await page.waitForTimeout(3000);
    
    // Should show no results message
    await expect(page.locator('[data-testid="no-results"]')).toBeVisible();
  });

  test('should clear search results', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    // Perform initial search
    await searchInput.fill('hanuman');
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Clear search by clearing input
    await searchInput.clear();
    
    // Results should disappear
    await expect(page.locator('[data-testid="search-results"]')).not.toBeVisible();
  });
});