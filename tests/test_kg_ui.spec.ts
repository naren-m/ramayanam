import { test, expect, Page } from '@playwright/test';

test.describe('Knowledge Graph UI Tests', () => {
  const API_BASE = 'http://localhost:8080';
  const UI_BASE = 'http://localhost:3000'; // Adjust if UI runs on different port

  test.beforeEach(async ({ page }) => {
    // Navigate to the Knowledge Graph tab
    await page.goto(UI_BASE);
    await page.click('[data-testid="knowledge-tab-button"]');
    await page.waitForSelector('[data-testid="knowledge-graph-search"]');
  });

  test('should display knowledge graph statistics', async ({ page }) => {
    // Wait for statistics to load
    await page.waitForSelector('text=Knowledge Graph Explorer');
    
    // Check that statistics cards are present
    await expect(page.locator('text=Total Entities')).toBeVisible();
    await expect(page.locator('text=Text Mentions')).toBeVisible();
    await expect(page.locator('text=People')).toBeVisible();
    await expect(page.locator('text=Places')).toBeVisible();
    
    // Verify numbers are displayed
    const totalEntities = await page.locator('text=Total Entities').locator('..').locator('.text-2xl').textContent();
    expect(parseInt(totalEntities || '0')).toBeGreaterThan(0);
  });

  test('should switch between search and browse modes', async ({ page }) => {
    // Test search mode button
    await page.click('button:has-text("Search")');
    await expect(page.locator('text=Search Knowledge Graph')).toBeVisible();
    
    // Test browse mode button
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.grid.gap-4');
    
    // Should show entity cards
    const entityCards = await page.locator('.bg-white.rounded-lg.p-6').count();
    expect(entityCards).toBeGreaterThan(0);
  });

  test('should perform entity search', async ({ page }) => {
    // Make sure we're in search mode
    await page.click('button:has-text("Search")');
    
    // Type in search box
    const searchInput = page.locator('input[placeholder*="Search entities"]');
    await searchInput.fill('rama');
    
    // Press Enter or click search
    await page.keyboard.press('Enter');
    
    // Wait for results
    await page.waitForSelector('text=Search Results');
    
    // Should show results
    const resultCount = await page.locator('text=Search Results').textContent();
    expect(resultCount).toContain('(');
    
    // Should have entity cards
    const entityCards = await page.locator('.bg-white.rounded-lg.p-6').count();
    expect(entityCards).toBeGreaterThan(0);
  });

  test('should filter entities by type', async ({ page }) => {
    // Go to browse mode
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.grid.gap-4');
    
    // Select Person filter
    await page.selectOption('select', 'Person');
    await page.waitForTimeout(1000); // Wait for filter to apply
    
    // All visible entity cards should be Person type
    const personBadges = await page.locator('text=Person').count();
    const entityCards = await page.locator('.bg-white.rounded-lg.p-6').count();
    
    expect(personBadges).toBe(entityCards);
  });

  test('should display entity details in modal', async ({ page }) => {
    // Go to browse mode to see entities
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    
    // Click on first "Details" button
    await page.click('button:has-text("Details")');
    
    // Should open modal
    await expect(page.locator('text=Entity Details')).toBeVisible();
    
    // Should show entity information
    await expect(page.locator('text=Name:')).toBeVisible();
    await expect(page.locator('text=Type:')).toBeVisible();
    await expect(page.locator('text=URI:')).toBeVisible();
    
    // Close modal
    await page.click('button[aria-label="Close"] svg, .text-gray-400 svg');
    await expect(page.locator('text=Entity Details')).not.toBeVisible();
  });

  test('should display Sanskrit text correctly', async ({ page }) => {
    // Go to browse mode
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    
    // Look for Sanskrit text (should have sanskrit-text class)
    const sanskritElements = await page.locator('.sanskrit-text').count();
    expect(sanskritElements).toBeGreaterThan(0);
  });

  test('should show entity type badges with correct colors', async ({ page }) => {
    // Go to browse mode
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    
    // Check for different entity type badges
    const personBadges = page.locator('.text-blue-600:has-text("Person")');
    const placeBadges = page.locator('.text-green-600:has-text("Place")');
    const conceptBadges = page.locator('.text-pink-600:has-text("Concept")');
    
    // At least one type should be present
    const totalBadges = await personBadges.count() + await placeBadges.count() + await conceptBadges.count();
    expect(totalBadges).toBeGreaterThan(0);
  });

  test('should handle empty search results', async ({ page }) => {
    // Make sure we're in search mode
    await page.click('button:has-text("Search")');
    
    // Search for something that doesn't exist
    const searchInput = page.locator('input[placeholder*="Search entities"]');
    await searchInput.fill('nonexistententity123');
    await page.keyboard.press('Enter');
    
    // Should show no results message
    await expect(page.locator('text=No entities found')).toBeVisible();
  });

  test('should clear search input', async ({ page }) => {
    // Make sure we're in search mode
    await page.click('button:has-text("Search")');
    
    // Type in search box
    const searchInput = page.locator('input[placeholder*="Search entities"]');
    await searchInput.fill('test search');
    
    // Click clear button (X icon)
    await page.click('button svg');
    
    // Input should be empty
    await expect(searchInput).toHaveValue('');
  });

  test('should show loading states', async ({ page }) => {
    // Intercept API calls to simulate slow response
    await page.route('**/api/kg/**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
      await route.continue();
    });
    
    // Go to browse mode (triggers API call)
    await page.click('button:has-text("Browse")');
    
    // Should show some kind of loading state
    // This could be a spinner or disabled state
    await page.waitForTimeout(500);
    
    // Wait for content to load
    await page.waitForSelector('.bg-white.rounded-lg.p-6', { timeout: 5000 });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls to return error
    await page.route('**/api/kg/entities', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: 'Internal server error' })
      });
    });
    
    // Go to browse mode (triggers API call)
    await page.click('button:has-text("Browse")');
    
    // Should show error message
    await expect(page.locator('text=Failed to connect to knowledge graph API')).toBeVisible();
  });

  test('should display entity occurrence counts', async ({ page }) => {
    // Go to browse mode
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    
    // Look for occurrence counts
    const mentionsText = await page.locator('text=Mentions:').count();
    expect(mentionsText).toBeGreaterThan(0);
  });

  test('should show epithet information', async ({ page }) => {
    // Go to browse mode and open details modal
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    await page.click('button:has-text("Details")');
    
    // Check if epithets are shown (might not be present for all entities)
    const epithetsSection = page.locator('text=Epithets:');
    if (await epithetsSection.count() > 0) {
      await expect(epithetsSection).toBeVisible();
    }
  });

  test('should maintain responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Go to browse mode
    await page.click('button:has-text("Browse")');
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
    
    // Should still be usable on mobile
    const entityCards = await page.locator('.bg-white.rounded-lg.p-6').count();
    expect(entityCards).toBeGreaterThan(0);
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Should adapt to larger screen
    await page.waitForSelector('.bg-white.rounded-lg.p-6');
  });

  test('should navigate between tabs correctly', async ({ page }) => {
    // Start on Knowledge Graph tab
    await expect(page.locator('[data-testid="knowledge-tab-button"]')).toHaveClass(/bg-orange-500/);
    
    // Switch to Search tab
    await page.click('[data-testid="search-tab-button"]');
    await expect(page.locator('[data-testid="search-interface"]')).toBeVisible();
    
    // Switch back to Knowledge Graph tab
    await page.click('[data-testid="knowledge-tab-button"]');
    await expect(page.locator('[data-testid="knowledge-graph-search"]')).toBeVisible();
  });
});

test.describe('Knowledge Graph API Integration', () => {
  test('should validate API responses', async ({ request }) => {
    // Test statistics endpoint
    const statsResponse = await request.get('http://localhost:8080/api/kg/statistics');
    expect(statsResponse.ok()).toBeTruthy();
    
    const statsData = await statsResponse.json();
    expect(statsData.success).toBe(true);
    expect(statsData.statistics).toBeDefined();
    expect(typeof statsData.statistics.total_entities).toBe('number');
    expect(statsData.statistics.total_entities).toBeGreaterThan(0);
    
    // Test search endpoint
    const searchResponse = await request.get('http://localhost:8080/api/kg/search?q=rama');
    expect(searchResponse.ok()).toBeTruthy();
    
    const searchData = await searchResponse.json();
    expect(searchData.success).toBe(true);
    expect(Array.isArray(searchData.entities)).toBe(true);
    expect(typeof searchData.count).toBe('number');
    
    // Test entities endpoint
    const entitiesResponse = await request.get('http://localhost:8080/api/kg/entities');
    expect(entitiesResponse.ok()).toBeTruthy();
    
    const entitiesData = await entitiesResponse.json();
    expect(entitiesData.success).toBe(true);
    expect(Array.isArray(entitiesData.entities)).toBe(true);
    expect(entitiesData.entities.length).toBeGreaterThan(0);
    
    // Validate entity structure
    const entity = entitiesData.entities[0];
    expect(entity.kg_id).toBeDefined();
    expect(entity.entity_type).toBeDefined();
    expect(entity.labels).toBeDefined();
    expect(entity.labels.en).toBeDefined();
    expect(entity.kg_id).toContain('ramayanam.hanuma.com');
  });
});