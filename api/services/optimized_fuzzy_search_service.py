from rapidfuzz import fuzz
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib


class OptimizedFuzzySearchService:
    """
    Optimized FuzzySearchService using pre-built indices, parallel processing, 
    and caching for better performance.
    """

    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # Simple cache for search results
        self._search_cache = {}
        self._cache_lock = threading.Lock()
        # Pre-build search indices for faster lookups
        self._build_search_indices()

    def _get_cache_key(self, query, search_type, kanda=None, threshold=70):
        """Generate a cache key for search results."""
        key_string = f"{search_type}:{query}:{kanda}:{threshold}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key):
        """Get cached search result if available."""
        with self._cache_lock:
            return self._search_cache.get(cache_key)
    
    def _cache_result(self, cache_key, result):
        """Cache search result with size limit."""
        with self._cache_lock:
            # Simple cache size management - keep only 50 most recent searches
            if len(self._search_cache) >= 50:
                # Remove oldest entry
                oldest_key = next(iter(self._search_cache))
                del self._search_cache[oldest_key]
            self._search_cache[cache_key] = result

    def _build_search_indices(self):
        """Pre-build search indices for faster lookups."""
        self.translation_index = []
        self.sanskrit_index = []
        
        for kanda_number, kanda in self.ramayanam_data.kandas.items():
            for sarga_number, sarga in kanda.sargas.items():
                for sloka_number, sloka in sarga.slokas.items():
                    if sloka and sloka.translation:
                        self.translation_index.append({
                            'sloka_id': sloka.id,
                            'sloka_text': sloka.text,
                            'translation': sloka.translation.lower(),
                            'meaning': sloka.meaning,
                            'kanda': kanda_number,
                            'sarga': sarga_number,
                            'sloka_num': sloka_number
                        })
                    
                    if sloka and sloka.text and sloka.meaning:
                        self.sanskrit_index.append({
                            'sloka_id': sloka.id,
                            'sloka_text': sloka.text.lower(),
                            'translation': sloka.translation,
                            'meaning': sloka.meaning.lower(),
                            'kanda': kanda_number,
                            'sarga': sarga_number,
                            'sloka_num': sloka_number
                        })
        
        self.logger.info(f"Built search indices: {len(self.translation_index)} translations, {len(self.sanskrit_index)} sanskrit entries")

    def tokenize(self, text):
        """Tokenizes the input text into a list of tokens."""
        tokens = re.split(r"\s+|\|\|?|\n", text)
        return [token for token in tokens if token]

    def search_and_highlight(self, text, query, threshold=0.7):
        """Searches for a query within a given text and highlights matching tokens."""
        tokens = self.tokenize(text)
        highlighted_tokens = []

        for token in tokens:
            if query.lower() == token.lower():
                highlighted_tokens.append('<span class="highlight">' + token + "</span>")
            elif fuzz.ratio(query.lower(), token.lower()) >= threshold * 100:
                highlighted_tokens.append('<span class="highlight">' + token + "</span>")
            else:
                highlighted_tokens.append(token)

        return " ".join(highlighted_tokens)

    def _parallel_search_chunk(self, chunk, query, threshold, search_field):
        """Search a chunk of data in parallel."""
        results = []
        for item in chunk:
            text = item[search_field]
            # Use rapidfuzz for faster fuzzy matching
            ratio = fuzz.partial_ratio(text, query)
            
            if ratio > threshold:
                if search_field == 'translation':
                    highlighted_text = self.search_and_highlight(text, query)
                    results.append({
                        "sloka_number": item['sloka_id'],
                        "sloka": item['sloka_text'],
                        "translation": highlighted_text,
                        "meaning": item['meaning'],
                        "ratio": ratio,
                    })
                else:  # Sanskrit search
                    highlighted_text = self.search_and_highlight(item['sloka_text'], query)
                    highlighted_meaning = self.search_and_highlight(item['meaning'], query)
                    results.append({
                        "sloka_number": item['sloka_id'],
                        "sloka": highlighted_text,
                        "translation": item['translation'],
                        "meaning": highlighted_meaning,
                        "ratio": ratio,
                    })
        return results

    def search_translation_fuzzy(self, query, max_results=1000):
        """
        Optimized search for fuzzy translations using pre-built indices and parallel processing.
        """
        query = query.lower()
        cache_key = self._get_cache_key(query, 'translation')
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for translation search: {query}")
            return cached_result[:max_results]
        
        self.logger.info(f"Searching translations for query: {query}")
        
        # Quick exact match check first
        exact_matches = [item for item in self.translation_index if query in item['translation']]
        if len(exact_matches) >= max_results:
            results = []
            for item in exact_matches[:max_results]:
                highlighted_text = self.search_and_highlight(item['translation'], query)
                results.append({
                    "sloka_number": item['sloka_id'],
                    "sloka": item['sloka_text'],
                    "translation": highlighted_text,
                    "meaning": item['meaning'],
                    "ratio": 100,  # Exact match
                })
            results.sort(key=lambda x: x["ratio"], reverse=True)
            self._cache_result(cache_key, results)
            return results
        
        # Use parallel processing for fuzzy search
        chunk_size = max(100, len(self.translation_index) // 4)
        chunks = [self.translation_index[i:i+chunk_size] for i in range(0, len(self.translation_index), chunk_size)]
        
        all_results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._parallel_search_chunk, chunk, query, 70, 'translation') for chunk in chunks]
            for future in futures:
                chunk_results = future.result()
                all_results.extend(chunk_results)
        
        # Sort by ratio and limit results
        all_results.sort(key=lambda x: x["ratio"], reverse=True)
        final_results = all_results[:max_results]
        
        # Cache the result
        self._cache_result(cache_key, final_results)
        return final_results

    def search_sloka_sanskrit_fuzzy(self, query, threshold=70, max_results=1000):
        """
        Optimized search for slokas in Sanskrit using pre-built indices and parallel processing.
        """
        query = query.lower()
        cache_key = self._get_cache_key(query, 'sanskrit', threshold=threshold)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for Sanskrit search: {query}")
            return cached_result[:max_results]
        
        self.logger.info(f"Searching Sanskrit for query: {query}")
        
        # Quick exact match check first
        exact_matches = [item for item in self.sanskrit_index 
                        if query in item['sloka_text'] or query in item['meaning']]
        if len(exact_matches) >= max_results:
            results = []
            for item in exact_matches[:max_results]:
                highlighted_text = self.search_and_highlight(item['sloka_text'], query)
                highlighted_meaning = self.search_and_highlight(item['meaning'], query)
                results.append({
                    "sloka_number": item['sloka_id'],
                    "sloka": highlighted_text,
                    "translation": item['translation'],
                    "meaning": highlighted_meaning,
                    "ratio": 100,  # Exact match
                })
            results.sort(key=lambda x: x["ratio"], reverse=True)
            self._cache_result(cache_key, results)
            return results
        
        # Use parallel processing for fuzzy search
        chunk_size = max(100, len(self.sanskrit_index) // 4)
        chunks = [self.sanskrit_index[i:i+chunk_size] for i in range(0, len(self.sanskrit_index), chunk_size)]
        
        all_results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._parallel_search_chunk, chunk, query, threshold, 'sloka_text') for chunk in chunks]
            for future in futures:
                chunk_results = future.result()
                all_results.extend(chunk_results)
        
        # Sort by ratio and limit results
        all_results.sort(key=lambda x: x["ratio"], reverse=True)
        final_results = all_results[:max_results]
        
        # Cache the result
        self._cache_result(cache_key, final_results)
        return final_results

    def search_translation_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """Search for translations in a specific Kanda using fuzzy matching."""
        query = query.lower()
        cache_key = self._get_cache_key(query, 'translation_kanda', kanda=kanda_number, threshold=threshold)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for Kanda {kanda_number} translation search: {query}")
            return cached_result
        
        # Filter by kanda and search
        kanda_items = [item for item in self.translation_index if item['kanda'] == kanda_number]
        
        results = []
        for item in kanda_items:
            ratio = fuzz.partial_ratio(item['translation'], query)
            if ratio > threshold:
                highlighted_text = self.search_and_highlight(item['translation'], query)
                results.append({
                    "sloka_number": item['sloka_id'],
                    "sloka": item['sloka_text'],
                    "translation": highlighted_text,
                    "meaning": item['meaning'],
                    "ratio": ratio,
                })
        
        results.sort(key=lambda x: x["ratio"], reverse=True)
        self._cache_result(cache_key, results)
        return results

    def search_sloka_sanskrit_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """Search for slokas in a specified kanda using fuzzy matching."""
        query = query.lower()
        cache_key = self._get_cache_key(query, 'sanskrit_kanda', kanda=kanda_number, threshold=threshold)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for Kanda {kanda_number} Sanskrit search: {query}")
            return cached_result
        
        # Filter by kanda and search
        kanda_items = [item for item in self.sanskrit_index if item['kanda'] == kanda_number]
        
        results = []
        for item in kanda_items:
            ratio = fuzz.partial_ratio(item['sloka_text'], query)
            if ratio > threshold:
                highlighted_text = self.search_and_highlight(item['sloka_text'], query)
                highlighted_meaning = self.search_and_highlight(item['meaning'], query)
                results.append({
                    "sloka_number": item['sloka_id'],
                    "sloka": highlighted_text,
                    "translation": item['translation'],
                    "meaning": highlighted_meaning,
                    "ratio": ratio,
                })
        
        results.sort(key=lambda x: x["ratio"], reverse=True)
        self._cache_result(cache_key, results)
        return results