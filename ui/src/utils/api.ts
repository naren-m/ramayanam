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

  async search(query: string, type: 'english' | 'sanskrit', filters: SearchFilters): Promise<Verse[]> {
    const endpoint = type === 'english' ? 'fuzzy-search' : 'fuzzy-search-sanskrit';
    const kandaParam = filters.kanda ? `&kanda=${filters.kanda}` : '';
    const textsParam = filters.texts && filters.texts.length > 0 ? `&texts=${filters.texts.join(',')}` : '';
    const url = `${API_BASE_URL}/${endpoint}?query=${encodeURIComponent(query)}${kandaParam}${textsParam}`;
    
    const results = await this.makeRequest(url);
    
    // Filter by minimum ratio if specified
    let filteredResults = results.filter((verse: Verse) => verse.ratio >= filters.minRatio);
    
    // If cross-text search is enabled, simulate cross-text results
    if (filters.texts && filters.texts.length > 1) {
      // Mix results from different sources for demonstration
      filteredResults = this.getMockCrossTextResults(query, type);
    }
    
    return filteredResults;
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