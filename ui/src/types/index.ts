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
  threshold?: number;
  texts?: string[]; // Selected texts for cross-search
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

// Chat interfaces
export interface ChatMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  references?: TextReference[];
  context?: ChatContext;
}

export interface TextReference {
  text_id: string;
  unit_id: string;
  hierarchy_path: string;
  excerpt: string;
  relevance_score: number;
}

export interface ChatContext {
  active_text?: string;
  discussion_topic?: string;
  referenced_units: string[];
  user_intent: 'search' | 'analyze' | 'compare' | 'explain' | 'discuss' | 'general';
}

export interface Conversation {
  conversation_id: string;
  messages: ChatMessage[];
  message_count: number;
}

export interface ConversationSummary {
  conversation_id: string;
  summary: {
    message_count: number;
    user_messages: number;
    assistant_messages: number;
    topics: string[];
    texts_discussed: string[];
    start_time?: string;
    last_activity?: string;
  };
}

export interface AIProvider {
  id: string;
  name: string;
  available: boolean;
  models?: string[];
  reason?: string;
}

export interface AIStatus {
  provider: string;
  available: boolean;
  capabilities: {
    text_analysis: boolean;
    verse_search: boolean;
    philosophical_discussion: boolean;
    cross_text_comparison: boolean;
    multilingual: boolean;
  };
  note?: string;
}

// Text management interfaces
export interface TextMetadata {
  id: string;
  name: string;
  language: string;
  type: string;
  structure: TextStructure;
  metadata: {
    author?: string;
    estimated_date?: string;
    description: string;
    total_units: number;
    languages_available: string[];
  };
}

export interface TextStructure {
  hierarchy_levels: HierarchyLevel[];
  max_depth: number;
  total_units: number;
  root_collections: string[];
}

export interface HierarchyLevel {
  name: string;
  display_name: string;
  order: number;
  parent_level?: string;
}