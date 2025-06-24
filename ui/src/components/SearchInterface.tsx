import React, { useState, useCallback } from 'react';
import { Search, Filter, X, ChevronDown } from 'lucide-react';
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

const SearchInterface: React.FC = () => {
  const { searchVerses, filters, setFilters, clearSearch, loading, useStreaming, pagination } = useSearch();
  const [englishQuery, setEnglishQuery] = useState('');
  const [sanskritQuery, setSanskritQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [activeTab, setActiveTab] = useState<'english' | 'sanskrit'>('english');

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

  return (
    <div className="mb-8" data-testid="search-interface">
      {/* Search Tabs */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gold-500 w-5 h-5" />
            <input
              type="text"
              value={englishQuery}
              onChange={(e) => handleEnglishSearch(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, 'english')}
              placeholder="Search English translations..."
              className={`search-input w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none ${
                activeTab === 'english' ? 'ring-2 ring-gold-400' : ''
              }`}
              disabled={loading}
              data-testid="english-search-input"
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
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gold-500 w-5 h-5" />
            <input
              type="text"
              value={sanskritQuery}
              onChange={(e) => handleSanskritSearch(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, 'sanskrit')}
              placeholder="खोजें (Search in Sanskrit)..."
              className={`search-input sanskrit-text w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none ${
                activeTab === 'sanskrit' ? 'ring-2 ring-gold-400' : ''
              }`}
              disabled={loading}
              data-testid="sanskrit-search-input"
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
          className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gold-200 dark:border-gold-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gold-50 dark:hover:bg-gray-700 transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Quick Kandam Filter */}
        <select
          value={filters.kanda || ''}
          onChange={(e) => setFilters({ ...filters, kanda: e.target.value ? Number(e.target.value) : null })}
          className="px-4 py-2 bg-white dark:bg-gray-800 border border-gold-200 dark:border-gold-700 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-gold-400"
          data-testid="kanda-filter"
        >
          {KANDAS.map(kanda => (
            <option key={kanda.value || 'all'} value={kanda.value || ''}>
              {kanda.label}
            </option>
          ))}
        </select>
      </div>

      {/* Extended Filters */}
      {showFilters && (
        <div className="mt-4 p-4 bg-white dark:bg-gray-800 border border-gold-200 dark:border-gold-700 rounded-lg fade-in-up">
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
                className="w-full h-2 bg-gold-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
            {!useStreaming && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Search Mode
                </label>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <p>📥 Paginated mode: {pagination?.page_size || 20} results per page</p>
                  <p className="text-xs mt-1">Switch to streaming mode for progressive loading</p>
                </div>
              </div>
            )}
            {useStreaming && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Search Mode
                </label>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <p>🔄 Streaming mode: Results load progressively</p>
                  <p className="text-xs mt-1">Switch to paginated mode for controlled loading</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchInterface;