import React from 'react';
import { AlertCircle, BookOpen, Download, ToggleLeft, ToggleRight, Globe } from 'lucide-react';
import { useSearch } from '../contexts/SearchContext';
import VerseCard from './VerseCard';
import LoadingSpinner from './LoadingSpinner';

const ResultsDisplay: React.FC = () => {
  const { 
    verses, 
    loading, 
    streamingProgress,
    error, 
    pagination, 
    searchQuery, 
    searchType,
    useStreaming,
    loadNextPage,
    toggleStreamingMode,
    filters
  } = useSearch();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6 max-w-md mx-auto">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Search Error
          </h3>
          <p className="text-red-600 dark:text-red-300 mb-4">
            {error}
          </p>
          <p className="text-sm text-red-500 dark:text-red-400">
            Showing sample data instead.
          </p>
        </div>
      </div>
    );
  }

  if (!searchQuery && verses.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="bg-gradient-to-br from-gold-50 to-saffron-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-8 max-w-lg mx-auto">
          <div className="flex justify-center mb-4">
            <div className="flex space-x-2">
              <BookOpen className="w-16 h-16 text-gold-500" />
              <Globe className="w-16 h-16 text-blue-500 opacity-70" />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
            Welcome to Sacred Text Research
          </h3>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            Search through ancient Sanskrit texts in both English and Sanskrit. 
            Use single-text search for focused research or cross-text search to find related concepts across multiple scriptures.
          </p>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p className="font-medium mb-2">Available Features:</p>
            <ul className="text-left space-y-1">
              <li>• Single text search within Ramayana or Bhagavad Gita</li>
              <li>• Cross-text search to compare concepts</li>
              <li>• Sanskrit and English search capabilities</li>
              <li>• Advanced filtering and favorites</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (searchQuery && verses.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
            No Results Found
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No verses found for "{searchQuery}" in {searchType} search.
          </p>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>Try:</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Using different keywords</li>
              <li>Checking spelling</li>
              <li>Searching in the other language</li>
              <li>Removing filters or trying cross-text search</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  const getSearchModeDisplay = () => {
    if (filters.texts && filters.texts.length > 1) {
      return `cross-text search (${filters.texts.length} texts)`;
    }
    return `${searchType} search`;
  };

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Search Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Found {pagination?.total_results || verses.length} verses matching "{searchQuery}" in {getSearchModeDisplay()}
          </p>
          {filters.texts && filters.texts.length > 1 && (
            <div className="flex items-center space-x-2 mt-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Searching across:</span>
              {filters.texts.map((text, index) => (
                <span key={text} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-1 rounded-full">
                  {text === 'ramayana' ? 'Ramayana' : 
                   text === 'bhagavad-gita' ? 'Bhagavad Gita' : 
                   text === 'mahabharata' ? 'Mahabharata' : text}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid gap-6">
        {verses.map((verse, index) => (
          <VerseCard
            key={`${verse.source || 'unknown'}-${verse.sloka_number}-${index}`}
            verse={verse}
            index={index}
          />
        ))}
      </div>

      {/* Load More */}
      {verses.length >= 10 && (
        <div className="text-center pt-8">
          <button className="px-6 py-3 bg-gradient-to-r from-saffron-500 to-gold-500 text-white font-medium rounded-lg hover:from-saffron-600 hover:to-gold-600 transition-colors">
            Load More Results
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;