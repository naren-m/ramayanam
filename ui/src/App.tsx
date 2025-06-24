import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { SearchProvider } from './contexts/SearchContext';
import Header from './components/Header';
import SearchInterface from './components/SearchInterface';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <SearchProvider>
        <div className="min-h-screen bg-gradient-to-br from-cream-50 to-orange-50 dark:from-gray-900 dark:to-blue-900 transition-colors duration-300">
          <div className="absolute inset-0 opacity-5 dark:opacity-10">
            <div className="lotus-pattern"></div>
          </div>
          <div className="relative z-10">
            <Header />
            <main className="container mx-auto px-4 py-8">
              <SearchInterface />
              <ResultsDisplay />
            </main>
          </div>
        </div>
      </SearchProvider>
    </ThemeProvider>
  );
}

export default App;