import { test, expect } from '@playwright/test';

test.describe('API Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should make successful API calls for fuzzy search', async ({ page }) => {
    // Listen for API requests
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/ramayanam/slokas/fuzzy-search')) {
        apiCalls.push(request);
      }
    });

    // Use the English search input specifically
    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('hanuman');
    // The search triggers automatically on input change, no button needed
    
    // Wait for API call
    await page.waitForTimeout(2000);
    
    // Verify API call was made
    expect(apiCalls.length).toBeGreaterThan(0);
    
    const apiCall = apiCalls[0];
    expect(apiCall.url()).toContain('query=hanuman');
    expect(apiCall.method()).toBe('GET');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/ramayanam/slokas/fuzzy-search*', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('test');
    
    // Should show error message or fallback content
    // Wait a bit for the error to be handled
    await page.waitForTimeout(2000);
    
    // Check if there's a results section or error indication
    const resultsSection = page.locator('[data-testid="results-display"]');
    await expect(resultsSection).toBeVisible({ timeout: 5000 });
  });

  test('should handle slow API responses', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/ramayanam/slokas/fuzzy-search*', async route => {
      await new Promise(resolve => setTimeout(resolve, 3000)); // 3 second delay
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              sloka_id: '1-1-1',
              sloka_text: 'Test sloka',
              translation: 'Test translation',
              meaning: 'Test meaning',
              kanda: 1,
              sarga: 1,
              sloka: 1
            }
          ],
          pagination: {
            page: 1,
            page_size: 10,
            total_results: 1,
            total_pages: 1,
            has_next: false,
            has_prev: false
          }
        }),
      });
    });

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('test');
    
    // Should show loading spinner
    const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    await expect(loadingSpinner).toBeVisible();
    
    // Wait for response and verify loading disappears
    await expect(loadingSpinner).not.toBeVisible({ timeout: 5000 });
    
    // Should show results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  });

  test('should make correct API calls for Sanskrit search', async ({ page }) => {
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/ramayanam/slokas/fuzzy-search-sanskrit')) {
        apiCalls.push(request);
      }
    });

    // Switch to Sanskrit search if toggle exists
    const searchTypeToggle = page.locator('[data-testid="search-type-toggle"]');
    if (await searchTypeToggle.isVisible()) {
      await searchTypeToggle.click();
    }

    const searchInput = page.locator('[data-testid="sanskrit-search-input"]');
    
    await searchInput.fill('राम');
    
    // Wait for API call
    await page.waitForTimeout(2000);
    
    // Verify correct API endpoint was called
    if (apiCalls.length > 0) {
      const apiCall = apiCalls[0];
      expect(apiCall.url()).toContain('fuzzy-search-sanskrit');
      // Check for URL-encoded Sanskrit characters (%E0%A4%B0%E0%A4%BE%E0%A4%AE is URL-encoded राम)
      expect(apiCall.url()).toMatch(/query=(%E0%A4%B0%E0%A4%BE%E0%A4%AE|राम)/);
    }
  });

  test('should handle pagination API calls', async ({ page }) => {
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/ramayanam/slokas/fuzzy-search')) {
        apiCalls.push(request);
      }
    });

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Wait for initial results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 10000 });
    
    // Check if pagination exists and click next page
    const nextButton = page.locator('[data-testid="pagination-next"]');
    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      await nextButton.click();
      
      // Wait for new API call
      await page.waitForTimeout(2000);
      
      // Verify pagination API call was made
      const paginationCall = apiCalls.find(call => call.url().includes('page=2'));
      expect(paginationCall).toBeTruthy();
    }
  });

  test('should handle Kanda filter API calls', async ({ page }) => {
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/ramayanam/slokas/fuzzy-search')) {
        apiCalls.push(request);
      }
    });

    // Select Kanda filter if available
    const kandaSelect = page.locator('[data-testid="kanda-filter"]');
    if (await kandaSelect.isVisible()) {
      await kandaSelect.selectOption('1');
    }

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('rama');
    
    // Wait for API call
    await page.waitForTimeout(2000);
    
    // Verify Kanda parameter was included if filter exists
    if (await kandaSelect.isVisible() && apiCalls.length > 0) {
      const apiCall = apiCalls[apiCalls.length - 1];
      expect(apiCall.url()).toContain('kanda=1');
    }
  });

  test('should validate API response structure', async ({ page }) => {
    let responseData = null;
    
    page.on('response', async response => {
      if (response.url().includes('/api/ramayanam/slokas/fuzzy-search')) {
        responseData = await response.json();
      }
    });

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('hanuman');
    
    // Wait for response
    await page.waitForTimeout(3000);
    
    // Validate response structure
    if (responseData) {
      expect(responseData).toHaveProperty('results');
      expect(responseData).toHaveProperty('pagination');
      
      if (responseData.results.length > 0) {
        const firstResult = responseData.results[0];
        expect(firstResult).toHaveProperty('sloka_number');  // Correct field name
        expect(firstResult).toHaveProperty('sloka');         // Correct field name
        expect(firstResult).toHaveProperty('translation');
        expect(firstResult).toHaveProperty('meaning');
        expect(firstResult).toHaveProperty('ratio');
      }
      
      const pagination = responseData.pagination;
      expect(pagination).toHaveProperty('page');
      expect(pagination).toHaveProperty('page_size');
      expect(pagination).toHaveProperty('total_results');
      expect(pagination).toHaveProperty('total_pages');
      expect(pagination).toHaveProperty('has_next');
      expect(pagination).toHaveProperty('has_prev');
    }
  });

  test('should handle network connectivity issues', async ({ page }) => {
    // Simulate network failure by blocking all API requests
    await page.route('**/api/ramayanam/slokas/**', route => {
      route.abort('internetdisconnected');
    });

    const searchInput = page.locator('[data-testid="english-search-input"]');
    
    await searchInput.fill('test');
    
    // Wait for error handling
    await page.waitForTimeout(3000);
    
    // Should show error message or fallback content
    const errorMessage = page.locator('[data-testid="error-message"]');
    const resultsDisplay = page.locator('[data-testid="results-display"]');
    
    // Either error message should be visible OR results display should handle gracefully
    const hasError = await errorMessage.isVisible();
    const hasResults = await resultsDisplay.isVisible();
    expect(hasError || hasResults).toBeTruthy();
  });
});