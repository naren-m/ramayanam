from rapidfuzz import fuzz
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
import time
from collections import OrderedDict
import weakref
import gc


class OptimizedFuzzySearchService:
    """
    Optimized FuzzySearchService using pre-built indices, parallel processing, 
    and caching for better performance.
    """

    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # Advanced caching with TTL, memory management, and statistics
        self._search_cache = OrderedDict()
        self._cache_timestamps = {}
        self._cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 600  # 10 minutes TTL for optimized service
        self._cache_max_size = 200  # Larger cache for optimized service
        self._cache_max_memory_mb = 50  # Memory limit in MB
        # Pre-build search indices for faster lookups
        self._build_search_indices()
        # Enhanced thread pool with dynamic scaling
        self._thread_pool = ThreadPoolExecutor(
            max_workers=min(8, (ThreadPoolExecutor()._max_workers or 1) * 2),
            thread_name_prefix="optimized-search"
        )
        # Performance metrics
        self._search_stats = {'total_searches': 0, 'avg_response_time': 0}

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
                    self._cache_stats['hits'] += 1
                    return self._search_cache[cache_key]
                else:
                    # Remove expired entry
                    del self._search_cache[cache_key]
                    del self._cache_timestamps[cache_key]
                    self._cache_stats['evictions'] += 1
            
            self._cache_stats['misses'] += 1
            return None
    
    def _cache_result(self, cache_key, result):
        """Cache search result with TTL, size, and memory limits."""
        with self._cache_lock:
            # Check memory usage and clean up if needed
            self._cleanup_cache_by_memory()
            
            # Remove oldest entries if cache is full
            while len(self._search_cache) >= self._cache_max_size:
                oldest_key = next(iter(self._search_cache))
                del self._search_cache[oldest_key]
                del self._cache_timestamps[oldest_key]
                self._cache_stats['evictions'] += 1
            
            # Add new entry
            self._search_cache[cache_key] = result
            self._cache_timestamps[cache_key] = time.time()
    
    def _cleanup_cache_by_memory(self):
        """Clean up cache based on memory usage."""
        try:
            # Estimate cache memory usage (rough approximation)
            cache_size_mb = len(str(self._search_cache)) / (1024 * 1024)
            
            if cache_size_mb > self._cache_max_memory_mb:
                # Remove 25% of oldest entries
                remove_count = max(1, len(self._search_cache) // 4)
                for _ in range(remove_count):
                    if self._search_cache:
                        oldest_key = next(iter(self._search_cache))
                        del self._search_cache[oldest_key]
                        del self._cache_timestamps[oldest_key]
                        self._cache_stats['evictions'] += 1
                
                # Force garbage collection
                gc.collect()
                
        except Exception as e:
            self.logger.warning(f"Error in cache memory cleanup: {e}")
    
    def get_cache_stats(self):
        """Get cache performance statistics."""
        with self._cache_lock:
            total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
            hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_size': len(self._search_cache),
                'hit_rate': round(hit_rate, 2),
                'total_hits': self._cache_stats['hits'],
                'total_misses': self._cache_stats['misses'],
                'total_evictions': self._cache_stats['evictions'],
                'search_stats': self._search_stats.copy()
            }

    def _build_search_indices(self):
        """Pre-build optimized search indices with streaming support."""
        self.logger.info("Building optimized search indices...")
        start_time = time.time()
        
        self.translation_index = []
        self.sanskrit_index = []
        # Add streaming-friendly sorted indices
        self.translation_sorted_by_ratio = []
        self.sanskrit_sorted_by_ratio = []
        
        sloka_count = 0
        processed_count = 0
        
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
                        
                        if sloka.translation:
                            translation_entry = sloka_ref.copy()
                            translation_entry['translation'] = sloka.translation.lower()
                            self.translation_index.append(translation_entry)
                        
                        if sloka.text and sloka.meaning:
                            sanskrit_entry = sloka_ref.copy()
                            sanskrit_entry['sloka_text'] = sloka.text.lower()
                            sanskrit_entry['meaning'] = sloka.meaning.lower()
                            self.sanskrit_index.append(sanskrit_entry)
                        
                        sloka_count += 1
                        processed_count += 1
                        
                        # Log progress for large datasets
                        if processed_count % 1000 == 0:
                            self.logger.debug(f"Processed {processed_count} slokas...")
        
        build_time = time.time() - start_time
        self.logger.info(f"Built optimized search indices in {build_time:.2f}s: "
                        f"{sloka_count} slokas, {len(self.translation_index)} translations, "
                        f"{len(self.sanskrit_index)} sanskrit entries")

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
        """Search a chunk of data in parallel with enhanced error handling."""
        results = []
        chunk_start_time = time.time()
        
        try:
            for item in chunk:
                try:
                    if search_field == 'translation':
                        text = item.get('translation', '')
                        if not text:
                            continue
                        
                        # Use rapidfuzz for faster fuzzy matching
                        ratio = fuzz.partial_ratio(text, query)
                        
                        if ratio > threshold:
                            highlighted_text = self.search_and_highlight(text, query)
                            results.append({
                                "sloka_number": item['sloka_id'],
                                "sloka": item['sloka_text'],
                                "translation": highlighted_text,
                                "meaning": item['meaning'],
                                "ratio": ratio,
                                "source": "ramayana",
                            })
                    
                    elif search_field in ['sloka_text', 'sanskrit']:
                        sloka_text = item.get('sloka_text', '')
                        meaning_text = item.get('meaning', '')
                        
                        if not sloka_text or not meaning_text:
                            continue
                        
                        # Check both sloka text and meaning
                        sloka_ratio = fuzz.partial_ratio(sloka_text, query)
                        meaning_ratio = fuzz.partial_ratio(meaning_text, query)
                        ratio = max(sloka_ratio, meaning_ratio)
                        
                        if ratio > threshold:
                            highlighted_text = self.search_and_highlight(sloka_text, query)
                            highlighted_meaning = self.search_and_highlight(meaning_text, query)
                            results.append({
                                "sloka_number": item['sloka_id'],
                                "sloka": highlighted_text,
                                "translation": item['translation'],
                                "meaning": highlighted_meaning,
                                "ratio": ratio,
                                "source": "ramayana",
                            })
                
                except Exception as e:
                    self.logger.warning(f"Error processing item {item.get('sloka_id', 'unknown')}: {e}")
                    continue
            
            chunk_time = time.time() - chunk_start_time
            self.logger.debug(f"Processed chunk of {len(chunk)} items in {chunk_time:.3f}s, found {len(results)} matches")
            
        except Exception as e:
            self.logger.error(f"Error in parallel search chunk: {e}")
        
        return results
    
    def search_stream(self, query, search_type='translation', threshold=70, batch_size=50):
        """Stream search results in batches for better user experience."""
        query = query.lower().strip()
        if not query:
            return
        
        start_time = time.time()
        self._search_stats['total_searches'] += 1
        
        try:
            # Choose the appropriate index
            index = self.translation_index if search_type == 'translation' else self.sanskrit_index
            search_field = 'translation' if search_type == 'translation' else 'sloka_text'
            
            # Process in batches and yield results
            batch_results = []
            total_processed = 0
            
            for i in range(0, len(index), batch_size):
                batch = index[i:i + batch_size]
                chunk_results = self._parallel_search_chunk(batch, query, threshold, search_field)
                
                # Sort current batch results
                chunk_results.sort(key=lambda x: x["ratio"], reverse=True)
                batch_results.extend(chunk_results)
                total_processed += len(batch)
                
                # Yield batch if we have enough results or processed all data
                if len(batch_results) >= batch_size or i + batch_size >= len(index):
                    if batch_results:
                        # Sort accumulated results and yield top results
                        batch_results.sort(key=lambda x: x["ratio"], reverse=True)
                        yield_count = min(batch_size, len(batch_results))
                        yield batch_results[:yield_count]
                        
                        # Keep remaining results for next iteration
                        batch_results = batch_results[yield_count:]
                
                # Progress logging
                if total_processed % 1000 == 0:
                    self.logger.debug(f"Streamed search progress: {total_processed}/{len(index)} processed")
            
            # Yield any remaining results
            if batch_results:
                batch_results.sort(key=lambda x: x["ratio"], reverse=True)
                yield batch_results
        
        except Exception as e:
            self.logger.error(f"Error in stream search: {e}")
        
        finally:
            # Update performance stats
            search_time = time.time() - start_time
            current_avg = self._search_stats['avg_response_time']
            total_searches = self._search_stats['total_searches']
            self._search_stats['avg_response_time'] = (
                (current_avg * (total_searches - 1) + search_time) / total_searches
            )

    def search_translation_fuzzy(self, query, max_results=1000):
        """
        Enhanced optimized search for fuzzy translations with streaming support.
        """
        query = query.lower().strip()
        if not query:
            return []
            
        start_time = time.time()
        cache_key = self._get_cache_key(query, 'translation')
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"Cache hit for translation search: {query}")
            return cached_result[:max_results]
        
        self.logger.info(f"Searching translations for query: {query}")
        
        # Quick exact match check first for better performance
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
        
        # Enhanced parallel processing with dynamic chunk sizing
        optimal_workers = min(8, max(2, len(self.translation_index) // 500))
        chunk_size = max(50, len(self.translation_index) // optimal_workers)
        chunks = [self.translation_index[i:i+chunk_size] for i in range(0, len(self.translation_index), chunk_size)]
        
        all_results = []
        futures = []
        
        # Submit all chunks for parallel processing
        for chunk in chunks:
            future = self._thread_pool.submit(self._parallel_search_chunk, chunk, query, 70, 'translation')
            futures.append(future)
        
        # Collect results with timeout handling
        for i, future in enumerate(futures):
            try:
                chunk_results = future.result(timeout=30)  # 30 second timeout per chunk
                all_results.extend(chunk_results)
            except Exception as e:
                self.logger.error(f"Error processing chunk {i}: {e}")
        
        # Sort by ratio and limit results
        all_results.sort(key=lambda x: x["ratio"], reverse=True)
        final_results = all_results[:max_results]
        
        # Cache the result
        self._cache_result(cache_key, final_results)
        
        search_time = time.time() - start_time
        self.logger.info(f"Translation search completed in {search_time:.3f}s, found {len(final_results)} results")
        
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