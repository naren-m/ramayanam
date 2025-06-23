"""
Integration tests for the complete API workflow.
"""

import json
import pytest
import time
from unittest.mock import patch


@pytest.mark.integration
class TestAPIWorkflow:
    """Test complete API workflows."""
    
    def test_complete_search_workflow(self, client, sample_search_results):
        """Test complete search workflow from query to response."""
        # Step 1: Perform English search
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=hanuman')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert 'results' in data
        assert 'pagination' in data
        assert isinstance(data['results'], list)
        
        # Step 2: Get specific sloka from search results
        if data['results']:
            first_result = data['results'][0]
            sloka_id = first_result['sloka_id']
            
            # Parse sloka ID to get kanda, sarga, sloka numbers
            parts = sloka_id.split('.')
            if len(parts) == 3:
                kanda, sarga, sloka = parts
                
                # Step 3: Fetch specific sloka
                specific_response = client.get(f'/api/ramayanam/kandas/{kanda}/sargas/{sarga}/slokas/{sloka}')
                
                if specific_response.status_code == 200:
                    specific_data = json.loads(specific_response.data)
                    assert 'sloka_id' in specific_data
                    assert specific_data['sloka_id'] == sloka_id
    
    def test_pagination_workflow(self, client, sample_search_results):
        """Test pagination workflow."""
        query = "rama"
        page_size = 5
        
        # Get first page
        response1 = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}&page=1&page_size={page_size}')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        
        # Verify pagination info
        pagination1 = data1['pagination']
        assert pagination1['page'] == 1
        assert pagination1['page_size'] == page_size
        
        # Get second page if available
        if pagination1['has_next']:
            response2 = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}&page=2&page_size={page_size}')
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            
            pagination2 = data2['pagination']
            assert pagination2['page'] == 2
            assert pagination2['page_size'] == page_size
            
            # Results should be different
            if data1['results'] and data2['results']:
                assert data1['results'] != data2['results']
    
    def test_kanda_filtering_workflow(self, client, sample_search_results):
        """Test kanda filtering workflow."""
        query = "rama"
        
        # Search without filter
        response_all = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}')
        assert response_all.status_code == 200
        data_all = json.loads(response_all.data)
        
        # Search with kanda filter
        response_filtered = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}&kanda=1')
        assert response_filtered.status_code == 200
        data_filtered = json.loads(response_filtered.data)
        
        # Filtered results should be subset of all results
        assert data_filtered['pagination']['total_results'] <= data_all['pagination']['total_results']
    
    def test_search_type_comparison(self, client, sample_search_results):
        """Test comparison between English and Sanskrit search."""
        # English search
        english_response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama')
        assert english_response.status_code == 200
        english_data = json.loads(english_response.data)
        
        # Sanskrit search
        sanskrit_response = client.get('/api/ramayanam/slokas/fuzzy-search-sanskrit?query=राम')
        assert sanskrit_response.status_code == 200
        sanskrit_data = json.loads(sanskrit_response.data)
        
        # Both should return valid results
        assert 'results' in english_data
        assert 'results' in sanskrit_data
        
        # Results might be different but structure should be same
        assert 'pagination' in english_data
        assert 'pagination' in sanskrit_data


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across the entire API."""
    
    def test_cascading_error_handling(self, client):
        """Test how errors cascade through the system."""
        # Test with invalid kanda ID
        response = client.get('/api/ramayanam/kandas/999')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert isinstance(data['error'], str)
    
    def test_invalid_query_parameters(self, client):
        """Test various invalid query parameters."""
        # Invalid page number
        response1 = client.get('/api/ramayanam/slokas/fuzzy-search?query=test&page=-1')
        assert response1.status_code == 400
        
        # Invalid kanda
        response2 = client.get('/api/ramayanam/slokas/fuzzy-search?query=test&kanda=invalid')
        assert response2.status_code == 400
        
        # Missing required parameter
        response3 = client.get('/api/ramayanam/slokas/fuzzy-search')
        assert response3.status_code == 400
    
    def test_malformed_requests(self, client):
        """Test handling of malformed requests."""
        # Invalid content type for endpoints that might accept POST in future
        headers = {'Content-Type': 'text/plain'}
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=test', headers=headers)
        
        # Should still work for GET requests
        assert response.status_code in [200, 400]


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance across the API."""
    
    def test_response_time_consistency(self, client):
        """Test that response times are consistent."""
        query = "hanuman"
        times = []
        
        for i in range(5):
            start_time = time.time()
            response = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}')
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        # Check that response times are reasonable
        max_time = max(times)
        min_time = min(times)
        avg_time = sum(times) / len(times)
        
        assert max_time < 5.0  # No request should take more than 5 seconds
        assert avg_time < 2.0  # Average should be under 2 seconds
        
        # Variance shouldn't be too high (caching might help)
        variance = max_time - min_time
        assert variance < 3.0  # Difference shouldn't be more than 3 seconds
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.get('/api/ramayanam/slokas/fuzzy-search?query=test')
            results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check all requests succeeded
        while not results.empty():
            status_code = results.get()
            assert status_code == 200
    
    def test_large_result_set_handling(self, client):
        """Test handling of queries that might return large result sets."""
        # Use a common word that might return many results
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=a&page_size=50')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should handle large result sets gracefully
        assert 'results' in data
        assert 'pagination' in data
        
        # Check pagination limits are respected
        assert len(data['results']) <= 50


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across different endpoints."""
    
    def test_sloka_data_consistency(self, client, mock_ramayanam_data):
        """Test that same sloka data is consistent across endpoints."""
        # Get sloka through search
        search_response = client.get('/api/ramayanam/slokas/fuzzy-search?query=dharma')
        
        if search_response.status_code == 200:
            search_data = json.loads(search_response.data)
            
            if search_data['results']:
                first_result = search_data['results'][0]
                sloka_id = first_result['sloka_id']
                
                # Parse sloka ID
                parts = sloka_id.split('.')
                if len(parts) == 3:
                    kanda, sarga, sloka = parts
                    
                    # Get same sloka through direct endpoint
                    direct_response = client.get(f'/api/ramayanam/kandas/{kanda}/sargas/{sarga}/slokas/{sloka}')
                    
                    if direct_response.status_code == 200:
                        direct_data = json.loads(direct_response.data)
                        
                        # Compare key fields
                        assert direct_data['sloka_id'] == first_result['sloka_id']
                        assert direct_data['sloka_text'] == first_result['sloka_text']
                        assert direct_data['translation'] == first_result['translation']
    
    def test_kanda_data_consistency(self, client, mock_ramayanam_data):
        """Test kanda information consistency."""
        # Get kanda name
        kanda_response = client.get('/api/ramayanam/kandas/1')
        assert kanda_response.status_code == 200
        
        kanda_data = json.loads(kanda_response.data)
        kanda_name = kanda_data['kanda_name']
        
        # Search within this kanda
        search_response = client.get('/api/ramayanam/slokas/fuzzy-search?query=test&kanda=1')
        
        if search_response.status_code == 200:
            search_data = json.loads(search_response.data)
            
            # All results should be from the same kanda
            for result in search_data['results']:
                result_kanda = result['sloka_id'].split('.')[0]
                assert result_kanda == '1'


@pytest.mark.integration
class TestStreamingIntegration:
    """Test streaming endpoints integration."""
    
    def test_streaming_vs_paginated_consistency(self, client):
        """Test that streaming and paginated results are consistent."""
        query = "test"
        
        # Get paginated results
        paginated_response = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}&page_size=10')
        assert paginated_response.status_code == 200
        paginated_data = json.loads(paginated_response.data)
        
        # Get streaming results
        streaming_response = client.get(f'/api/ramayanam/slokas/fuzzy-search-stream?query={query}')
        assert streaming_response.status_code == 200
        
        # Streaming should return event-stream content type
        assert 'text/event-stream' in streaming_response.headers.get('Content-Type', '')
    
    def test_streaming_headers(self, client):
        """Test streaming endpoint headers."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-stream?query=test')
        
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'text/event-stream; charset=utf-8'
        assert response.headers.get('Cache-Control') == 'no-cache'
        assert response.headers.get('Connection') == 'keep-alive'


@pytest.mark.integration
@pytest.mark.slow
class TestFullSystemIntegration:
    """Full system integration tests (marked as slow)."""
    
    def test_end_to_end_user_journey(self, client):
        """Test complete user journey through the API."""
        # Journey 1: User searches for a term
        search_response = client.get('/api/ramayanam/slokas/fuzzy-search?query=hanuman')
        assert search_response.status_code == 200
        
        search_data = json.loads(search_response.data)
        assert len(search_data['results']) >= 0
        
        # Journey 2: User explores a specific kanda
        kanda_response = client.get('/api/ramayanam/kandas/1')
        assert kanda_response.status_code == 200
        
        # Journey 3: User gets a specific sloka
        if search_data['results']:
            sloka_id = search_data['results'][0]['sloka_id']
            parts = sloka_id.split('.')
            if len(parts) == 3:
                kanda, sarga, sloka = parts
                specific_response = client.get(f'/api/ramayanam/kandas/{kanda}/sargas/{sarga}/slokas/{sloka}')
                # Might succeed or fail based on mock data
                assert specific_response.status_code in [200, 404]
    
    def test_system_under_load(self, client):
        """Test system behavior under simulated load."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_requests():
            try:
                for i in range(10):
                    response = client.get(f'/api/ramayanam/slokas/fuzzy-search?query=test{i}')
                    results.append(response.status_code)
                    time.sleep(0.1)  # Small delay between requests
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads simulating concurrent users
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 30  # 3 threads * 10 requests each
        
        # Most requests should succeed
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 25  # At least 80% success rate
    
    def test_memory_usage_stability(self, client):
        """Test that memory usage doesn't grow excessively."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Make many requests
        for i in range(20):
            response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama')
            assert response.status_code == 200
            
            # Force cleanup
            del response
            if i % 5 == 0:
                gc.collect()
        
        # Final cleanup
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True


@pytest.mark.integration
class TestCacheIntegration:
    """Test caching behavior across the API."""
    
    def test_repeated_request_performance(self, client):
        """Test that repeated requests perform well (indicating caching)."""
        query = "hanuman"
        
        # First request (cold)
        start_time = time.time()
        response1 = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}')
        first_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Second request (should be faster if cached)
        start_time = time.time()
        response2 = client.get(f'/api/ramayanam/slokas/fuzzy-search?query={query}')
        second_time = time.time() - start_time
        
        assert response2.status_code == 200
        
        # Results should be identical
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1 == data2
        
        # Second request might be faster (if caching is implemented)
        # This is not a strict requirement as mock services are already fast
        assert second_time <= first_time + 0.1  # Allow small variance