import React from 'react';
import Header from './components/Header';
import SearchInterface from './components/SearchInterface';
import ResultsDisplay from './components/ResultsDisplay';
import ErrorBoundary from './components/ErrorBoundary';
import { ThemeProvider } from './contexts/ThemeContext';
import { SearchProvider } from './contexts/SearchContext';
import './App.css';

function App() {
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
              <main className="container mx-auto px-4 py-8">
                <ErrorBoundary>
                  <SearchInterface />
                </ErrorBoundary>
                <ErrorBoundary>
                  <ResultsDisplay />
                </ErrorBoundary>
              </main>
            </div>
          </div>
        </SearchProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;