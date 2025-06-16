import React, { createContext, useContext, useState, useCallback } from 'react';
import { Verse, SearchFilters, SearchHistory, FavoriteVerse } from '../types';
import { searchAPI, APIError } from '../utils/api';

interface SearchContextType {
  verses: Verse[];
  loading: boolean;
  error: string | null;
  searchHistory: SearchHistory[];
  favorites: FavoriteVerse[];
  totalResults: number;
  currentPage: number;
  searchQuery: string;
  searchType: 'english' | 'sanskrit';
  filters: SearchFilters;
  
  searchVerses: (query: string, type: 'english' | 'sanskrit') => Promise<void>;
  setFilters: (filters: SearchFilters) => void;
  addToFavorites: (verse: Verse) => void;
  removeFromFavorites: (verseId: string) => void;
  clearSearch: () => void;
  setCurrentPage: (page: number) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>(() => {
    const stored = localStorage.getItem('ramayana-search-history');
    return stored ? JSON.parse(stored) : [];
  });
  const [favorites, setFavorites] = useState<FavoriteVerse[]>(() => {
    const stored = localStorage.getItem('ramayana-favorites');
    return stored ? JSON.parse(stored) : [];
  });
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'english' | 'sanskrit'>('english');
  const [filters, setFilters] = useState<SearchFilters>({
    kanda: null,
    minRatio: 0
  });

  const searchVerses = useCallback(async (query: string, type: 'english' | 'sanskrit') => {
    if (!query.trim()) {
      setVerses([]);
      setTotalResults(0);
      return;
    }

    setLoading(true);
    setError(null);
    setSearchQuery(query);
    setSearchType(type);
    setCurrentPage(1);

    try {
      const results = await searchAPI.search(query, type, filters);
      setVerses(results);
      setTotalResults(results.length);

      // Add to search history
      const historyEntry: SearchHistory = {
        id: Date.now().toString(),
        query,
        type,
        timestamp: Date.now(),
        resultCount: results.length
      };

      const updatedHistory = [historyEntry, ...searchHistory.slice(0, 9)];
      setSearchHistory(updatedHistory);
      localStorage.setItem('ramayana-search-history', JSON.stringify(updatedHistory));

    } catch (err) {
      const errorMessage = err instanceof APIError 
        ? err.message 
        : err instanceof Error 
          ? err.message 
          : 'An unexpected error occurred during search';
      
      setError(errorMessage);
      setVerses([]);
      setTotalResults(0);
      
      // Log error for debugging
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchHistory]);

  const addToFavorites = useCallback((verse: Verse) => {
    const favorite: FavoriteVerse = {
      id: verse.sloka_number,
      verse,
      timestamp: Date.now()
    };

    const updatedFavorites = [favorite, ...favorites.filter(f => f.id !== verse.sloka_number)];
    setFavorites(updatedFavorites);
    localStorage.setItem('ramayana-favorites', JSON.stringify(updatedFavorites));
  }, [favorites]);

  const removeFromFavorites = useCallback((verseId: string) => {
    const updatedFavorites = favorites.filter(f => f.id !== verseId);
    setFavorites(updatedFavorites);
    localStorage.setItem('ramayana-favorites', JSON.stringify(updatedFavorites));
  }, [favorites]);

  const clearSearch = useCallback(() => {
    setVerses([]);
    setError(null);
    setSearchQuery('');
    setTotalResults(0);
    setCurrentPage(1);
  }, []);

  return (
    <SearchContext.Provider value={{
      verses,
      loading,
      error,
      searchHistory,
      favorites,
      totalResults,
      currentPage,
      searchQuery,
      searchType,
      filters,
      searchVerses,
      setFilters,
      addToFavorites,
      removeFromFavorites,
      clearSearch,
      setCurrentPage
    }}>
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
};