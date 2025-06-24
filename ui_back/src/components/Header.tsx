import React, { useState } from 'react';
import { Sun, Moon, Search, Book, Heart, History, Settings } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useSearch } from '../contexts/SearchContext';

const Header: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const { favorites, searchHistory } = useSearch();
  const [showMenu, setShowMenu] = useState(false);

  return (
    <header className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gold-200/20 dark:border-gold-700/20 sticky top-0 z-50" data-testid="header">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-saffron-400 to-terracotta-500 rounded-full flex items-center justify-center">
                <Book className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -inset-1 bg-gradient-to-br from-saffron-400 to-terracotta-500 rounded-full opacity-20 blur"></div>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-heading font-bold bg-gradient-to-r from-saffron-600 to-terracotta-600 dark:from-saffron-400 dark:to-terracotta-400 bg-clip-text text-transparent">
                Ramayana Digital Corpus
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                Search the Ancient Epic
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-2">
            <div className="hidden md:flex items-center space-x-2">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gold-100 dark:hover:bg-gray-700 transition-colors"
                title="Search History"
              >
                <History className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {searchHistory.length}
                </span>
              </button>
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gold-100 dark:hover:bg-gray-700 transition-colors"
                title="Favorites"
              >
                <Heart className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {favorites.length}
                </span>
              </button>
            </div>
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-gold-100 dark:bg-gray-700 text-gold-700 dark:text-gold-400 hover:bg-gold-200 dark:hover:bg-gray-600 transition-colors"
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              data-testid="theme-toggle"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Decorative Border */}
        <div className="mt-4 h-1 bg-gradient-to-r from-saffron-400 via-gold-400 to-terracotta-400 rounded-full"></div>
      </div>
    </header>
  );
};

export default Header;