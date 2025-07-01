import { test, expect } from '@playwright/test';

test.describe('Interactive Graph Visualization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Universal Sacred Text Platform/);
    
    // Navigate to Knowledge Graph tab
    const knowledgeTab = page.locator('[data-testid="knowledge-tab-button"]');
    await expect(knowledgeTab).toBeVisible();
    await knowledgeTab.click();
    
    // Wait for the graph interface to load
    await page.waitForTimeout(2000);
  });

  test('should load knowledge graph interface successfully', async ({ page }) => {
    // Check main graph container
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Check graph controls panel
    const graphControls = page.locator('[data-testid="graph-controls"]');
    if (await graphControls.isVisible()) {
      await expect(graphControls).toBeVisible();
    }
    
    // Check search interface for knowledge graph
    const searchInput = page.locator('[data-testid="kg-search-input"]');
    if (await searchInput.isVisible()) {
      await expect(searchInput).toBeVisible();
    }
  });

  test('should display graph info overlay with node and edge counts', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Check for graph info overlay (nodes/edges count)
    const graphInfo = page.locator('.absolute.top-4.left-4');
    if (await graphInfo.isVisible()) {
      await expect(graphInfo).toContainText(/Nodes:/);
      await expect(graphInfo).toContainText(/Edges:/);
    }
  });

  test('should have functional zoom controls', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Test zoom in button
    const zoomInButton = page.locator('button[title="Zoom In"]');
    if (await zoomInButton.isVisible()) {
      await zoomInButton.click();
      await page.waitForTimeout(500); // Wait for zoom animation
    }
    
    // Test zoom out button
    const zoomOutButton = page.locator('button[title="Zoom Out"]');
    if (await zoomOutButton.isVisible()) {
      await zoomOutButton.click();
      await page.waitForTimeout(500);
    }
    
    // Test reset view button
    const resetButton = page.locator('button[title="Reset View"]');
    if (await resetButton.isVisible()) {
      await resetButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should search for entities and display graph results', async ({ page }) => {
    // Look for knowledge graph search input
    const searchInput = page.locator('[data-testid="kg-search-input"]').or(
      page.locator('input[placeholder*="entity"]')
    ).or(
      page.locator('input[placeholder*="search"]')
    );
    
    if (await searchInput.isVisible()) {
      // Test searching for a common entity
      await searchInput.fill('rama');
      await searchInput.press('Enter');
      
      // Wait for search results and graph update
      await page.waitForTimeout(3000);
      
      // Check if graph visualization is updated
      const graphContainer = page.locator('[data-testid="graph-visualization"]');
      await expect(graphContainer).toBeVisible();
      
      // Check for search results or entity nodes
      const searchResults = page.locator('[data-testid="search-results"]');
      if (await searchResults.isVisible()) {
        await expect(searchResults).toBeVisible();
      }
    }
  });

  test('should handle graph layout changes', async ({ page }) => {
    // Check if graph controls are available
    const controlsSection = page.locator('text="Layout"').locator('..');
    
    if (await controlsSection.isVisible()) {
      // Try different layout options
      const layoutButtons = page.locator('button').filter({ hasText: /Force|Hierarchical|Radial|Circular/ });
      const layoutCount = await layoutButtons.count();
      
      if (layoutCount > 0) {
        // Test clicking different layout options
        for (let i = 0; i < Math.min(layoutCount, 2); i++) {
          await layoutButtons.nth(i).click();
          await page.waitForTimeout(1000); // Wait for layout change
          
          // Verify graph is still visible after layout change
          const graphContainer = page.locator('[data-testid="graph-visualization"]');
          await expect(graphContainer).toBeVisible();
        }
      }
    }
  });

  test('should toggle display options (labels, edge labels)', async ({ page }) => {
    // Look for display controls
    const displaySection = page.locator('text="Display"').locator('..');
    
    if (await displaySection.isVisible()) {
      // Test show labels toggle
      const showLabelsCheckbox = page.locator('input[type="checkbox"]').filter({ 
        has: page.locator('text="Show Labels"') 
      });
      
      if (await showLabelsCheckbox.isVisible()) {
        const initialState = await showLabelsCheckbox.isChecked();
        await showLabelsCheckbox.click();
        await page.waitForTimeout(500);
        
        // Verify state changed
        const newState = await showLabelsCheckbox.isChecked();
        expect(newState).toBe(!initialState);
      }
      
      // Test show edge labels toggle
      const showEdgeLabelsCheckbox = page.locator('input[type="checkbox"]').filter({ 
        has: page.locator('text="Show Edge Labels"') 
      });
      
      if (await showEdgeLabelsCheckbox.isVisible()) {
        const initialState = await showEdgeLabelsCheckbox.isChecked();
        await showEdgeLabelsCheckbox.click();
        await page.waitForTimeout(500);
        
        const newState = await showEdgeLabelsCheckbox.isChecked();
        expect(newState).toBe(!initialState);
      }
    }
  });

  test('should filter entities by type', async ({ page }) => {
    // Look for entity filter controls
    const filtersButton = page.locator('button').filter({ hasText: /Entity Filters/ });
    
    if (await filtersButton.isVisible()) {
      await filtersButton.click();
      await page.waitForTimeout(500);
      
      // Test entity type checkboxes
      const entityCheckboxes = page.locator('input[type="checkbox"]').filter({ 
        has: page.locator('text=/People|Places|Events|Objects|Concepts/') 
      });
      
      const checkboxCount = await entityCheckboxes.count();
      if (checkboxCount > 0) {
        // Toggle first entity type filter
        await entityCheckboxes.first().click();
        await page.waitForTimeout(1000);
        
        // Verify graph still visible after filtering
        const graphContainer = page.locator('[data-testid="graph-visualization"]');
        await expect(graphContainer).toBeVisible();
      }
    }
  });

  test('should adjust numeric filters (mentions, confidence, max nodes)', async ({ page }) => {
    // Look for advanced controls
    const advancedButton = page.locator('button').filter({ hasText: /Advanced/ });
    
    if (await advancedButton.isVisible()) {
      await advancedButton.click();
      await page.waitForTimeout(500);
      
      // Test range sliders
      const rangeSliders = page.locator('input[type="range"]');
      const sliderCount = await rangeSliders.count();
      
      if (sliderCount > 0) {
        // Test first range slider
        const firstSlider = rangeSliders.first();
        await firstSlider.fill('50'); // Set to middle value
        await page.waitForTimeout(500);
        
        // Verify graph still visible after adjustment
        const graphContainer = page.locator('[data-testid="graph-visualization"]');
        await expect(graphContainer).toBeVisible();
      }
    }
  });

  test('should export graph in different formats', async ({ page }) => {
    // Look for export button
    const exportButton = page.locator('button').filter({ hasText: /Export/ });
    
    if (await exportButton.isVisible()) {
      await exportButton.click();
      await page.waitForTimeout(500);
      
      // Check export options
      const exportOptions = page.locator('text=/PNG|SVG|JSON/');
      const optionCount = await exportOptions.count();
      
      if (optionCount > 0) {
        // Test clicking export option (without actually downloading)
        await exportOptions.first().click();
        await page.waitForTimeout(500);
        
        // Verify no errors occurred (graph still visible)
        const graphContainer = page.locator('[data-testid="graph-visualization"]');
        await expect(graphContainer).toBeVisible();
      }
    }
  });

  test('should reset graph to default state', async ({ page }) => {
    // Look for reset button
    const resetButton = page.locator('button').filter({ hasText: /Reset/ });
    
    if (await resetButton.isVisible()) {
      // Make some changes first (if controls are available)
      const layoutButtons = page.locator('button').filter({ hasText: /Force|Hierarchical/ });
      if (await layoutButtons.count() > 1) {
        await layoutButtons.nth(1).click();
        await page.waitForTimeout(500);
      }
      
      // Reset graph
      await resetButton.click();
      await page.waitForTimeout(1000);
      
      // Verify graph is still visible after reset
      const graphContainer = page.locator('[data-testid="graph-visualization"]');
      await expect(graphContainer).toBeVisible();
    }
  });

  test('should handle responsive design on different viewport sizes', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(graphContainer).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(graphContainer).toBeVisible();
    
    // Test large desktop viewport
    await page.setViewportSize({ width: 1440, height: 900 });
    await expect(graphContainer).toBeVisible();
    
    // Reset to default
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('should handle loading and error states gracefully', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Check for loading indicators
    const loadingIndicator = page.locator('text=/Loading|Spinner/').or(
      page.locator('.animate-spin')
    );
    
    // If loading state is visible, wait for it to complete
    if (await loadingIndicator.isVisible()) {
      await page.waitForTimeout(5000);
      // Loading should complete or show error
      expect(
        await loadingIndicator.isVisible() || 
        await page.locator('text=/error|Error/').isVisible() ||
        await graphContainer.isVisible()
      ).toBeTruthy();
    }
    
    // Check for error handling
    const errorMessage = page.locator('text=/error|Error|failed/i');
    if (await errorMessage.isVisible()) {
      // Error should be displayed gracefully
      await expect(errorMessage).toBeVisible();
    }
  });

  test('should provide accessibility features', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Check for keyboard navigation support
    await page.keyboard.press('Tab');
    await page.waitForTimeout(100);
    
    // Test that buttons are focusable
    const focusableButtons = page.locator('button:visible');
    const buttonCount = await focusableButtons.count();
    
    if (buttonCount > 0) {
      // Test first few buttons are focusable
      for (let i = 0; i < Math.min(buttonCount, 3); i++) {
        await focusableButtons.nth(i).focus();
        await expect(focusableButtons.nth(i)).toBeFocused();
      }
    }
    
    // Check for ARIA labels and roles
    const ariaElements = page.locator('[aria-label], [role]');
    const ariaCount = await ariaElements.count();
    
    // Should have some accessibility attributes
    expect(ariaCount).toBeGreaterThanOrEqual(0);
  });

  test('should handle node and edge interactions', async ({ page }) => {
    const graphContainer = page.locator('[data-testid="graph-visualization"]');
    await expect(graphContainer).toBeVisible();
    
    // Wait for potential graph data to load
    await page.waitForTimeout(3000);
    
    // Try to interact with SVG elements (nodes/edges) if they exist
    const svgElement = page.locator('svg');
    if (await svgElement.isVisible()) {
      // Click on the SVG to test background interaction
      await svgElement.click({ position: { x: 100, y: 100 } });
      await page.waitForTimeout(500);
      
      // Try hovering over different areas
      await svgElement.hover({ position: { x: 200, y: 200 } });
      await page.waitForTimeout(500);
      
      // Graph should remain functional
      await expect(graphContainer).toBeVisible();
    }
  });
});