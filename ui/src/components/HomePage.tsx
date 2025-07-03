import React, { useState } from 'react';
import Header from './Header';
import SearchInterface from './SearchInterface';
import EnhancedSearchInterface from './Search/EnhancedSearchInterface';
import ResultsDisplay from './ResultsDisplay';
import ErrorBoundary from './ErrorBoundary';
import { ChatInterface } from './chat/ChatInterface';
import { EnhancedKnowledgeGraphSearch } from './KnowledgeGraph';
import { EntityDiscoveryDashboard } from './EntityDiscovery';

const HomePage: React.FC = () => {
  const [activeView, setActiveView] = useState<'search' | 'enhanced-search' | 'chat' | 'knowledge' | 'entities'>('enhanced-search');
  const [searchMode, setSearchMode] = useState<'basic' | 'enhanced'>('enhanced');

  return (
    <div className="min-h-screen bg-gradient-to-br from-cream-50 to-orange-50 dark:from-gray-900 dark:to-blue-900 transition-colors duration-300">
      <div className="absolute inset-0 opacity-5 dark:opacity-10">
        <div className="lotus-pattern"></div>
      </div>
      <div className="relative z-10">
        <Header />
        
        {/* View Toggle */}
        <div className="container mx-auto px-4 pt-4">
          <div className="flex justify-center mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-1 shadow-sm">
              <button
                onClick={() => setActiveView('search')}
                data-testid="search-tab-button"
                className={`px-4 py-2 rounded-md transition-colors text-sm ${
                  activeView === 'search'
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Basic Search
              </button>
              <button
                onClick={() => setActiveView('enhanced-search')}
                data-testid="enhanced-search-tab-button"
                className={`px-4 py-2 rounded-md transition-colors text-sm ${
                  activeView === 'enhanced-search'
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Enhanced Search
              </button>
              <button
                onClick={() => setActiveView('knowledge')}
                data-testid="knowledge-tab-button"
                className={`px-4 py-2 rounded-md transition-colors text-sm ${
                  activeView === 'knowledge'
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Knowledge Graph
              </button>
              <button
                onClick={() => setActiveView('entities')}
                data-testid="entities-tab-button"
                className={`px-4 py-2 rounded-md transition-colors text-sm ${
                  activeView === 'entities'
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Entity Discovery
              </button>
              <button
                onClick={() => setActiveView('chat')}
                data-testid="chat-tab-button"
                className={`px-4 py-2 rounded-md transition-colors text-sm ${
                  activeView === 'chat'
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Chat & Discuss
              </button>
            </div>
          </div>
        </div>

        <main className="container mx-auto px-4 pb-8">
          {activeView === 'search' ? (
            <>
              <ErrorBoundary>
                <SearchInterface />
              </ErrorBoundary>
              <ErrorBoundary>
                <ResultsDisplay />
              </ErrorBoundary>
            </>
          ) : activeView === 'enhanced-search' ? (
            <>
              <ErrorBoundary>
                <div className="max-w-7xl mx-auto">
                  <EnhancedSearchInterface />
                </div>
              </ErrorBoundary>
              <ErrorBoundary>
                <div className="max-w-7xl mx-auto mt-6">
                  <ResultsDisplay />
                </div>
              </ErrorBoundary>
            </>
          ) : activeView === 'knowledge' ? (
            <ErrorBoundary>
              <div className="max-w-7xl mx-auto">
                <EnhancedKnowledgeGraphSearch />
              </div>
            </ErrorBoundary>
          ) : activeView === 'entities' ? (
            <ErrorBoundary>
              <div className="max-w-7xl mx-auto">
                <EntityDiscoveryDashboard />
              </div>
            </ErrorBoundary>
          ) : (
            <ErrorBoundary>
              <div className="max-w-4xl mx-auto h-[600px] bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <ChatInterface activeText="ramayana" />
              </div>
            </ErrorBoundary>
          )}
        </main>
      </div>
    </div>
  );
};

export default HomePage;