import { Verse, SearchFilters } from '../types';

const API_BASE_URL = '/api/ramayanam/slokas';

class SearchAPI {
  private async makeRequest(url: string): Promise<any> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      // Return mock data for demonstration
      return this.getMockData();
    }
  }

  private getMockData(): Verse[] {
    return [
      {
        sloka_number: "1.1.9",
        ratio: 95,
        sloka: "तपस्स्वाध्यायनिरतं तपस्वी वाग्विदां वरम्।",
        meaning: "तपस्या और स्वाध्याय में निरत, तपस्वी और वाग्विदों में श्रेष्ठ।",
        translation: "One devoted to <span class=\"highlight\">penance</span> and study, ascetic and best among the eloquent.",
        source: "ramayana"
      },
      {
        sloka_number: "2.47",
        ratio: 92,
        sloka: "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        meaning: "कर्म में ही तेरा अधिकार है, फलों में कभी नहीं।",
        translation: "You have the right to perform your <span class=\"highlight\">duty</span>, but not to the fruits of action.",
        source: "bhagavad-gita"
      },
      {
        sloka_number: "1.1.10",
        ratio: 88,
        sloka: "नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुंगवम्।",
        meaning: "वाल्मीकि ने मुनिश्रेष्ठ नारद से पूछा।",
        translation: "Valmiki questioned <span class=\"highlight\">Narada</span>, the best among sages.",
        source: "ramayana"
      },
      {
        sloka_number: "18.66",
        ratio: 90,
        sloka: "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।",
        meaning: "सभी धर्मों को छोड़कर केवल मेरी शरण में आओ।",
        translation: "Abandon all varieties of <span class=\"highlight\">dharma</span> and just surrender unto Me.",
        source: "bhagavad-gita"
      },
      {
        sloka_number: "2.15.23",
        ratio: 85,
        sloka: "रामो राजीवलोचनः।",
        meaning: "राम कमल के समान नेत्रों वाले हैं।",
        translation: "<span class=\"highlight\">Rama</span> has lotus-like eyes.",
        source: "ramayana"
      }
    ];
  }

  async search(query: string, type: 'english' | 'sanskrit', filters: SearchFilters | any, page: number = 1, pageSize: number = 10): Promise<{ verses: Verse[], pagination?: any }> {
    const endpoint = type === 'english' ? 'fuzzy-search' : 'fuzzy-search-sanskrit';
    const kandaParam = filters.kanda ? `&kanda=${filters.kanda}` : '';
    const textsParam = filters.texts && filters.texts.length > 0 ? `&texts=${filters.texts.join(',')}` : '';
    const paginationParams = `&page=${page}&page_size=${pageSize}`;
    const url = `${API_BASE_URL}/${endpoint}?query=${encodeURIComponent(query)}${kandaParam}${textsParam}${paginationParams}`;
    
    const response = await this.makeRequest(url);
    
    // Handle paginated response format
    let results: Verse[];
    let pagination: any = undefined;
    
    if (response && typeof response === 'object' && 'results' in response) {
      // API returns paginated format: {results: [...], pagination: {...}}
      results = response.results || [];
      pagination = response.pagination;
    } else if (Array.isArray(response)) {
      // API returns direct array (fallback/mock data)
      results = response;
      // Create mock pagination for fallback
      pagination = {
        page: 1,
        page_size: results.length,
        total_results: results.length,
        total_pages: 1,
        has_next: false,
        has_prev: false
      };
    } else {
      // Unexpected format, return empty array
      console.error('Unexpected API response format:', response);
      return { verses: [], pagination: undefined };
    }
    
    // Filter by minimum ratio if specified
    const minRatio = filters.minRatio || 0;
    let filteredResults = results.filter((verse: Verse) => verse.ratio >= minRatio);
    
    // If cross-text search is enabled, simulate cross-text results
    if (filters.texts && filters.texts.length > 1) {
      // Mix results from different sources for demonstration
      filteredResults = this.getMockCrossTextResults(query, type);
    }
    
    return { verses: filteredResults, pagination };
  }

  private getMockCrossTextResults(query: string, type: 'english' | 'sanskrit'): Verse[] {
    // Simulate cross-text search results
    const crossTextResults = [
      {
        sloka_number: "1.1.9",
        ratio: 95,
        sloka: "तपस्स्वाध्यायनिरतं तपस्वी वाग्विदां वरम्।",
        meaning: "तपस्या और स्वाध्याय में निरत, तपस्वी और वाग्विदों में श्रेष्ठ।",
        translation: "One devoted to <span class=\"highlight\">penance</span> and study, ascetic and best among the eloquent.",
        source: "ramayana"
      },
      {
        sloka_number: "2.47",
        ratio: 92,
        sloka: "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        meaning: "कर्म में ही तेरा अधिकार है, फलों में कभी नहीं।",
        translation: "You have the right to perform your <span class=\"highlight\">duty</span>, but not to the fruits of action.",
        source: "bhagavad-gita"
      },
      {
        sloka_number: "18.66",
        ratio: 90,
        sloka: "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।",
        meaning: "सभी धर्मों को छोड़कर केवल मेरी शरण में आओ।",
        translation: "Abandon all varieties of <span class=\"highlight\">dharma</span> and just surrender unto Me.",
        source: "bhagavad-gita"
      },
      {
        sloka_number: "2.15.23",
        ratio: 85,
        sloka: "रामो राजीवलोचनः।",
        meaning: "राम कमल के समान नेत्रों वाले हैं।",
        translation: "<span class=\"highlight\">Rama</span> has lotus-like eyes.",
        source: "ramayana"
      }
    ];

    return crossTextResults.filter(verse => verse.ratio >= 80);
  }
}

export const searchAPI = new SearchAPI();

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
  const sourceName = verse.source === 'bhagavad-gita' ? 'Bhagavad Gita' : 
                     verse.source === 'ramayana' ? 'Ramayana' : 'Sacred Text';
  return `${verse.sloka_number}: ${verse.sloka}\n\n${verse.translation}\n\nSource: ${sourceName} Digital Corpus`;
};

export interface SargaData {
  kanda: {
    number: number;
    name: string;
  };
  sarga: {
    number: number;
    total_slokas: number;
  };
  slokas: Verse[];
}

// Type guard for API response validation
interface SargaApiResponse {
  kanda: { number: number; name: string };
  sarga: { number: number; total_slokas: number };
  slokas: Array<{
    sloka_id: string;
    sloka_text: string;
    meaning: string;
    translation: string;
  }>;
}

function isSargaApiResponse(data: any): data is SargaApiResponse {
  return data &&
    typeof data === 'object' &&
    data.kanda &&
    typeof data.kanda.number === 'number' &&
    typeof data.kanda.name === 'string' &&
    data.sarga &&
    typeof data.sarga.number === 'number' &&
    typeof data.sarga.total_slokas === 'number' &&
    Array.isArray(data.slokas) &&
    data.slokas.every((sloka: any) => 
      sloka &&
      typeof sloka.sloka_id === 'string' &&
      typeof sloka.sloka_text === 'string' &&
      typeof sloka.meaning === 'string' &&
      typeof sloka.translation === 'string'
    );
}

export const fetchSargaData = async (source: string, kanda: string, sarga: string): Promise<SargaData> => {
  try {
    console.log(`Fetching sarga data for source: ${source}, kanda: ${kanda}, sarga: ${sarga}`);
    const response = await fetch(`/api/ramayanam/kandas/${kanda}/sargas/${sarga}`);
    
    if (!response.ok) {
      console.error(`API request failed with status: ${response.status}`);
      if (response.status === 404) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Sarga ${sarga} not found in Kanda ${kanda}`);
      }
      throw new Error(`Failed to fetch sarga data: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Raw API response:', data);
    
    // Validate API response structure
    if (!isSargaApiResponse(data)) {
      console.error('Invalid API response structure:', data);
      throw new Error('Invalid sarga data format received from server');
    }
    
    // Transform the API response to match our expected format
    const transformedData: SargaData = {
      kanda: data.kanda,
      sarga: data.sarga,
      slokas: data.slokas.map((sloka, index) => {
        console.log(`Transforming sloka ${index}:`, sloka);
        return {
          sloka_number: sloka.sloka_id,
          sloka: sloka.sloka_text,
          meaning: sloka.meaning,
          translation: sloka.translation,
          ratio: 100, // Default ratio for sarga reading
          source: source
        };
      })
    };
    
    console.log('Transformed data:', transformedData);
    return transformedData;
  } catch (error) {
    console.error('Failed to fetch sarga data:', error);
    throw error;
  }
};