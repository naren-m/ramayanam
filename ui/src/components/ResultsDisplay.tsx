import React from 'react';
import { AlertCircle, BookOpen, Download, ToggleLeft, ToggleRight } from 'lucide-react';
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
    toggleStreamingMode
  } = useSearch();

  if (loading && verses.length === 0) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner />
        {useStreaming && streamingProgress > 0 && (
          <div className="mt-4">
            <div className="w-64 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mx-auto">
              <div 
                className="bg-gradient-to-r from-saffron-500 to-gold-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${streamingProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Loading results... {Math.round(streamingProgress)}%
            </p>
          </div>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6 max-w-md mx-auto" data-testid="error-message">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Search Error
          </h3>
          <p className="text-red-600 dark:text-red-300">
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!searchQuery && verses.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="bg-gradient-to-br from-gold-50 to-saffron-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-8 max-w-lg mx-auto">
          <BookOpen className="w-16 h-16 text-gold-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
            Welcome to Ramayana Digital Corpus
          </h3>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            Search through the ancient Sanskrit epic in both English and Sanskrit. 
            Use the search boxes above to explore verses, characters, and themes.
          </p>
        </div>
      </div>
    );
  }

  if (searchQuery && verses.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 max-w-md mx-auto" data-testid="no-results">
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
              <li>Removing filters</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  const totalResults = pagination?.total_results || verses.length;
  const hasMore = pagination?.has_next || false;

  return (
    <div className="space-y-6" data-testid="search-results">
      {/* Results Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Search Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {useStreaming ? (
              <>Found {verses.length}{totalResults > verses.length ? ` of ${totalResults}` : ''} verses matching "{searchQuery}"</>
            ) : (
              <>Showing {verses.length} of {totalResults} verses matching "{searchQuery}"</>
            )} in {searchType} search
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center gap-4">
          {/* Streaming Mode Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {useStreaming ? 'Streaming' : 'Paginated'}
            </span>
            <button
              onClick={toggleStreamingMode}
              className="text-gold-500 hover:text-gold-600 transition-colors"
              title={useStreaming ? 'Switch to paginated mode' : 'Switch to streaming mode'}
            >
              {useStreaming ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid gap-6">
        {verses.map((verse, index) => (
          <VerseCard
            key={`${verse.sloka_number}-${index}`}
            verse={verse}
            index={index}
          />
        ))}
      </div>

      {/* Loading More Indicator */}
      {loading && verses.length > 0 && (
        <div className="text-center py-6">
          <div className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gold-500"></div>
            <span>Loading more results...</span>
          </div>
        </div>
      )}

      {/* Load More Button */}
      {!useStreaming && hasMore && !loading && (
        <div className="text-center pt-8">
          <button 
            onClick={loadNextPage}
            className="px-6 py-3 bg-gradient-to-r from-saffron-500 to-gold-500 text-white font-medium rounded-lg hover:from-saffron-600 hover:to-gold-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
            data-testid="load-more-button"
          >
            Load More Results
          </button>
        </div>
      )}

      {/* End of Results */}
      {((useStreaming && streamingProgress === 100) || (!useStreaming && !hasMore)) && verses.length > 0 && (
        <div className="text-center pt-8">
          <div className="inline-flex items-center space-x-2 text-gray-500 dark:text-gray-400">
            <Download className="w-4 h-4" />
            <span>All results loaded ({totalResults} total)</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;