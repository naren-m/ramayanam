export interface Verse {
  sloka_number: string;
  ratio: number;
  sloka: string;
  meaning: string;
  translation: string;
  source?: string; // 'ramayana' | 'bhagavad-gita' | 'mahabharata'
}

export interface SearchFilters {
  kanda: number | null;
  minRatio: number;
  texts?: string[]; // Selected texts for cross-search
}

export interface SearchHistory {
  id: string;
  query: string;
  type: 'english' | 'sanskrit';
  timestamp: number;
  resultCount: number;
  searchMode?: 'single' | 'cross';
  texts?: string[];
}

export interface FavoriteVerse {
  id: string;
  verse: Verse;
  timestamp: number;
  note?: string;
}

export interface AppSettings {
  theme: 'light' | 'dark';
  language: 'en' | 'hi';
  resultsPerPage: number;
  autoSearch: boolean;
}