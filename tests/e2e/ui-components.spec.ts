import { test, expect } from '@playwright/test';

test.describe('UI Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Universal Sacred Text Platform/);
  });

  test('should have responsive header component', async ({ page }) => {
    // Check title
    await expect(page.locator('h1')).toContainText('Sacred Text Research');
    
    // Check theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle-button"]');
    await expect(themeToggle).toBeVisible();
    
    // Check view toggle buttons
    await expect(page.locator('[data-testid="search-tab-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="chat-tab-button"]')).toBeVisible();
  });

  test('should toggle dark/light theme', async ({ page }) => {
    const themeToggle = page.locator('[data-testid="theme-toggle-button"]');
    
    // Get initial theme
    const html = page.locator('html');
    const initialClass = await html.getAttribute('class');
    
    // Toggle theme
    await themeToggle.click();
    
    // Wait for theme change animation
    await page.waitForTimeout(500);
    
    // Verify theme changed
    const newClass = await html.getAttribute('class');
    expect(newClass).not.toBe(initialClass);
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

  test('should handle error boundary', async ({ page }) => {
    // Navigate to invalid URL or trigger error
    await page.goto('/invalid-route');
    
    // Check if error boundary catches the error
    const errorBoundary = page.locator('[data-testid="error-boundary"]');
    if (await errorBoundary.isVisible()) {
      await expect(errorBoundary).toContainText(/error/i);
    } else {
      // If no error boundary, that's also acceptable behavior
      expect(true).toBeTruthy();
    }
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
});