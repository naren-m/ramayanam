import React, { createContext, useContext, useState, useCallback } from 'react';
import { Verse, SearchFilters, SearchHistory, FavoriteVerse } from '../types';
import { searchAPI } from '../utils/api';

interface PaginationMetadata {
  page: number;
  page_size: number;
  total_results: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface SearchContextType {
  verses: Verse[];
  loading: boolean;
  loadingMore: boolean;
  error: string | null;
  searchHistory: SearchHistory[];
  favorites: FavoriteVerse[];
  totalResults: number;
  currentPage: number;
  searchQuery: string;
  searchType: 'english' | 'sanskrit';
  filters: SearchFilters;
  useStreaming?: boolean;
  pagination?: { page_size: number };
  paginationMeta?: PaginationMetadata;
  
  searchVerses: (query: string, type: 'english' | 'sanskrit') => Promise<void>;
  loadMoreResults: () => Promise<void>;
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
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paginationMeta, setPaginationMeta] = useState<PaginationMetadata | undefined>();
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
  // Adding pagination and streaming settings for compatibility with ui_back
  const pagination = { page_size: 20 };
  const useStreaming = false;

  // This function is only called when Enter is pressed in the search input
  const searchVerses = useCallback(async (query: string, type: 'english' | 'sanskrit') => {
    if (!query.trim()) {
      setVerses([]);
      setTotalResults(0);
      setPaginationMeta(undefined);
      return;
    }

    setLoading(true);
    setError(null);
    setSearchQuery(query);
    setSearchType(type);
    setCurrentPage(1);

    try {
      const { verses: results, pagination } = await searchAPI.search(query, type, filters, 1, 10);
      setVerses(results);
      setTotalResults(pagination?.total_results || results.length);
      setPaginationMeta(pagination);

      // Add to search history
      const historyEntry: SearchHistory = {
        id: Date.now().toString(),
        query,
        type,
        timestamp: Date.now(),
        resultCount: pagination?.total_results || results.length
      };

      const updatedHistory = [historyEntry, ...searchHistory.slice(0, 9)];
      setSearchHistory(updatedHistory);
      localStorage.setItem('ramayana-search-history', JSON.stringify(updatedHistory));

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setVerses([]);
      setTotalResults(0);
      setPaginationMeta(undefined);
    } finally {
      setLoading(false);
    }
  }, [filters, searchHistory]);

  const loadMoreResults = useCallback(async () => {
    if (!searchQuery || !paginationMeta?.has_next || loadingMore) {
      return;
    }

    setLoadingMore(true);
    setError(null);

    try {
      const nextPage = paginationMeta.page + 1;
      const { verses: newResults, pagination } = await searchAPI.search(
        searchQuery, 
        searchType, 
        filters, 
        nextPage, 
        10
      );
      
      setVerses(prevVerses => [...prevVerses, ...newResults]);
      setPaginationMeta(pagination);
      setCurrentPage(nextPage);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load more results');
    } finally {
      setLoadingMore(false);
    }
  }, [searchQuery, searchType, filters, paginationMeta, loadingMore]);

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
    setPaginationMeta(undefined);
  }, []);

  return (
    <SearchContext.Provider value={{
      verses,
      loading,
      loadingMore,
      error,
      searchHistory,
      favorites,
      totalResults,
      currentPage,
      searchQuery,
      searchType,
      filters,
      useStreaming,
      pagination,
      paginationMeta,
      searchVerses,
      loadMoreResults,
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