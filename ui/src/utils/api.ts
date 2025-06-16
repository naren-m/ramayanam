import { Verse, SearchFilters, PaginatedResponse } from '../types';

const API_BASE_URL = '/api/ramayanam/slokas';

interface APIError {
  message: string;
  status: number;
}

class SearchAPI {
  private async makeRequest(url: string): Promise<any> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.error || `HTTP error! status: ${response.status}`,
          response.status
        );
      }
      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      console.error('API request failed:', error);
      throw new APIError('Network error occurred', 0);
    }
  }


  async search(
    query: string, 
    type: 'english' | 'sanskrit', 
    filters: SearchFilters, 
    page: number = 1, 
    pageSize: number = 10
  ): Promise<PaginatedResponse> {
    if (!query.trim()) {
      throw new APIError('Search query cannot be empty', 400);
    }

    const endpoint = type === 'english' ? 'fuzzy-search' : 'fuzzy-search-sanskrit';
    const params = new URLSearchParams({
      query: query.trim(),
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(filters.kanda && { kanda: filters.kanda.toString() }),
      ...(filters.threshold && { threshold: filters.threshold.toString() })
    });
    
    const url = `${API_BASE_URL}/${endpoint}?${params}`;
    const response = await this.makeRequest(url);
    
    if (!response.results || !Array.isArray(response.results)) {
      throw new APIError('Invalid response format from server', 500);
    }
    
    // Filter by minimum ratio if specified
    const filteredResults = response.results.filter((verse: Verse) => verse.ratio >= filters.minRatio);
    
    return {
      results: filteredResults,
      pagination: response.pagination
    };
  }

  async searchStream(
    query: string,
    type: 'english' | 'sanskrit',
    filters: SearchFilters,
    onBatch: (batch: Verse[], hasMore: boolean) => void,
    onTotal: (total: number) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    if (!query.trim()) {
      throw new APIError('Search query cannot be empty', 400);
    }

    const params = new URLSearchParams({
      query: query.trim(),
      batch_size: '5',
      ...(filters.kanda && { kanda: filters.kanda.toString() }),
      ...(filters.threshold && { threshold: filters.threshold.toString() })
    });
    
    const url = `${API_BASE_URL}/fuzzy-search-stream?${params}`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new APIError(`HTTP error! status: ${response.status}`, response.status);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new APIError('Failed to get response reader', 500);
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'total':
                  onTotal(data.count);
                  break;
                case 'batch':
                  const filteredBatch = data.results.filter((verse: Verse) => verse.ratio >= filters.minRatio);
                  onBatch(filteredBatch, data.has_more);
                  break;
                case 'complete':
                  onComplete();
                  return;
                case 'error':
                  onError(data.message);
                  return;
              }
            } catch (e) {
              console.error('Failed to parse streaming data:', e);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      onError('Network error occurred during streaming');
    }
  }

  async getKandaName(kandaNumber: number): Promise<string> {
    const url = `/api/ramayanam/kandas/${kandaNumber}`;
    const result = await this.makeRequest(url);
    return result.kanda_name;
  }

  async getSloka(kandaNumber: number, sargaNumber: number, slokaNumber: number): Promise<Verse> {
    const url = `/api/ramayanam/kandas/${kandaNumber}/sargas/${sargaNumber}/slokas/${slokaNumber}`;
    return await this.makeRequest(url);
  }
}

class APIError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = 'APIError';
  }
}

export const searchAPI = new SearchAPI();
export { APIError };

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    // Fallback for browsers that don't support clipboard API
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textArea);
    return success;
  }
};

export const formatVerseForSharing = (verse: Verse): string => {
  return `${verse.sloka_number}: ${verse.sloka}\n\n${verse.translation}\n\nSource: Ramayana Digital Corpus`;
};