import React, { createContext, useContext, useState, useCallback } from 'react';
import { Verse, SearchFilters, SearchHistory, FavoriteVerse, PaginationInfo } from '../types';
import { searchAPI, APIError } from '../utils/api';

interface SearchContextType {
  verses: Verse[];
  loading: boolean;
  streamingProgress: number;
  error: string | null;
  searchHistory: SearchHistory[];
  favorites: FavoriteVerse[];
  pagination: PaginationInfo | null;
  searchQuery: string;
  searchType: 'english' | 'sanskrit';
  filters: SearchFilters;
  useStreaming: boolean;
  
  searchVerses: (query: string, type: 'english' | 'sanskrit') => Promise<void>;
  loadNextPage: () => Promise<void>;
  setFilters: (filters: SearchFilters) => void;
  addToFavorites: (verse: Verse) => void;
  removeFromFavorites: (verseId: string) => void;
  clearSearch: () => void;
  toggleStreamingMode: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingProgress, setStreamingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>(() => {
    const stored = localStorage.getItem('ramayana-search-history');
    return stored ? JSON.parse(stored) : [];
  });
  const [favorites, setFavorites] = useState<FavoriteVerse[]>(() => {
    const stored = localStorage.getItem('ramayana-favorites');
    return stored ? JSON.parse(stored) : [];
  });
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'english' | 'sanskrit'>('english');
  const [useStreaming, setUseStreaming] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    kanda: null,
    minRatio: 0
  });

  const searchVerses = useCallback(async (query: string, type: 'english' | 'sanskrit') => {
    if (!query.trim()) {
      setVerses([]);
      setPagination(null);
      return;
    }

    setLoading(true);
    setError(null);
    setSearchQuery(query);
    setSearchType(type);
    setStreamingProgress(0);

    try {
      // Always use paginated search for better performance
      const response = await searchAPI.search(query, type, filters, 1, 10);
      setVerses(response.results);
      setPagination(response.pagination);
      
      // Auto-load more results in background for better UX
      if (response.pagination.has_next && response.results.length > 0) {
        setTimeout(() => {
          loadMorePagesAutomatically(query, type, filters, 2, 2); // Load next 2 pages
        }, 500);
      }

      // Add to search history
      const historyEntry: SearchHistory = {
        id: Date.now().toString(),
        query,
        type,
        timestamp: Date.now(),
        resultCount: verses.length
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
      setPagination(null);
      
      // Log error for debugging
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchHistory, verses.length]);

  const loadNextPage = useCallback(async () => {
    if (!pagination?.has_next || !searchQuery || useStreaming) return;

    setLoading(true);
    setError(null);

    try {
      const response = await searchAPI.search(
        searchQuery, 
        searchType, 
        filters, 
        pagination.page + 1, 
        pagination.page_size
      );
      
      setVerses(prev => [...prev, ...response.results]);
      setPagination(response.pagination);
    } catch (err) {
      const errorMessage = err instanceof APIError 
        ? err.message 
        : 'Failed to load next page';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [pagination, searchQuery, searchType, filters, useStreaming]);

  const loadMorePagesAutomatically = useCallback(async (
    query: string, 
    type: 'english' | 'sanskrit', 
    searchFilters: SearchFilters,
    startPage: number, 
    numPages: number
  ) => {
    try {
      for (let page = startPage; page < startPage + numPages; page++) {
        const response = await searchAPI.search(query, type, searchFilters, page, 5);
        if (response.results.length > 0) {
          setVerses(prev => [...prev, ...response.results]);
          setPagination(response.pagination);
          
          // Small delay between pages to show progressive loading
          if (page < startPage + numPages - 1) {
            await new Promise(resolve => setTimeout(resolve, 200));
          }
        } else {
          break;
        }
      }
    } catch (err) {
      console.error('Auto-loading failed:', err);
    }
  }, []);

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
    setPagination(null);
    setStreamingProgress(0);
  }, []);

  const toggleStreamingMode = useCallback(() => {
    setUseStreaming(prev => !prev);
    clearSearch();
  }, [clearSearch]);

  return (
    <SearchContext.Provider value={{
      verses,
      loading,
      streamingProgress,
      error,
      searchHistory,
      favorites,
      pagination,
      searchQuery,
      searchType,
      filters,
      useStreaming,
      searchVerses,
      loadNextPage,
      setFilters,
      addToFavorites,
      removeFromFavorites,
      clearSearch,
      toggleStreamingMode
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