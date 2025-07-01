import React, { useState } from 'react';
import { ChevronDown, ChevronUp, MapPin, Target, BookOpen, BarChart3 } from 'lucide-react';
import { AdvancedSearchFilters, KANDAS, FILTER_SECTIONS } from '../../types/search';
import { MultiSelect, RangeSlider, RadioGroup, ToggleSwitch } from './FilterControls';

interface AdvancedFiltersPanelProps {
  filters: AdvancedSearchFilters;
  onChange: (filters: Partial<AdvancedSearchFilters>) => void;
  onReset: () => void;
  className?: string;
  disabled?: boolean;
}

export const AdvancedFiltersPanel: React.FC<AdvancedFiltersPanelProps> = ({
  filters,
  onChange,
  onReset,
  className = '',
  disabled = false
}) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    location: true,
    precision: true,
    content: false,
    display: false
  });

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Prepare options for MultiSelect components
  const kandaOptions = KANDAS.map(kanda => ({
    value: kanda.value,
    label: kanda.label,
    description: kanda.description
  }));

  const searchModeOptions = [
    {
      value: 'fuzzy',
      label: 'Fuzzy Search',
      description: 'Find similar words and concepts',
      icon: Target
    },
    {
      value: 'exact',
      label: 'Exact Match',
      description: 'Find exact word matches only',
      icon: Target
    },
    {
      value: 'semantic',
      label: 'Semantic Search',
      description: 'AI-powered meaning-based search',
      icon: Target
    }
  ];

  const sortOptions = [
    {
      value: 'relevance',
      label: 'Relevance',
      description: 'Best matches first'
    },
    {
      value: 'chronological',
      label: 'Chronological',
      description: 'Story order (Kanda, then Sarga)'
    },
    {
      value: 'textLength',
      label: 'Text Length',
      description: 'Shortest to longest'
    }
  ];

  const languageOptions = [
    {
      value: 'both',
      label: 'Both Languages',
      description: 'Search Sanskrit and English'
    },
    {
      value: 'english',
      label: 'English Only',
      description: 'Search translations only'
    },
    {
      value: 'sanskrit',
      label: 'Sanskrit Only',
      description: 'Search original text only'
    }
  ];

  const renderSectionHeader = (sectionId: string, title: string, icon: React.ReactNode) => {
    const isExpanded = expandedSections[sectionId];
    
    return (
      <button
        type="button"
        onClick={() => toggleSection(sectionId)}
        className="w-full flex items-center justify-between p-3 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
        disabled={disabled}
      >
        <div className="flex items-center space-x-3">
          <span className="text-lg">{icon}</span>
          <span className="font-medium text-gray-700 dark:text-gray-300">{title}</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
    );
  };

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg ${className}`} data-testid="advanced-filters-panel">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Advanced Filters
          </h3>
          <button
            onClick={onReset}
            disabled={disabled}
            className="text-sm text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 disabled:opacity-50"
          >
            Reset All
          </button>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Refine your search with precise filtering options
        </p>
      </div>

      {/* Filter Sections */}
      <div className="p-4 space-y-4">
        {/* Location Filters */}
        <div className="space-y-3">
          {renderSectionHeader('location', 'Location Filters', <MapPin className="w-5 h-5" />)}
          
          {expandedSections.location && (
            <div className="pl-6 space-y-4">
              {/* Kanda Selection */}
              <div>
                <MultiSelect
                  options={kandaOptions}
                  selectedValues={filters.kanda}
                  onChange={(values) => onChange({ kanda: values as number[] })}
                  placeholder="All Kandas"
                  searchable={false}
                  disabled={disabled}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Select specific books of the Ramayana to search within
                </p>
              </div>

              {/* Sarga Range - TODO: Implement when needed */}
              {filters.kanda.length === 1 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sarga Range (within {KANDAS.find(k => k.value === filters.kanda[0])?.label})
                  </label>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Sarga-level filtering coming soon...
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Search Precision */}
        <div className="space-y-3">
          {renderSectionHeader('precision', 'Search Precision', <Target className="w-5 h-5" />)}
          
          {expandedSections.precision && (
            <div className="pl-6 space-y-4">
              {/* Search Mode */}
              <RadioGroup
                options={searchModeOptions}
                value={filters.searchMode}
                onChange={(value) => onChange({ searchMode: value as 'fuzzy' | 'exact' | 'semantic' })}
                name="searchMode"
                label="Search Algorithm"
                layout="vertical"
                disabled={disabled}
              />

              {/* Match Ratio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Minimum Match Score: {filters.minRatio}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={filters.minRatio}
                  onChange={(e) => onChange({ minRatio: Number(e.target.value) })}
                  disabled={disabled}
                  className="w-full h-2 bg-orange-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>Any match (0%)</span>
                  <span>Perfect match (100%)</span>
                </div>
              </div>

              {/* Text Length */}
              <RangeSlider
                min={1}
                max={500}
                value={filters.textLength}
                onChange={(value) => onChange({ textLength: value })}
                label="Text Length Filter"
                unit=" words"
                showInput={true}
                disabled={disabled}
              />
            </div>
          )}
        </div>

        {/* Content Filters */}
        <div className="space-y-3">
          {renderSectionHeader('content', 'Content Filters', <BookOpen className="w-5 h-5" />)}
          
          {expandedSections.content && (
            <div className="pl-6 space-y-4">
              {/* Entity Filters - Placeholder for future integration */}
              <div className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                <div className="font-medium">Character & Entity Filters</div>
                <div className="text-xs">
                  Advanced entity filtering will be available after the Entity Discovery Module is implemented.
                  This will include:
                </div>
                <ul className="text-xs space-y-1 ml-4">
                  <li>• Filter by characters (Rama, Sita, Hanuman, etc.)</li>
                  <li>• Filter by places (Ayodhya, Lanka, forests, etc.)</li>
                  <li>• Filter by concepts (dharma, devotion, duty, etc.)</li>
                  <li>• Filter by events (battles, ceremonies, journeys, etc.)</li>
                </ul>
              </div>

              {/* Annotations Toggle */}
              <ToggleSwitch
                checked={filters.includeAnnotations}
                onChange={(checked) => onChange({ includeAnnotations: checked })}
                label="Include Annotations"
                description="Search within commentaries and annotations"
                disabled={disabled}
              />
            </div>
          )}
        </div>

        {/* Results & Display */}
        <div className="space-y-3">
          {renderSectionHeader('display', 'Results & Display', <BarChart3 className="w-5 h-5" />)}
          
          {expandedSections.display && (
            <div className="pl-6 space-y-4">
              {/* Sort Order */}
              <RadioGroup
                options={sortOptions}
                value={filters.sortBy}
                onChange={(value) => onChange({ sortBy: value as 'relevance' | 'chronological' | 'textLength' })}
                name="sortBy"
                label="Sort Results By"
                layout="vertical"
                disabled={disabled}
              />

              {/* Language Filter */}
              <RadioGroup
                options={languageOptions}
                value={filters.language}
                onChange={(value) => onChange({ language: value as 'sanskrit' | 'english' | 'both' })}
                name="language"
                label="Language Preference"
                layout="vertical"
                disabled={disabled}
              />
            </div>
          )}
        </div>
      </div>

      {/* Filter Tips */}
      <div className="p-4 bg-orange-50 dark:bg-orange-900/20 border-t border-gray-200 dark:border-gray-600">
        <div className="text-sm text-orange-800 dark:text-orange-200">
          <div className="font-medium mb-1">💡 Filter Tips:</div>
          <ul className="text-xs space-y-0.5">
            <li>• Use fuzzy search for discovering related concepts</li>
            <li>• Try exact match for finding specific quotes</li>
            <li>• Combine Kanda filters with text length for precise results</li>
            <li>• Chronological sorting helps understand story progression</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFiltersPanel;