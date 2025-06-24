export interface Verse {
  sloka_number: string;
  ratio: number;
  sloka: string;
  meaning: string;
  translation: string;
}

export interface SearchFilters {
  kanda: number | null;
  minRatio: number;
  threshold?: number;
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total_results: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse {
  results: Verse[];
  pagination: PaginationInfo;
}

export interface SearchHistory {
  id: string;
  query: string;
  type: 'english' | 'sanskrit';
  timestamp: number;
  resultCount: number;
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