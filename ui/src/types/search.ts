// Enhanced Search Types for Advanced Filtering

export interface AdvancedSearchFilters {
  // Location filters
  kanda: number[];              // Multi-select kandas
  sarga: number[];              // Sarga range selection
  
  // Search precision
  searchMode: 'fuzzy' | 'exact' | 'semantic';
  minRatio: number;             // Existing similarity ratio
  textLength: { min?: number; max?: number };
  
  // Results & display
  sortBy: 'relevance' | 'chronological' | 'textLength';
  language: 'sanskrit' | 'english' | 'both';
  includeAnnotations: boolean;
  
  // Entity-based filters (for future integration)
  entityTypes: string[];
  characterFilter: string[];
  placeFilter: string[];
  conceptFilter: string[];
  
  // Text selection
  texts: string[];
}

export interface SearchPreset {
  id: string;
  name: string;
  description: string;
  icon: string;
  filters: Partial<AdvancedSearchFilters>;
  isCustom: boolean;
  usageCount?: number;
}

export interface SearchSuggestion {
  query: string;
  type: 'character' | 'concept' | 'place' | 'preset';
  resultCount: number;
  filters?: Partial<AdvancedSearchFilters>;
}

export interface FilterSection {
  id: string;
  title: string;
  icon: string;
  expanded: boolean;
  order: number;
}

// Existing SearchFilters interface (for backward compatibility)
export interface SearchFilters {
  kanda: number | null;
  minRatio: number;
  texts: string[];
}

// Enhanced SearchContext type
export interface EnhancedSearchContextType {
  // Enhanced filter management
  advancedFilters: AdvancedSearchFilters;
  setAdvancedFilters: (filters: Partial<AdvancedSearchFilters>) => void;
  resetFilters: () => void;
  
  // Filter presets
  filterPresets: SearchPreset[];
  applyPreset: (presetId: string) => void;
  saveCustomPreset: (name: string, description: string) => void;
  deleteCustomPreset: (presetId: string) => void;
  
  // Search suggestions
  suggestions: SearchSuggestion[];
  getSuggestions: (query: string) => Promise<SearchSuggestion[]>;
  
  // Filter state management
  activeFilters: Array<{ key: string; label: string; value: any }>;
  removeFilter: (key: string) => void;
  
  // Core search functionality
  searchVerses: (query: string, type: 'english' | 'sanskrit') => Promise<void>;
  clearSearch: () => void;
  loading: boolean;
  
  // Backward compatibility
  filters: SearchFilters;
  setFilters: (filters: Partial<SearchFilters>) => void;
}

// Component prop types
export interface MultiSelectProps {
  options: Array<{ value: string | number; label: string; description?: string; disabled?: boolean }>;
  selectedValues: (string | number)[];
  onChange: (values: (string | number)[]) => void;
  placeholder?: string;
  maxDisplayed?: number;
  className?: string;
  disabled?: boolean;
  searchable?: boolean;
}

export interface RangeSliderProps {
  min: number;
  max: number;
  value: { min?: number; max?: number };
  onChange: (value: { min?: number; max?: number }) => void;
  step?: number;
  label?: string;
  unit?: string;
  showInput?: boolean;
  className?: string;
  disabled?: boolean;
}

export interface RadioGroupProps {
  options: Array<{
    value: string;
    label: string;
    description?: string;
    icon?: React.ComponentType<{ className?: string }>;
    disabled?: boolean;
  }>;
  value: string;
  onChange: (value: string) => void;
  name: string;
  label?: string;
  layout?: 'horizontal' | 'vertical' | 'grid';
  className?: string;
  disabled?: boolean;
}

export interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'orange' | 'blue' | 'green' | 'purple';
  disabled?: boolean;
  className?: string;
}

// Default values
export const DEFAULT_ADVANCED_FILTERS: AdvancedSearchFilters = {
  kanda: [],
  sarga: [],
  searchMode: 'fuzzy',
  minRatio: 30,
  textLength: { min: undefined, max: undefined },
  sortBy: 'relevance',
  language: 'both',
  includeAnnotations: true,
  entityTypes: [],
  characterFilter: [],
  placeFilter: [],
  conceptFilter: [],
  texts: ['ramayana']
};

// Predefined search presets
export const DEFAULT_SEARCH_PRESETS: SearchPreset[] = [
  {
    id: 'character-dialogues',
    name: 'Character Dialogues',
    description: 'Find direct speech and conversations',
    icon: '💬',
    filters: {
      textLength: { min: 50, max: 300 },
      sortBy: 'chronological',
      language: 'english'
    },
    isCustom: false
  },
  {
    id: 'moral-teachings',
    name: 'Moral Teachings',
    description: 'Philosophical and ethical guidance',
    icon: '📚',
    filters: {
      searchMode: 'semantic',
      conceptFilter: ['dharma', 'duty', 'righteousness'],
      sortBy: 'relevance'
    },
    isCustom: false
  },
  {
    id: 'battle-scenes',
    name: 'Battle Scenes',
    description: 'War and combat descriptions',
    icon: '⚔️',
    filters: {
      kanda: [4, 6], // Kishkindha and Yuddha
      textLength: { min: 100 },
      sortBy: 'chronological'
    },
    isCustom: false
  },
  {
    id: 'devotional-verses',
    name: 'Devotional Verses',
    description: 'Prayers and devotional content',
    icon: '🙏',
    filters: {
      conceptFilter: ['prayer', 'devotion', 'worship'],
      language: 'both',
      sortBy: 'relevance'
    },
    isCustom: false
  },
  {
    id: 'nature-descriptions',
    name: 'Nature Descriptions',
    description: 'Descriptions of forests, rivers, and landscapes',
    icon: '🌿',
    filters: {
      placeFilter: ['forest', 'river', 'mountain'],
      textLength: { min: 80 },
      sortBy: 'relevance'
    },
    isCustom: false
  }
];

// Kanda information
export const KANDAS = [
  { value: 1, label: 'Bala Kandam', description: 'Childhood and youth of Rama' },
  { value: 2, label: 'Ayodhya Kandam', description: 'Rama\'s exile from Ayodhya' },
  { value: 3, label: 'Aranya Kandam', description: 'Forest exile and Sita\'s abduction' },
  { value: 4, label: 'Kishkindha Kandam', description: 'Alliance with Hanuman and Sugriva' },
  { value: 5, label: 'Sundara Kandam', description: 'Hanuman\'s journey to Lanka' },
  { value: 6, label: 'Yuddha Kandam', description: 'War with Ravana and return to Ayodhya' }
];

// Filter section configuration
export const FILTER_SECTIONS: FilterSection[] = [
  {
    id: 'location',
    title: 'Location Filters',
    icon: '📍',
    expanded: true,
    order: 1
  },
  {
    id: 'precision',
    title: 'Search Precision',
    icon: '🎯',
    expanded: true,
    order: 2
  },
  {
    id: 'content',
    title: 'Content Filters',
    icon: '📖',
    expanded: false,
    order: 3
  },
  {
    id: 'display',
    title: 'Results & Display',
    icon: '📊',
    expanded: false,
    order: 4
  }
];