import React from 'react';
import { AlertCircle, BookOpen } from 'lucide-react';
import { useSearch } from '../contexts/SearchContext';
import VerseCard from './VerseCard';
import LoadingSpinner from './LoadingSpinner';

const ResultsDisplay: React.FC = () => {
  const { verses, loading, error, totalResults, searchQuery, searchType } = useSearch();

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
              <li>Removing filters</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Search Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Found {totalResults} verses matching "{searchQuery}" in {searchType} search
          </p>
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