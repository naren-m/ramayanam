import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { Verse } from '../types';
import { 
  AdvancedSearchFilters, 
  SearchPreset, 
  SearchSuggestion, 
  DEFAULT_ADVANCED_FILTERS, 
  DEFAULT_SEARCH_PRESETS,
  EnhancedSearchContextType 
} from '../types/search';
import { searchAPI } from '../utils/api';

// Utility functions for filter management
const generateFilterKey = (filters: AdvancedSearchFilters): string => {
  return btoa(JSON.stringify(filters)).slice(0, 16);
};

const debounce = <T extends (...args: any[]) => any>(func: T, delay: number): T => {
  let timeoutId: NodeJS.Timeout;
  return ((...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  }) as T;
};

interface PaginationMetadata {
  page: number;
  page_size: number;
  total_results: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

const EnhancedSearchContext = createContext<EnhancedSearchContextType | undefined>(undefined);

export const EnhancedSearchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Core search state
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'english' | 'sanskrit'>('english');
  const [totalResults, setTotalResults] = useState(0);
  const [paginationMeta, setPaginationMeta] = useState<PaginationMetadata | undefined>();

  // Advanced filters state
  const [advancedFilters, setAdvancedFilters] = useState<AdvancedSearchFilters>(() => {
    const stored = localStorage.getItem('ramayana-advanced-filters');
    return stored ? { ...DEFAULT_ADVANCED_FILTERS, ...JSON.parse(stored) } : DEFAULT_ADVANCED_FILTERS;
  });

  // Filter presets state
  const [customPresets, setCustomPresets] = useState<SearchPreset[]>(() => {
    const stored = localStorage.getItem('ramayana-custom-presets');
    return stored ? JSON.parse(stored) : [];
  });

  // Search suggestions state
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);

  // Backward compatibility - derive legacy filters from advanced filters
  const legacyFilters = {
    kanda: advancedFilters.kanda.length === 1 ? advancedFilters.kanda[0] : null,
    minRatio: advancedFilters.minRatio,
    texts: advancedFilters.texts
  };

  // Save filters to localStorage whenever they change
  useEffect(() => {
    const filtersToSave = {
      ...advancedFilters,
      // Don't save texts array to avoid conflicts
      texts: undefined
    };
    localStorage.setItem('ramayana-advanced-filters', JSON.stringify(filtersToSave));
  }, [advancedFilters]);

  // Save custom presets to localStorage
  useEffect(() => {
    localStorage.setItem('ramayana-custom-presets', JSON.stringify(customPresets));
  }, [customPresets]);

  // Convert advanced filters to API parameters
  const convertFiltersToAPIParams = useCallback((filters: AdvancedSearchFilters) => {
    const apiFilters: any = {};

    // Location filters
    if (filters.kanda.length > 0) {
      apiFilters.kanda = filters.kanda.length === 1 ? filters.kanda[0] : filters.kanda;
    }

    if (filters.sarga.length > 0) {
      apiFilters.sarga = filters.sarga;
    }

    // Search precision
    apiFilters.minRatio = filters.minRatio;
    
    // Text length
    if (filters.textLength.min !== undefined) {
      apiFilters.minLength = filters.textLength.min;
    }
    if (filters.textLength.max !== undefined) {
      apiFilters.maxLength = filters.textLength.max;
    }

    // Search mode
    apiFilters.searchMode = filters.searchMode;

    // Sort order
    apiFilters.sortBy = filters.sortBy;

    // Language
    apiFilters.language = filters.language;

    // Annotations
    apiFilters.includeAnnotations = filters.includeAnnotations;

    return apiFilters;
  }, []);

  // Enhanced search function
  const searchVerses = useCallback(async (query: string, type: 'english' | 'sanskrit') => {
    if (!query.trim()) {
      setVerses([]);
      setTotalResults(0);
      setPaginationMeta(undefined);
      setSearchQuery('');
      return;
    }

    setLoading(true);
    setError(null);
    setSearchQuery(query);
    setSearchType(type);

    try {
      const apiFilters = convertFiltersToAPIParams(advancedFilters);
      const { verses: results, pagination } = await searchAPI.search(query, type, apiFilters, 1, 20);
      
      setVerses(results);
      setTotalResults(pagination?.total_results || results.length);
      setPaginationMeta(pagination);

      // TODO: Add to search history
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setVerses([]);
      setTotalResults(0);
      setPaginationMeta(undefined);
    } finally {
      setLoading(false);
    }
  }, [advancedFilters, convertFiltersToAPIParams]);

  // Advanced filters management
  const setAdvancedFiltersPartial = useCallback((partialFilters: Partial<AdvancedSearchFilters>) => {
    setAdvancedFilters(prev => ({ ...prev, ...partialFilters }));
  }, []);

  const resetFilters = useCallback(() => {
    setAdvancedFilters(DEFAULT_ADVANCED_FILTERS);
  }, []);

  // Filter presets management
  const applyPreset = useCallback((presetId: string) => {
    const preset = [...DEFAULT_SEARCH_PRESETS, ...customPresets].find(p => p.id === presetId);
    if (preset && preset.filters) {
      setAdvancedFiltersPartial(preset.filters);
      
      // Update usage count for custom presets
      if (preset.isCustom) {
        setCustomPresets(prev => 
          prev.map(p => 
            p.id === presetId 
              ? { ...p, usageCount: (p.usageCount || 0) + 1 }
              : p
          )
        );
      }
    }
  }, [customPresets, setAdvancedFiltersPartial]);

  const saveCustomPreset = useCallback((name: string, description: string) => {
    const newPreset: SearchPreset = {
      id: `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      icon: '📝',
      filters: { ...advancedFilters },
      isCustom: true,
      usageCount: 0
    };

    setCustomPresets(prev => [newPreset, ...prev]);
  }, [advancedFilters]);

  const deleteCustomPreset = useCallback((presetId: string) => {
    setCustomPresets(prev => prev.filter(p => p.id !== presetId));
  }, []);

  // Active filters for chips
  const activeFilters = React.useMemo(() => {
    const active: Array<{ key: string; label: string; value: any }> = [];

    if (advancedFilters.kanda.length > 0) {
      active.push({ key: 'kanda', label: 'Kandas', value: advancedFilters.kanda });
    }

    if (advancedFilters.searchMode !== 'fuzzy') {
      active.push({ key: 'searchMode', label: 'Search Mode', value: advancedFilters.searchMode });
    }

    if (advancedFilters.minRatio !== 30) {
      active.push({ key: 'minRatio', label: 'Match Ratio', value: advancedFilters.minRatio });
    }

    if (advancedFilters.textLength.min !== undefined || advancedFilters.textLength.max !== undefined) {
      active.push({ key: 'textLength', label: 'Text Length', value: advancedFilters.textLength });
    }

    if (advancedFilters.sortBy !== 'relevance') {
      active.push({ key: 'sortBy', label: 'Sort Order', value: advancedFilters.sortBy });
    }

    if (advancedFilters.language !== 'both') {
      active.push({ key: 'language', label: 'Language', value: advancedFilters.language });
    }

    return active;
  }, [advancedFilters]);

  // Remove individual filter
  const removeFilter = useCallback((key: string) => {
    const updates: Partial<AdvancedSearchFilters> = {};

    switch (key) {
      case 'kanda':
        updates.kanda = [];
        break;
      case 'sarga':
        updates.sarga = [];
        break;
      case 'searchMode':
        updates.searchMode = 'fuzzy';
        break;
      case 'minRatio':
        updates.minRatio = 30;
        break;
      case 'textLength':
        updates.textLength = { min: undefined, max: undefined };
        break;
      case 'sortBy':
        updates.sortBy = 'relevance';
        break;
      case 'language':
        updates.language = 'both';
        break;
      case 'includeAnnotations':
        updates.includeAnnotations = true;
        break;
    }

    if (Object.keys(updates).length > 0) {
      setAdvancedFiltersPartial(updates);
    }
  }, [setAdvancedFiltersPartial]);

  // Search suggestions (placeholder)
  const getSuggestions = useCallback(async (query: string): Promise<SearchSuggestion[]> => {
    // TODO: Implement actual suggestions API call
    const mockSuggestions: SearchSuggestion[] = [
      {
        query: `${query} rama`,
        type: 'character',
        resultCount: 45,
        filters: { characterFilter: ['rama'] }
      },
      {
        query: `${query} dharma`,
        type: 'concept',
        resultCount: 23,
        filters: { conceptFilter: ['dharma'] }
      }
    ];
    
    setSuggestions(mockSuggestions);
    return mockSuggestions;
  }, []);

  // Clear search
  const clearSearch = useCallback(() => {
    setVerses([]);
    setError(null);
    setSearchQuery('');
    setTotalResults(0);
    setPaginationMeta(undefined);
    setSuggestions([]);
  }, []);

  // Backward compatibility functions
  const setLegacyFilters = useCallback((filters: Partial<typeof legacyFilters>) => {
    const updates: Partial<AdvancedSearchFilters> = {};

    if (filters.kanda !== undefined) {
      updates.kanda = filters.kanda ? [filters.kanda] : [];
    }

    if (filters.minRatio !== undefined) {
      updates.minRatio = filters.minRatio;
    }

    if (filters.texts !== undefined) {
      updates.texts = filters.texts;
    }

    setAdvancedFiltersPartial(updates);
  }, [setAdvancedFiltersPartial]);

  const contextValue: EnhancedSearchContextType = {
    // Enhanced properties
    advancedFilters,
    setAdvancedFilters: setAdvancedFiltersPartial,
    resetFilters,
    
    filterPresets: [...DEFAULT_SEARCH_PRESETS, ...customPresets],
    applyPreset,
    saveCustomPreset,
    deleteCustomPreset,
    
    suggestions,
    getSuggestions,
    
    activeFilters,
    removeFilter,
    
    // Core search functionality
    searchVerses,
    clearSearch,
    loading,
    
    // Backward compatibility
    filters: legacyFilters,
    setFilters: setLegacyFilters
  };

  return (
    <EnhancedSearchContext.Provider value={contextValue}>
      {children}
    </EnhancedSearchContext.Provider>
  );
};

export const useEnhancedSearch = () => {
  const context = useContext(EnhancedSearchContext);
  if (!context) {
    throw new Error('useEnhancedSearch must be used within an EnhancedSearchProvider');
  }
  return context;
};

// Export both contexts for gradual migration
export default EnhancedSearchContext;