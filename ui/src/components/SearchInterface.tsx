import React, { useState, useCallback, useEffect } from 'react';
import { Search, Filter, X, ChevronDown, BookOpen, Globe } from 'lucide-react';
import { useSearch } from '../contexts/SearchContext';
import { debounce } from '../utils/api';

const KANDAS = [
  { value: null, label: 'All Kandams' },
  { value: 1, label: 'Bala Kandam' },
  { value: 2, label: 'Ayodhya Kandam' },
  { value: 3, label: 'Aranya Kandam' },
  { value: 4, label: 'Kishkindha Kandam' },
  { value: 5, label: 'Sundara Kandam' },
  { value: 6, label: 'Yuddha Kandam' }
];

const TEXTS = [
  { value: 'ramayana', label: 'Valmiki Ramayana', available: true },
  { value: 'bhagavad-gita', label: 'Bhagavad Gita', available: false },
  { value: 'mahabharata', label: 'Mahabharata', available: false },
  { value: 'upanishads', label: 'Principal Upanishads', available: false },
];

const SEARCH_MODES = [
  { value: 'single', label: 'Search Ramayana', icon: BookOpen },
  { value: 'cross', label: 'Cross-Text Search (Coming Soon)', icon: Globe }
];

const SearchInterface: React.FC = () => {
  const { searchVerses, filters, setFilters, clearSearch, loading } = useSearch();
  const [englishQuery, setEnglishQuery] = useState('');
  const [sanskritQuery, setSanskritQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [activeTab, setActiveTab] = useState<'english' | 'sanskrit'>('english');
  const [searchMode, setSearchMode] = useState<'single' | 'cross'>('single');
  const [selectedTexts, setSelectedTexts] = useState<string[]>(['ramayana']);

  // Sync selectedTexts with search filters
  useEffect(() => {
    setFilters({ ...filters, texts: selectedTexts });
  }, [selectedTexts, setFilters]);

  const debouncedSearch = useCallback(
    debounce((query: string, type: 'english' | 'sanskrit') => {
      searchVerses(query, type);
    }, 500),
    [searchVerses]
  );

  const handleEnglishSearch = (value: string) => {
    setEnglishQuery(value);
    setSanskritQuery('');
    setActiveTab('english');
    if (value.trim()) {
      debouncedSearch(value, 'english');
    } else {
      clearSearch();
    }
  };

  const handleSanskritSearch = (value: string) => {
    setSanskritQuery(value);
    setEnglishQuery('');
    setActiveTab('sanskrit');
    if (value.trim()) {
      debouncedSearch(value, 'sanskrit');
    } else {
      clearSearch();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, type: 'english' | 'sanskrit') => {
    if (e.key === 'Enter') {
      const query = type === 'english' ? englishQuery : sanskritQuery;
      if (query.trim()) {
        searchVerses(query, type);
      }
    }
  };

  const handleTextSelection = (textValue: string) => {
    if (searchMode === 'single') {
      setSelectedTexts([textValue]);
    } else {
      setSelectedTexts(prev => 
        prev.includes(textValue) 
          ? prev.filter(t => t !== textValue)
          : [...prev, textValue]
      );
    }
  };

  const handleSearchModeChange = (mode: 'single' | 'cross') => {
    setSearchMode(mode);
    if (mode === 'single' && selectedTexts.length > 1) {
      setSelectedTexts([selectedTexts[0]]);
    } else if (mode === 'cross' && selectedTexts.length === 0) {
      setSelectedTexts(['ramayana']);
    }
  };

  return (
    <div className="mb-8 search-interface" data-testid="search-interface">
      {/* Search Mode Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Search Mode:
        </label>
        <div className="flex gap-3">
          {SEARCH_MODES.map((mode) => {
            const IconComponent = mode.icon;
            return (
              <button
                key={mode.value}
                onClick={() => mode.value === 'single' && handleSearchModeChange(mode.value)}
                disabled={mode.value === 'cross'}
                className={`flex items-center space-x-2 px-4 py-3 rounded-lg border transition-colors ${
                  searchMode === mode.value
                    ? 'bg-orange-500 text-white border-orange-500'
                    : mode.value === 'cross'
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 border-gray-200 dark:border-gray-600 cursor-not-allowed'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-orange-400'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                <span className="text-sm font-medium">{mode.label}</span>
              </button>
            );
          })}
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          {searchMode === 'single' 
            ? 'Search within the Valmiki Ramayana text for focused research'
            : 'Cross-text search across multiple sacred texts (feature coming soon)'
          }
        </p>
      </div>

      {/* Text Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          {searchMode === 'single' ? 'Select Text:' : 'Select Texts to Search:'}
        </label>
        <div className="flex flex-wrap gap-3">
          {TEXTS.map((text) => {
            const isSelected = selectedTexts.includes(text.value);
            const isDisabled = !text.available;
            
            return (
              <button
                key={text.value}
                onClick={() => text.available && handleTextSelection(text.value)}
                disabled={isDisabled}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  isSelected && text.available
                    ? 'bg-orange-500 text-white border-orange-500'
                    : text.available
                    ? 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-orange-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 border-gray-200 dark:border-gray-600 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-4 h-4" />
                  <span className="text-sm font-medium">{text.label}</span>
                  {!text.available && (
                    <span className="text-xs bg-gray-200 dark:bg-gray-600 px-2 py-0.5 rounded">
                      Coming Soon
                    </span>
                  )}
                  {searchMode === 'cross' && isSelected && (
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
        {searchMode === 'cross' && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Selected {selectedTexts.length} text{selectedTexts.length !== 1 ? 's' : ''} for cross-search
          </p>
        )}
      </div>

      {/* Search Tabs */}
      <div className="flex flex-col lg:flex-row gap-4 mb-6">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search English Translations
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-orange-500 w-5 h-5" />
            <input
              type="text"
              data-testid="english-search-input"
              value={englishQuery}
              onChange={(e) => handleEnglishSearch(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, 'english')}
              placeholder={searchMode === 'cross' 
                ? "Search concepts across texts like 'dharma', 'duty', 'devotion'..."
                : "Search for concepts like 'dharma', 'rama', 'duty'..."
              }
              className={`search-input w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none transition-colors ${
                activeTab === 'english' 
                  ? 'border-orange-400 ring-2 ring-orange-400/20' 
                  : 'border-gray-200 dark:border-gray-600 focus:border-orange-400'
              }`}
              disabled={loading}
            />
            {englishQuery && (
              <button
                onClick={() => {
                  setEnglishQuery('');
                  clearSearch();
                }}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Sanskrit Text
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-orange-500 w-5 h-5" />
            <input
              type="text"
              data-testid="sanskrit-search-input"
              value={sanskritQuery}
              onChange={(e) => handleSanskritSearch(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, 'sanskrit')}
              placeholder={searchMode === 'cross'
                ? "धर्म, भक्ति, या अन्य शब्द खोजें..."
                : "राम, धर्म, या अन्य शब्द खोजें..."
              }
              className={`sanskrit-text w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none bg-white dark:bg-gray-800 border-2 transition-colors ${
                activeTab === 'sanskrit' 
                  ? 'border-orange-400 ring-2 ring-orange-400/20' 
                  : 'border-gray-200 dark:border-gray-600 focus:border-orange-400'
              }`}
              disabled={loading}
            />
            {sanskritQuery && (
              <button
                onClick={() => {
                  setSanskritQuery('');
                  clearSearch();
                }}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Quick Kandam Filter - Only show for Ramayana */}
        {selectedTexts.includes('ramayana') && (
          <select
            data-testid="kanda-filter"
            value={filters.kanda || ''}
            onChange={(e) => setFilters({ ...filters, kanda: e.target.value ? Number(e.target.value) : null })}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-400"
          >
            {KANDAS.map(kanda => (
              <option key={kanda.value || 'all'} value={kanda.value || ''}>
                {kanda.label}
              </option>
            ))}
          </select>
        )}

        {/* Search Tips */}
        <div className="text-sm text-gray-500 dark:text-gray-400 ml-auto hidden lg:block">
          <span>💡 Try: {searchMode === 'cross' ? '"dharma across texts", "devotion", "duty"' : '"dharma", "rama sita", "duty honor"'}</span>
        </div>
      </div>

      {/* Extended Filters */}
      {showFilters && (
        <div className="mt-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Minimum Match Ratio: {filters.minRatio}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.minRatio}
                onChange={(e) => setFilters({ ...filters, minRatio: Number(e.target.value) })}
                className="w-full h-2 bg-orange-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>Any match</span>
                <span>Exact match</span>
              </div>
            </div>
            <div className="flex items-end">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <p className="font-medium mb-1">Search Tips:</p>
                <ul className="text-xs space-y-1">
                  {searchMode === 'cross' ? (
                    <>
                      <li>• Cross-text search finds related concepts</li>
                      <li>• Compare teachings across different texts</li>
                      <li>• Try universal concepts: "dharma", "devotion"</li>
                      <li>• Sanskrit works across all texts</li>
                    </>
                  ) : (
                    <>
                      <li>• Use specific terms for better results</li>
                      <li>• Try character names: "rama", "sita", "hanuman"</li>
                      <li>• Search concepts: "dharma", "duty", "honor"</li>
                      <li>• Sanskrit works too: "राम", "धर्म"</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchInterface;