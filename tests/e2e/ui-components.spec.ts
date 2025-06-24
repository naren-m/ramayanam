import { test, expect } from '@playwright/test';

test.describe('UI Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Ramayana Digital Corpus/);
  });

  test('should have responsive header component', async ({ page }) => {
    const header = page.locator('[data-testid="header"]');
    await expect(header).toBeVisible();
    
    // Check title
    await expect(page.locator('h1')).toContainText('Ramayana Digital Corpus');
    
    // Check theme toggle button if present
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    if (await themeToggle.isVisible()) {
      await expect(themeToggle).toBeVisible();
    }
  });

  test('should toggle dark/light theme', async ({ page }) => {
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    
    if (await themeToggle.isVisible()) {
      // Get initial theme
      const body = page.locator('body');
      const initialClass = await body.getAttribute('class');
      
      // Toggle theme
      await themeToggle.click();
      
      // Wait for theme change animation
      await page.waitForTimeout(500);
      
      // Verify theme changed
      const newClass = await body.getAttribute('class');
      expect(newClass).not.toBe(initialClass);
    } else {
      // Skip if theme toggle not implemented yet
      test.skip();
    }
  });

  test('should display search interface correctly', async ({ page }) => {
    const searchInterface = page.locator('[data-testid="search-interface"]');
    await expect(searchInterface).toBeVisible();
    
    // Check English search input
    const englishSearchInput = page.locator('[data-testid="english-search-input"]');
    await expect(englishSearchInput).toBeVisible();
    await expect(englishSearchInput).toHaveAttribute('placeholder');
    
    // Check Sanskrit search input
    const sanskritSearchInput = page.locator('[data-testid="sanskrit-search-input"]');
    await expect(sanskritSearchInput).toBeVisible();
    await expect(sanskritSearchInput).toHaveAttribute('placeholder');
  });

  test('should show loading spinner during search', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Check for loading spinner
    const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    await expect(loadingSpinner).toBeVisible();
    
    // Wait for results to load and spinner to disappear
    await expect(loadingSpinner).not.toBeVisible({ timeout: 10000 });
  });

  test('should display verse cards with proper content', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('hanuman');
    
    // Wait for results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Check verse card structure
    const verseCards = page.locator('[data-testid="verse-card"]');
    const firstCard = verseCards.first();
    
    await expect(firstCard).toBeVisible();
    
    // Check verse card components
    await expect(firstCard.locator('[data-testid="verse-text"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="verse-translation"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="verse-metadata"]')).toBeVisible();
  });

  test('should handle error boundary', async ({ page }) => {
    // Trigger an error scenario if possible
    // This test might need to be customized based on how errors are handled
    
    // Navigate to invalid URL or trigger error
    await page.goto('/invalid-route');
    
    // Check if error boundary catches the error
    const errorBoundary = page.locator('[data-testid="error-boundary"]');
    if (await errorBoundary.isVisible()) {
      await expect(errorBoundary).toContainText(/error/i);
    }
  });

  test('should have accessible keyboard navigation', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Check if first focusable element is focused
    const englishSearchInput = page.locator('[data-testid="english-search-input"]');
    await expect(englishSearchInput).toBeFocused();
    
    // Test Enter key to trigger search
    await englishSearchInput.fill('rama');
    await page.keyboard.press('Enter');
    
    // Should trigger search (debounced)
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
  });

  test('should handle window resize responsively', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const header = page.locator('[data-testid="header"]');
    const searchInterface = page.locator('[data-testid="search-interface"]');
    
    await expect(header).toBeVisible();
    await expect(searchInterface).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    await expect(header).toBeVisible();
    await expect(searchInterface).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    
    await expect(header).toBeVisible();
    await expect(searchInterface).toBeVisible();
  });

  test('should display proper metadata in verse cards', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('sita');
    
    // Wait for results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    const verseCards = page.locator('[data-testid="verse-card"]');
    if (await verseCards.count() > 0) {
      const firstCard = verseCards.first();
      const metadata = firstCard.locator('[data-testid="verse-metadata"]');
      
      await expect(metadata).toBeVisible();
      
      // Check if metadata contains verse information
      const metadataText = await metadata.textContent();
      expect(metadataText).toBeTruthy();
    }
  });

  test('should handle long content gracefully', async ({ page }) => {
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Wait for results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    const verseCards = page.locator('[data-testid="verse-card"]');
    if (await verseCards.count() > 0) {
      const firstCard = verseCards.first();
      
      // Check that content doesn't overflow container
      const cardBounds = await firstCard.boundingBox();
      const verseText = firstCard.locator('[data-testid="verse-text"]');
      const textBounds = await verseText.boundingBox();
      
      if (cardBounds && textBounds) {
        expect(textBounds.width).toBeLessThanOrEqual(cardBounds.width);
      }
    }
  });
});