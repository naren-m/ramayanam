import React, { useState } from 'react';
import Header from './components/Header';
import SearchInterface from './components/SearchInterface';
import ResultsDisplay from './components/ResultsDisplay';
import ErrorBoundary from './components/ErrorBoundary';
import { ChatInterface } from './components/chat/ChatInterface';
import { ThemeProvider } from './contexts/ThemeContext';
import { SearchProvider } from './contexts/SearchContext';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState<'search' | 'chat'>('search');

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <SearchProvider>
          <div className="min-h-screen bg-gradient-to-br from-cream-50 to-cream-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
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
                      className={`px-6 py-2 rounded-md transition-colors ${
                        activeView === 'search'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      Search Verses
                    </button>
                    <button
                      onClick={() => setActiveView('chat')}
                      className={`px-6 py-2 rounded-md transition-colors ${
                        activeView === 'chat'
                          ? 'bg-blue-600 text-white'
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
        </SearchProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;