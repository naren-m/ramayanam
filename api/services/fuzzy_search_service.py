from fuzzywuzzy import fuzz
from rapidfuzz import fuzz as rapid_fuzz
from rapidfuzz import utils as rapid_utils

# fuzzy_search_service.py
import logging
from difflib import SequenceMatcher
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
from functools import lru_cache
import time
from collections import defaultdict, OrderedDict
import weakref


class FuzzySearchService:
    """
    FuzzySearchService is a class that provides methods for performing fuzzy searches
    on the Ramayanam data, allowing for similarity matching of translations and slokas.

    Attributes:
        ramayanam_data (object): An object containing the Ramayanam data structured
        into Kandas, Sargas, and Slokas.
        logger (Logger): A logger instance for logging information and errors.

    Methods:
        __init__(ramayanam_data): Initializes the FuzzySearchService with the provided
        Ramayanam data and sets up the logger.

        tokenize(text): Splits the input text into tokens based on spaces, pipes,
        and newlines.

        similarity(a, b): Computes the similarity ratio between two strings using
        the SequenceMatcher.

        search_and_highlight(text, query, threshold=0.7): Searches for the query
        in the provided text and highlights matching tokens based on the similarity
        threshold.

        search_translation_fuzzy(query): Searches for translations across all Kandas
        using fuzzy matching and returns a list of results.

        search_translation_in_kanda_fuzzy(kanda_number, query, threshold=70):
        Searches for translations in a specific Kanda using fuzzy matching, returning
        a list of matching slokas with details.

        search_sloka_sanskrit_fuzzy(query, threshold=70): Searches for slokas in
        Sanskrit using fuzzy matching and returns a list of results.

        search_sloka_sanskrit_in_kanda_fuzzy(kanda_number, query, threshold=70):
        Searches for slokas in a specified Kanda using fuzzy matching, returning
        a list of matched slokas with details.
    """

    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # Advanced caching with TTL and memory management
        self._search_cache = OrderedDict()
        self._cache_timestamps = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 300  # 5 minutes TTL
        self._cache_max_size = 100
        # Pre-build search indices for faster lookups
        self._build_search_indices()
        # Thread pool for parallel processing
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="fuzzy-search")
    
    def _build_search_indices(self):
        """Build inverted indices for faster lookups."""
        self.logger.info("Building search indices...")
        start_time = time.time()
        
        # Inverted index for translations: word -> list of sloka references
        self.translation_word_index = defaultdict(list)
        # Inverted index for Sanskrit text: word -> list of sloka references  
        self.sanskrit_word_index = defaultdict(list)
        # Full text index for quick lookups
        self.translation_index = []
        self.sanskrit_index = []
        
        # Validate data structure
        if self.ramayanam_data is None:
            raise TypeError("ramayanam_data cannot be None")
        if not hasattr(self.ramayanam_data, 'kandas'):
            self.logger.warning("Invalid ramayanam_data structure - no 'kandas' attribute")
            return
        
        sloka_count = 0
        for kanda_number, kanda in self.ramayanam_data.kandas.items():
            for sarga_number, sarga in kanda.sargas.items():
                for sloka_number, sloka in sarga.slokas.items():
                    if sloka:
                        sloka_ref = {
                            'sloka_id': sloka.id,
                            'sloka_text': sloka.text,
                            'translation': sloka.translation,
                            'meaning': sloka.meaning,
                            'kanda': kanda_number,
                            'sarga': sarga_number,
                            'sloka_num': sloka_number
                        }
                        
                        # Build translation indices
                        if sloka.translation:
                            words = self._extract_words(sloka.translation.lower())
                            for word in words:
                                self.translation_word_index[word].append(sloka_ref)
                            self.translation_index.append(sloka_ref)
                        
                        # Build Sanskrit indices
                        if sloka.text and sloka.meaning:
                            # Index both Sanskrit text and meaning
                            sanskrit_words = self._extract_words(sloka.text.lower())
                            meaning_words = self._extract_words(sloka.meaning.lower())
                            all_words = set(sanskrit_words + meaning_words)
                            
                            for word in all_words:
                                self.sanskrit_word_index[word].append(sloka_ref)
                            self.sanskrit_index.append(sloka_ref)
                        
                        sloka_count += 1
        
        build_time = time.time() - start_time
        self.logger.info(f"Built search indices in {build_time:.2f}s: {sloka_count} slokas, "
                        f"{len(self.translation_word_index)} translation words, "
                        f"{len(self.sanskrit_word_index)} Sanskrit words")
    
    def _extract_words(self, text):
        """Extract meaningful words from text for indexing."""
        if not text:
            return []
        # Split on various delimiters and filter short words
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return [word for word in words if len(word) >= 3]

    def _get_cache_key(self, query, search_type, kanda=None, threshold=70):
        """Generate a cache key for search results."""
        key_string = f"{search_type}:{query}:{kanda}:{threshold}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key):
        """Get cached search result if available and not expired."""
        with self._cache_lock:
            if cache_key in self._search_cache:
                timestamp = self._cache_timestamps.get(cache_key, 0)
                if time.time() - timestamp < self._cache_ttl:
                    # Move to end (mark as recently used)
                    self._search_cache.move_to_end(cache_key)
                    return self._search_cache[cache_key]
                else:
                    # Remove expired entry
                    del self._search_cache[cache_key]
                    del self._cache_timestamps[cache_key]
            return None
    
    def _cache_result(self, cache_key, result):
        """Cache search result with TTL and size limits."""
        with self._cache_lock:
            # Remove oldest entries if cache is full
            while len(self._search_cache) >= self._cache_max_size:
                oldest_key = next(iter(self._search_cache))
                del self._search_cache[oldest_key]
                del self._cache_timestamps[oldest_key]
            
            # Add new entry
            self._search_cache[cache_key] = result
            self._cache_timestamps[cache_key] = time.time()
    
    def _cleanup_expired_cache(self):
        """Remove expired cache entries."""
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                key for key, timestamp in self._cache_timestamps.items()
                if current_time - timestamp >= self._cache_ttl
            ]
            for key in expired_keys:
                del self._search_cache[key]
                del self._cache_timestamps[key]

    def tokenize(self, text):
        """
        Tokenizes the input text into a list of tokens.

        This method splits the input text based on spaces, single pipes ('|'), 
        double pipes ('||'), and newline characters. It returns a list of non-empty 
        tokens.

        Parameters:
            text (str): The input string to be tokenized.

        Returns:
            List[str]: A list of tokens extracted from the input text.
        """
        # Splitting based on spaces, |, and ||
        tokens = re.split(r"\s+|\|\|?|\n", text)
        return [token for token in tokens if token]

    def similarity(self, a, b):
        """
        Calculates the similarity ratio between two strings using the SequenceMatcher.

        Args:
            a (str): The first string to compare.
            b (str): The second string to compare.

        Returns:
            float: A float value representing the similarity ratio between the two strings,
                   ranging from 0.0 (no similarity) to 1.0 (identical strings).
        """
        # Using SequenceMatcher to get similarity ratio
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def search_and_highlight(self, text, query, threshold=0.7):
        """
        Searches for a query within a given text and highlights matching tokens.

        Parameters:
            text (str): The text in which to search for the query.
            query (str): The query string to search for in the text.
            threshold (float, optional): The similarity threshold for highlighting. 
                                          Defaults to 0.7.

        Returns:
            str: The text with matching tokens highlighted using HTML span elements.
        """
        tokens = self.tokenize(text)
        highlighted_tokens = []

        for _, token in enumerate(tokens):
            if query.lower() == token.lower():
                highlighted_tokens.append(
                    '<span class="highlight">' + token + "</span>"
                )
            elif self.similarity(query, token) >= threshold:
                highlighted_tokens.append(
                    '<span class="highlight">' + token + "</span>"
                )
            else:
                highlighted_tokens.append(token)

        # Joining tokens to recreate sentences/phrases for output
        highlighted_text = " ".join(highlighted_tokens)
        return highlighted_text

    def search_translation_fuzzy(self, query, max_results=1000):
        """
        Search for fuzzy translations using inverted indices and caching.

        Parameters:
            query (str): The search term to find translations for.
            max_results (int): Maximum number of results to return.

        Returns:
            list: A list of results containing fuzzy matches for the provided query.
        """
        query = query.lower().strip()
        if not query:
            return []
            
        cache_key = self._get_cache_key(query, 'translation_all')
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for translation search: {query}")
            return cached_result[:max_results]
        
        self.logger.info(f"Searching translations for query: {query}")
        
        # Use inverted index for fast candidate retrieval
        candidates = self._get_translation_candidates(query)
        
        if not candidates:
            # Fallback to full search if no candidates found
            candidates = self.translation_index
        
        # Perform parallel fuzzy matching on candidates
        results = self._parallel_fuzzy_search(candidates, query, 'translation', threshold=70)
        
        # Sort by ratio and limit results
        results.sort(key=lambda x: x["ratio"], reverse=True)
        final_results = results[:max_results]
        
        # Cache the result
        self._cache_result(cache_key, final_results)
        return final_results
    
    def _get_translation_candidates(self, query):
        """Get candidate slokas using inverted index."""
        query_words = self._extract_words(query)
        if not query_words:
            return []
        
        # Find slokas that contain any of the query words
        candidate_refs = set()
        for word in query_words:
            if word in self.translation_word_index:
                candidate_refs.update(self.translation_word_index[word])
        
        # Convert to list and deduplicate
        candidates = list({ref['sloka_id']: ref for ref in candidate_refs}.values())
        
        self.logger.debug(f"Found {len(candidates)} candidates for query words: {query_words}")
        return candidates
    
    def _parallel_fuzzy_search(self, candidates, query, search_type, threshold=70):
        """Perform parallel fuzzy search on candidates."""
        if not candidates:
            return []
        
        # Split candidates into chunks for parallel processing
        chunk_size = max(50, len(candidates) // 4)
        chunks = [candidates[i:i+chunk_size] for i in range(0, len(candidates), chunk_size)]
        
        all_results = []
        futures = []
        
        for chunk in chunks:
            future = self._thread_pool.submit(self._search_chunk, chunk, query, search_type, threshold)
            futures.append(future)
        
        for future in futures:
            try:
                chunk_results = future.result(timeout=30)  # 30 second timeout
                all_results.extend(chunk_results)
            except Exception as e:
                self.logger.error(f"Error in parallel search: {e}")
        
        return all_results
    
    def _search_chunk(self, chunk, query, search_type, threshold):
        """Search a chunk of candidates."""
        results = []
        
        for item in chunk:
            try:
                if search_type == 'translation':
                    if not item.get('translation'):
                        continue
                    text = item['translation'].lower()
                    ratio = rapid_fuzz.partial_ratio(text, query)
                    
                    if ratio > threshold:
                        highlighted_text = self.search_and_highlight(text, query)
                        results.append({
                            "sloka_number": item['sloka_id'],
                            "sloka": item['sloka_text'],
                            "translation": highlighted_text,
                            "meaning": item['meaning'],
                            "ratio": ratio,
                        })
                        
                elif search_type == 'sanskrit':
                    if not item.get('sloka_text') or not item.get('meaning'):
                        continue
                    text = item['sloka_text'].lower()
                    meaning = item['meaning'].lower()
                    
                    text_ratio = rapid_fuzz.partial_ratio(text, query)
                    meaning_ratio = rapid_fuzz.partial_ratio(meaning, query)
                    ratio = max(text_ratio, meaning_ratio)
                    
                    if ratio > threshold:
                        highlighted_text = self.search_and_highlight(text, query)
                        highlighted_meaning = self.search_and_highlight(meaning, query)
                        results.append({
                            "sloka_number": item['sloka_id'],
                            "sloka": highlighted_text,
                            "translation": item['translation'],
                            "meaning": highlighted_meaning,
                            "ratio": ratio,
                        })
            except Exception as e:
                self.logger.error(f"Error processing item {item.get('sloka_id', 'unknown')}: {e}")
                continue
        
        return results

    def search_translation_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """
        Searches for translations in a specific Kanda of the Ramayanam using fuzzy matching.

        Parameters:
            kanda_number (int): The number of the Kanda to search within.
            query (str): The search query to match against the translations.
            threshold (int, optional): The minimum similarity ratio for a match to be considered valid. Defaults to 70.

        Returns:
            list: A list of dictionaries containing details of matching slokas, including:
                - sloka_number (int): The ID of the sloka.
                - sloka (str): The text of the sloka.
                - translation (str): The highlighted translation of the sloka.
                - meaning (str): The meaning of the sloka.
                - ratio (int): The similarity ratio of the translation to the query.
        """
        kanda = self.ramayanam_data.kandas.get(kanda_number)
        results = []
        if not kanda:
            self.logger.error("Kanda '%s' not found", kanda_number)
            return results
        for sarga_number, sarga in kanda.sargas.items():
            if not sarga:
                self.logger.error(
                    "Sarga '%s' not found for Kanda '%s'", sarga_number, kanda_number
                )
                continue

            for sloka_number, sloka in sarga.slokas.items():
                if sloka is None or sloka.translation is None:
                    self.logger.debug(
                        "Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka
                    )
                    continue
                text = sloka.translation.lower()  # Convert sloka text to lowercase
                highlighted_text = self.search_and_highlight(text, query)

                ratio = rapid_fuzz.partial_ratio(text, query)
                self.logger.debug(
                    "Checking sloka %s.%s.%s - Ratio: %s",
                    kanda_number,
                    sarga_number,
                    sloka_number,
                    ratio,
                )
                if ratio > threshold:  # Adjust the threshold as needed
                    results.append(
                        {
                            "sloka_number": sloka.id,
                            "sloka": sloka.text,
                            "translation": highlighted_text,
                            "meaning": sloka.meaning,
                            "ratio": ratio,
                        }
                    )

        results.sort(key=lambda x: x["ratio"], reverse=True)
        return results

    def search_sloka_sanskrit_fuzzy(self, query, threshold=70, max_results=1000):
        """
        Search for slokas in Sanskrit using inverted indices and parallel processing.

        Parameters:
            query (str): The search query in Sanskrit to be matched.
            threshold (int, optional): The minimum similarity threshold for fuzzy matching. Defaults to 70.
            max_results (int): Maximum number of results to return.

        Returns:
            list: A list of slokas that match the query based on the fuzzy search criteria.
        """
        query = query.lower().strip()
        if not query:
            return []
            
        cache_key = self._get_cache_key(query, 'sanskrit_all', threshold=threshold)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for Sanskrit search: {query}")
            return cached_result[:max_results]
            
        self.logger.info(f"Searching Sanskrit for query: {query}")
        
        # Use inverted index for fast candidate retrieval
        candidates = self._get_sanskrit_candidates(query)
        
        if not candidates:
            # Fallback to full search if no candidates found
            candidates = self.sanskrit_index
        
        # Perform parallel fuzzy matching on candidates
        results = self._parallel_fuzzy_search(candidates, query, 'sanskrit', threshold=threshold)
        
        # Sort by ratio and limit results
        results.sort(key=lambda x: x["ratio"], reverse=True)
        final_results = results[:max_results]
        
        # Cache the result
        self._cache_result(cache_key, final_results)
        return final_results
    
    def _get_sanskrit_candidates(self, query):
        """Get candidate slokas for Sanskrit search using inverted index."""
        query_words = self._extract_words(query)
        if not query_words:
            return []
        
        # Find slokas that contain any of the query words
        candidate_refs = set()
        for word in query_words:
            if word in self.sanskrit_word_index:
                candidate_refs.update(self.sanskrit_word_index[word])
        
        # Convert to list and deduplicate
        candidates = list({ref['sloka_id']: ref for ref in candidate_refs}.values())
        
        self.logger.debug(f"Found {len(candidates)} Sanskrit candidates for query words: {query_words}")
        return candidates

    def search_sloka_sanskrit_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """
        Search for slokas in a specified kanda using a fuzzy matching algorithm.

        Parameters:
            kanda_number (int): The number of the kanda to search within.
            query (str): The search term to match against sloka text and meaning.
            threshold (int, optional): The minimum similarity ratio (default is 70) for a match to be considered valid.

        Returns:
            list: A list of dictionaries containing the matched slokas, each with the following keys:
                - sloka_number (int): The ID of the sloka.
                - sloka (str): The text of the sloka with highlighted matches.
                - translation (str): The translation of the sloka.
                - meaning (str): The meaning of the sloka with highlighted matches.
                - ratio (int): The similarity ratio of the match.

        Logs:
            Errors if the specified kanda or sarga is not found.
            Debug information about the matching process and ratios.
        """
        results = []
        kanda = self.ramayanam_data.kandas.get(kanda_number)
        if not kanda:
            self.logger.error("Kanda '%s' not found", kanda_number)
            return results
        for sarga_number, sarga in kanda.sargas.items():
            if not sarga:
                self.logger.error(
                    "Sarga '%s' not found for Kanda '%s'", sarga_number, kanda_number
                )
                continue

            for sloka_number, sloka in sarga.slokas.items():
                if sloka is None or sloka.text is None or sloka.meaning is None:
                    self.logger.debug(
                        "Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka
                    )
                    continue
                text = sloka.text.lower()  # Convert sloka text to lowercase
                highlighted_text = self.search_and_highlight(text, query)
                highlighted_meaning = self.search_and_highlight(
                    sloka.meaning.lower(), query
                )

                ratio = rapid_fuzz.partial_ratio(text, query)
                self.logger.debug(
                    "Checking sloka %s.%s.%s - Ratio: %s",
                    kanda_number,
                    sarga_number,
                    sloka_number,
                    ratio,
                )
                if ratio > threshold:  # Adjust the threshold as needed
                    results.append(
                        {
                            "sloka_number": sloka.id,
                            "sloka": highlighted_text,
                            "translation": sloka.translation,
                            "meaning": highlighted_meaning,
                            "ratio": ratio,
                        }
                    )

        results.sort(key=lambda x: x["ratio"], reverse=True)
        return results
