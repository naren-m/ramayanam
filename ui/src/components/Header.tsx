import React, { useState } from 'react';
import { Sun, Moon, Menu, X, BookOpen, Settings, Info } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const Header: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  return (
    <header className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-orange-200/20 dark:border-orange-700/20 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-blue-600 rounded-full flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold gradient-text">
                Sacred Text Research
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Search across ancient scriptures
              </p>
            </div>
          </div>

          {/* Desktop Controls */}
          <div className="hidden md:flex items-center space-x-4">
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-orange-100 dark:hover:bg-gray-700 transition-colors"
              title="About"
            >
              <Info className="w-5 h-5" />
            </button>
            <button
              onClick={toggleTheme}
              data-testid="theme-toggle-button"
              className="p-2 rounded-lg bg-orange-100 dark:bg-gray-700 text-orange-700 dark:text-orange-400 hover:bg-orange-200 dark:hover:bg-gray-600 transition-colors"
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-orange-100 dark:bg-gray-700 text-orange-700 dark:text-orange-400 hover:bg-orange-200 dark:hover:bg-gray-600 transition-colors"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-orange-200/20 dark:border-orange-700/20">
            <div className="flex flex-col space-y-2 pt-4">
              <button
                onClick={() => {
                  setShowInfo(!showInfo);
                  setIsMenuOpen(false);
                }}
                className="flex items-center space-x-3 px-3 py-3 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-orange-100 dark:hover:bg-gray-700 transition-colors text-left"
              >
                <Info className="w-5 h-5" />
                <span>About</span>
              </button>
            </div>
          </div>
        )}

        {/* Info Panel */}
        {showInfo && (
          <div className="mt-4 p-4 bg-orange-50 dark:bg-gray-800 rounded-lg border border-orange-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">About This Platform</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Search and explore ancient Sanskrit texts including the Valmiki Ramayana with over 12,000 verses. 
              Use fuzzy search in both English and Sanskrit to find relevant passages for your research.
            </p>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              <p>• Valmiki Ramayana: Complete with 6 Kandams</p>
              <p>• Search in English translations or Sanskrit text</p>
              <p>• Filter by specific Kandams for focused research</p>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;