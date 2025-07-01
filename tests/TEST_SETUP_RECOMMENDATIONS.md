# E2E Test Setup Recommendations

This document provides recommendations for improving the testability of the Interactive Graph Visualization and Advanced Search Filters features by adding strategic `data-testid` attributes.

## Completed E2E Test Files

### 1. Graph Visualization Tests
- **File**: `tests/e2e/graph-visualization.spec.ts` 
- **Coverage**: 15 comprehensive test cases covering all graph functionality
- **Tests Include**:
  - Component loading and visibility
  - Zoom controls interaction
  - Entity search functionality
  - Layout changes and display options
  - Entity filtering and numeric adjustments
  - Export functionality
  - Reset functionality
  - Responsive design
  - Loading/error state handling
  - Accessibility features
  - Node/edge interactions

### 2. Advanced Search Filters Tests
- **File**: `tests/e2e/advanced-search-filters.spec.ts`
- **Coverage**: 18 comprehensive test cases covering all filter functionality
- **Tests Include**:
  - Filter panel loading and visibility
  - Section expansion/collapse
  - MultiSelect (Kanda selection)
  - RadioGroup (search modes, sorting, language)
  - RangeSlider (text length filtering)
  - Match ratio slider adjustment
  - ToggleSwitch (boolean options)
  - Filter reset functionality
  - Integration with search
  - Filter persistence
  - Helpful tips and descriptions
  - Disabled state handling
  - Responsive design
  - Validation and error handling
  - Keyboard navigation
  - Filter chips/indicators
  - Search presets

## Recommended Data-TestId Additions

### Graph Visualization Components

#### GraphControls.tsx
```typescript
// Layout controls section
<div data-testid="graph-layout-controls">
  <button data-testid="layout-force-button">
  <button data-testid="layout-hierarchical-button">
  <button data-testid="layout-radial-button">
  <button data-testid="layout-circular-button">
</div>

// Display controls
<div data-testid="graph-display-controls">
  <input data-testid="show-labels-checkbox" type="checkbox">
  <input data-testid="show-edge-labels-checkbox" type="checkbox">
</div>

// Entity filters section
<div data-testid="graph-entity-filters">
  <button data-testid="entity-filters-toggle">
  <input data-testid="entity-type-person-checkbox">
  <input data-testid="entity-type-place-checkbox">
  <input data-testid="entity-type-event-checkbox">
  <input data-testid="entity-type-object-checkbox">
  <input data-testid="entity-type-concept-checkbox">
</div>

// Numeric filters
<div data-testid="graph-numeric-filters">
  <input data-testid="min-mentions-slider" type="range">
  <input data-testid="min-confidence-slider" type="range">
  <input data-testid="max-nodes-slider" type="range">
  <input data-testid="show-isolated-nodes-checkbox">
</div>

// Advanced controls
<div data-testid="graph-advanced-controls">
  <button data-testid="advanced-controls-toggle">
  <input data-testid="link-distance-slider" type="range">
  <input data-testid="charge-strength-slider" type="range">
  <select data-testid="color-scheme-select">
</div>

// Action buttons
<button data-testid="graph-export-button">
<button data-testid="graph-reset-button">
```

#### EnhancedKnowledgeGraphSearch.tsx
```typescript
// View mode buttons
<button data-testid="kg-search-mode-button">
<button data-testid="kg-browse-mode-button">
<button data-testid="kg-graph-mode-button">

// Search interface
<input data-testid="kg-search-input" type="text">
<button data-testid="kg-search-button">
<select data-testid="kg-entity-type-select">

// Graph controls container
<div data-testid="graph-controls">

// Statistics display
<div data-testid="kg-statistics">
  <div data-testid="total-entities-stat">
  <div data-testid="total-mentions-stat">
  <div data-testid="people-count-stat">
  <div data-testid="places-count-stat">
</div>

// Entity results
<div data-testid="kg-search-results">
  <div data-testid="entity-card">
    <button data-testid="entity-graph-button">
    <button data-testid="entity-details-button">
  </div>
</div>

// Load graph data button
<button data-testid="load-graph-data-button">
```

### Advanced Search Filters Components

#### AdvancedFiltersPanel.tsx
```typescript
// Main container
<div data-testid="advanced-filters-panel">

// Reset button
<button data-testid="filters-reset-button">

// Section headers
<button data-testid="location-filters-header">
<button data-testid="precision-filters-header">
<button data-testid="content-filters-header">
<button data-testid="display-filters-header">

// Kanda selection
<div data-testid="kanda-multiselect">

// Search mode radio group
<div data-testid="search-mode-radio-group">
  <input data-testid="search-mode-fuzzy" type="radio">
  <input data-testid="search-mode-exact" type="radio">
  <input data-testid="search-mode-semantic" type="radio">
</div>

// Match ratio slider
<input data-testid="match-ratio-slider" type="range">

// Text length range slider
<div data-testid="text-length-range-slider">

// Sort options
<div data-testid="sort-radio-group">
  <input data-testid="sort-relevance" type="radio">
  <input data-testid="sort-chronological" type="radio">
  <input data-testid="sort-text-length" type="radio">
</div>

// Language options
<div data-testid="language-radio-group">
  <input data-testid="language-both" type="radio">
  <input data-testid="language-english" type="radio">
  <input data-testid="language-sanskrit" type="radio">
</div>

// Annotations toggle
<input data-testid="include-annotations-toggle" type="checkbox">

// Filter tips section
<div data-testid="filter-tips">
```

#### EnhancedSearchInterface.tsx
```typescript
// Main container
<div data-testid="enhanced-search-interface">

// Search input
<input data-testid="enhanced-search-input">

// Filter chips container
<div data-testid="filter-chips">
  <span data-testid="filter-chip">
    <button data-testid="remove-filter-chip">
  </span>
</div>

// Search presets
<div data-testid="search-presets">
  <button data-testid="preset-character-dialogues">
  <button data-testid="preset-moral-teachings">
  <button data-testid="preset-battle-scenes">
  <button data-testid="preset-devotional-verses">
  <button data-testid="preset-nature-descriptions">
</div>
```

#### FilterControls Components

##### MultiSelect.tsx
```typescript
<div data-testid="multiselect-container">
  <button data-testid="multiselect-trigger">
  <div data-testid="multiselect-chips">
    <span data-testid="multiselect-chip">
  </div>
  <div data-testid="multiselect-dropdown">
    <input data-testid="multiselect-search" type="text">
    <button data-testid="multiselect-option">
    <button data-testid="multiselect-select-all">
    <button data-testid="multiselect-clear-all">
  </div>
</div>
```

##### RangeSlider.tsx
```typescript
<div data-testid="range-slider-container">
  <input data-testid="range-slider-min" type="range">
  <input data-testid="range-slider-max" type="range">
  <input data-testid="range-input-min" type="number">
  <input data-testid="range-input-max" type="number">
</div>
```

##### RadioGroup.tsx
```typescript
<div data-testid="radio-group-container">
  <input data-testid="radio-option" type="radio">
</div>
```

##### ToggleSwitch.tsx
```typescript
<div data-testid="toggle-switch-container">
  <input data-testid="toggle-switch-input" type="checkbox">
  <label data-testid="toggle-switch-label">
</div>
```

## Test Execution Instructions

### Prerequisites
```bash
# Ensure Docker is running for containerized testing
docker-compose up -d

# Or start local Python server
python run.py
```

### Running the New E2E Tests
```bash
# Navigate to tests directory
cd tests

# Run graph visualization tests
npx playwright test e2e/graph-visualization.spec.ts --config=config/playwright.config.ts --project=chromium

# Run advanced search filters tests
npx playwright test e2e/advanced-search-filters.spec.ts --config=config/playwright.config.ts --project=chromium

# Run all new tests together
npx playwright test e2e/graph-visualization.spec.ts e2e/advanced-search-filters.spec.ts --config=config/playwright.config.ts --project=chromium

# Run with headed browser for debugging
npx playwright test e2e/graph-visualization.spec.ts --config=config/playwright.config.ts --project=chromium --headed

# Generate HTML report
npx playwright show-report
```

### Expected Test Results

**Graph Visualization Tests**: 15 tests covering:
- ✅ Component loading and basic functionality
- ✅ Zoom controls and interactions
- ✅ Entity search and graph updates
- ✅ Layout changes and display options
- ✅ Entity type filtering
- ✅ Numeric filter adjustments
- ✅ Export functionality
- ✅ Reset capabilities
- ✅ Responsive design
- ✅ Loading/error state handling
- ✅ Accessibility features
- ✅ Node/edge interactions

**Advanced Search Filters Tests**: 18 tests covering:
- ✅ Filter panel loading and sections
- ✅ MultiSelect components (Kanda selection)
- ✅ RadioGroup components (modes, sorting, language)
- ✅ RangeSlider components (text length)
- ✅ ToggleSwitch components (boolean options)
- ✅ Filter integration with search
- ✅ Filter persistence and reset
- ✅ Responsive design and accessibility
- ✅ Validation and error handling

## Implementation Priority

### High Priority (Essential for stable testing)
1. Add data-testids to main container elements
2. Add data-testids to interactive buttons and inputs
3. Add data-testids to section headers and toggles

### Medium Priority (Improves test specificity)
1. Add data-testids to individual filter controls
2. Add data-testids to result displays and chips
3. Add data-testids to modal and overlay elements

### Low Priority (Nice to have)
1. Add data-testids to decorative elements
2. Add data-testids to tooltip containers
3. Add data-testids to loading states

## Test Maintenance Notes

1. **Robust Selectors**: Tests use multiple fallback selectors to handle variations in implementation
2. **Conditional Testing**: Tests gracefully handle missing features or different states
3. **Timeout Management**: Appropriate waits for animations and async operations
4. **Error Handling**: Tests continue even if some interactions fail
5. **Accessibility Testing**: Basic keyboard navigation and ARIA attribute checks included

## Integration with Existing Test Suite

These new tests complement the existing test suite:
- **search-functionality.spec.ts**: Basic search operations (8/8 passing)
- **ui-components.spec.ts**: General UI components (6/10 passing)
- **api-integration.spec.ts**: API integration tests (2/8 passing)

Total test coverage after adding new tests: **41 E2E tests** covering all major features of the Ramayanam platform.