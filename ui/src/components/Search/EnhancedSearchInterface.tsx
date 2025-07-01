import React, { useState } from 'react';
import { Search, X, Settings, Bookmark, ChevronDown, ChevronUp } from 'lucide-react';
import { useEnhancedSearch } from '../../contexts/EnhancedSearchContext';
import AdvancedFiltersPanel from './AdvancedFiltersPanel';
import FilterChips from './FilterChips';
import SearchPresets from './SearchPresets';

interface EnhancedSearchInterfaceProps {
  className?: string;
}

export const EnhancedSearchInterface: React.FC<EnhancedSearchInterfaceProps> = ({
  className = ''
}) => {
  const {
    advancedFilters,
    setAdvancedFilters,
    resetFilters,
    filterPresets,
    applyPreset,
    saveCustomPreset,
    deleteCustomPreset,
    activeFilters,
    removeFilter,
    searchVerses,
    clearSearch,
    loading,
    getSuggestions
  } = useEnhancedSearch();

  // Local UI state
  const [englishQuery, setEnglishQuery] = useState('');
  const [sanskritQuery, setSanskritQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'english' | 'sanskrit'>('english');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showPresets, setShowPresets] = useState(false);

  // Handle search input changes
  const handleEnglishSearch = (value: string) => {
    setEnglishQuery(value);
    setSanskritQuery('');
    setActiveTab('english');
  };

  const handleSanskritSearch = (value: string) => {
    setSanskritQuery(value);
    setEnglishQuery('');
    setActiveTab('sanskrit');
  };

  // Handle search execution
  const handleKeyDown = (e: React.KeyboardEvent, type: 'english' | 'sanskrit') => {
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      const query = type === 'english' ? englishQuery : sanskritQuery;
      if (query.trim()) {
        searchVerses(query, type);
      }
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = englishQuery || sanskritQuery;
    const type = englishQuery ? 'english' : 'sanskrit';
    if (query.trim()) {
      searchVerses(query, type);
    }
  };

  const handleSearchClick = (type: 'english' | 'sanskrit') => {
    const query = type === 'english' ? englishQuery : sanskritQuery;
    if (query.trim()) {
      searchVerses(query, type);
    }
  };

  // Handle clear
  const handleClear = () => {
    setEnglishQuery('');
    setSanskritQuery('');
    clearSearch();
  };

  // Filter the custom presets from the full presets list
  const customPresets = filterPresets.filter(preset => preset.isCustom);

  return (
    <div className={`space-y-6 ${className}`} data-testid="enhanced-search-interface">
      {/* Main Search Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
              Enhanced Search
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Search the Valmiki Ramayana with advanced filtering and precision controls
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setShowPresets(!showPresets)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-colors ${
                showPresets
                  ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                  : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-orange-300 dark:hover:border-orange-500'
              }`}
            >
              <Bookmark className="w-4 h-4" />
              <span className="text-sm">Presets</span>
              {showPresets ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-colors ${
                showAdvancedFilters
                  ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                  : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-orange-300 dark:hover:border-orange-500'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span className="text-sm">Advanced</span>
              {showAdvancedFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Search Inputs */}
        <form onSubmit={handleSubmit} className="flex flex-col lg:flex-row gap-4 mb-6">
          {/* English Search */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search English Translations
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-orange-500 w-5 h-5" />
              <input
                type="text"
                data-testid="enhanced-search-input"
                value={englishQuery}
                onChange={(e) => handleEnglishSearch(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'english')}
                placeholder="Search for concepts like 'dharma', 'duty', 'devotion'..."
                className={`w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 bg-white dark:bg-gray-800 border-2 focus:outline-none transition-colors ${
                  activeTab === 'english' 
                    ? 'border-orange-400 ring-2 ring-orange-400/20' 
                    : 'border-gray-200 dark:border-gray-600 focus:border-orange-400'
                }`}
                disabled={loading}
              />
              {englishQuery && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
              <button
                type="submit"
                onClick={() => handleSearchClick('english')}
                disabled={loading || !englishQuery.trim()}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-orange-500 hover:text-orange-600 dark:hover:text-orange-400 disabled:text-gray-300 dark:disabled:text-gray-600"
                aria-label="Search English"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Sanskrit Search */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Sanskrit Text
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-orange-500 w-5 h-5" />
              <input
                type="text"
                data-testid="enhanced-sanskrit-search-input"
                value={sanskritQuery}
                onChange={(e) => handleSanskritSearch(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'sanskrit')}
                placeholder="राम, धर्म, या अन्य शब्द खोजें..."
                className={`sanskrit-text w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 bg-white dark:bg-gray-800 border-2 focus:outline-none transition-colors ${
                  activeTab === 'sanskrit' 
                    ? 'border-orange-400 ring-2 ring-orange-400/20' 
                    : 'border-gray-200 dark:border-gray-600 focus:border-orange-400'
                }`}
                disabled={loading}
              />
              {sanskritQuery && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
              <button
                type="submit"
                onClick={() => handleSearchClick('sanskrit')}
                disabled={loading || !sanskritQuery.trim()}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-orange-500 hover:text-orange-600 dark:hover:text-orange-400 disabled:text-gray-300 dark:disabled:text-gray-600"
                aria-label="Search Sanskrit"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>
        </form>

        {/* Active Filters Chips */}
        {activeFilters.length > 0 && (
          <FilterChips
            filters={advancedFilters}
            onRemoveFilter={removeFilter}
            onClearAll={resetFilters}
            className="mb-6"
          />
        )}

        {/* Search Tips */}
        <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
          💡 <strong>Pro tip:</strong> Use presets for common searches, or customize filters for precise results
        </div>
      </div>

      {/* Search Presets Panel */}
      {showPresets && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
          <SearchPresets
            customPresets={customPresets}
            onApplyPreset={applyPreset}
            onSaveCustomPreset={saveCustomPreset}
            onDeleteCustomPreset={deleteCustomPreset}
            disabled={loading}
            className="p-6"
          />
        </div>
      )}

      {/* Advanced Filters Panel */}
      {showAdvancedFilters && (
        <AdvancedFiltersPanel
          filters={advancedFilters}
          onChange={setAdvancedFilters}
          onReset={resetFilters}
          disabled={loading}
          className="shadow-sm"
        />
      )}
    </div>
  );
};

export default EnhancedSearchInterface;