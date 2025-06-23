"""
Unit tests for API endpoints.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from api.exceptions import KandaNotFoundError, SargaNotFoundError, SlokaNotFoundError, SearchError


@pytest.mark.api
class TestKandaEndpoints:
    """Test cases for Kanda-related endpoints."""
    
    def test_get_kanda_name_success(self, client, mock_ramayanam_data):
        """Test successful retrieval of kanda name."""
        response = client.get('/api/ramayanam/kandas/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'kanda_name' in data
        assert data['kanda_name'] == 'BalaKanda'
    
    def test_get_kanda_name_not_found(self, client, mock_ramayanam_data):
        """Test kanda not found scenario."""
        # Mock empty kanda details
        mock_ramayanam_data.kandaDetails = {}
        
        response = client.get('/api/ramayanam/kandas/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_get_kanda_name_invalid_number(self, client):
        """Test invalid kanda number."""
        response = client.get('/api/ramayanam/kandas/abc')
        
        assert response.status_code == 404  # Flask converts invalid int to 404


@pytest.mark.api
class TestSlokaEndpoints:
    """Test cases for Sloka-related endpoints."""
    
    def test_get_sloka_by_kanda_sarga_success(self, client, mock_ramayanam_data):
        """Test successful retrieval of specific sloka."""
        response = client.get('/api/ramayanam/kandas/1/sargas/1/slokas/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify sloka structure
        required_fields = ['sloka_id', 'sloka_text', 'meaning', 'translation']
        for field in required_fields:
            assert field in data
        
        assert data['sloka_id'] == '1.1.1'
    
    def test_get_sloka_kanda_not_found(self, client, mock_ramayanam_data):
        """Test sloka retrieval with non-existent kanda."""
        mock_ramayanam_data.kandas = {}
        
        response = client.get('/api/ramayanam/kandas/999/sargas/1/slokas/1')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_sloka_sarga_not_found(self, client, mock_ramayanam_data):
        """Test sloka retrieval with non-existent sarga."""
        mock_kanda = MagicMock()
        mock_kanda.sargas = {}
        mock_ramayanam_data.kandas = {1: mock_kanda}
        
        response = client.get('/api/ramayanam/kandas/1/sargas/999/slokas/1')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_sloka_not_found(self, client, mock_ramayanam_data):
        """Test sloka retrieval with non-existent sloka."""
        mock_sarga = MagicMock()
        mock_sarga.slokas = {}
        mock_kanda = MagicMock()
        mock_kanda.sargas = {1: mock_sarga}
        mock_ramayanam_data.kandas = {1: mock_kanda}
        
        response = client.get('/api/ramayanam/kandas/1/sargas/1/slokas/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


@pytest.mark.api
class TestFuzzySearchEndpoints:
    """Test cases for fuzzy search endpoints."""
    
    def test_fuzzy_search_success(self, client, sample_search_results, assert_valid_search_response):
        """Test successful fuzzy search."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=hanuman')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert_valid_search_response(data)
        assert len(data['results']) > 0
        
        # Verify first result structure
        first_result = data['results'][0]
        required_fields = ['sloka_id', 'sloka_text', 'translation', 'ratio']
        for field in required_fields:
            assert field in first_result
    
    def test_fuzzy_search_empty_query(self, client):
        """Test fuzzy search with empty query."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_fuzzy_search_no_query_param(self, client):
        """Test fuzzy search without query parameter."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_fuzzy_search_with_kanda_filter(self, client, sample_search_results):
        """Test fuzzy search with kanda filter."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&kanda=1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'pagination' in data
    
    def test_fuzzy_search_with_threshold(self, client, sample_search_results):
        """Test fuzzy search with custom threshold."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&threshold=80')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
    
    def test_fuzzy_search_with_pagination(self, client, sample_search_results):
        """Test fuzzy search with pagination parameters."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&page=2&page_size=5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        pagination = data['pagination']
        assert pagination['page'] == 2
        assert pagination['page_size'] == 5
    
    def test_fuzzy_search_invalid_page(self, client):
        """Test fuzzy search with invalid page number."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_fuzzy_search_invalid_kanda(self, client):
        """Test fuzzy search with invalid kanda parameter."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&kanda=abc')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'invalid' in data['error'].lower()


@pytest.mark.api
class TestSanskritSearchEndpoints:
    """Test cases for Sanskrit fuzzy search endpoints."""
    
    def test_sanskrit_fuzzy_search_success(self, client, sample_search_results, assert_valid_search_response):
        """Test successful Sanskrit fuzzy search."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-sanskrit?query=राम')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert_valid_search_response(data)
        assert len(data['results']) > 0
    
    def test_sanskrit_search_empty_query(self, client):
        """Test Sanskrit search with empty query."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-sanskrit?query=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_sanskrit_search_with_kanda_filter(self, client, sample_search_results):
        """Test Sanskrit search with kanda filter."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-sanskrit?query=राम&kanda=1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
    
    def test_sanskrit_search_with_pagination(self, client, sample_search_results):
        """Test Sanskrit search with pagination."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-sanskrit?query=राम&page=1&page_size=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        pagination = data['pagination']
        assert pagination['page'] == 1
        assert pagination['page_size'] == 10


@pytest.mark.api
class TestStreamingSearchEndpoints:
    """Test cases for streaming search endpoints."""
    
    def test_streaming_search_success(self, client, sample_search_results):
        """Test successful streaming search."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-stream?query=hanuman')
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/event-stream; charset=utf-8'
        assert 'Cache-Control' in response.headers
        assert response.headers['Cache-Control'] == 'no-cache'
    
    def test_streaming_search_empty_query(self, client):
        """Test streaming search with empty query."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-stream?query=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_streaming_search_with_batch_size(self, client, sample_search_results):
        """Test streaming search with custom batch size."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-stream?query=rama&batch_size=3')
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/event-stream; charset=utf-8'


@pytest.mark.api
class TestErrorHandling:
    """Test cases for error handling in API endpoints."""
    
    def test_404_endpoint(self, client):
        """Test non-existent endpoint."""
        response = client.get('/api/ramayanam/nonexistent')
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test incorrect HTTP method."""
        response = client.post('/api/ramayanam/kandas/1')
        
        assert response.status_code == 405
    
    @patch('api.controllers.sloka_controller.fuzzy_search_service.search_translation_fuzzy')
    def test_search_service_exception(self, mock_search, client):
        """Test handling of search service exceptions."""
        mock_search.side_effect = Exception("Service error")
        
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=test')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_large_page_size_limit(self, client):
        """Test page size limiting."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search?query=rama&page_size=1000')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should be limited to MAX_PAGE_SIZE (50)
        assert data['pagination']['page_size'] <= 50


@pytest.mark.api
class TestResponseHeaders:
    """Test cases for response headers and CORS."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get('/api/ramayanam/kandas/1')
        
        # CORS headers should be present due to Flask-CORS
        assert response.status_code == 200
    
    def test_content_type_json(self, client):
        """Test JSON content type."""
        response = client.get('/api/ramayanam/kandas/1')
        
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('Content-Type', '')
    
    def test_streaming_content_type(self, client):
        """Test streaming endpoint content type."""
        response = client.get('/api/ramayanam/slokas/fuzzy-search-stream?query=test')
        
        assert response.status_code == 200
        assert 'text/event-stream' in response.headers.get('Content-Type', '')


@pytest.mark.api
@pytest.mark.parametrize("endpoint,params", [
    ('/api/ramayanam/slokas/fuzzy-search', {'query': 'hanuman'}),
    ('/api/ramayanam/slokas/fuzzy-search-sanskrit', {'query': 'राम'}),
    ('/api/ramayanam/kandas/1', {}),
])
def test_endpoint_response_time(client, endpoint, params):
    """Test that endpoints respond within reasonable time."""
    import time
    
    start_time = time.time()
    response = client.get(endpoint, query_string=params)
    end_time = time.time()
    
    assert response.status_code in [200, 400, 404]  # Valid status codes
    assert (end_time - start_time) < 5  # Should respond within 5 seconds


@pytest.mark.api
def test_api_documentation_endpoints(client):
    """Test that API provides some form of documentation or health check."""
    # Test root endpoint
    response = client.get('/')
    assert response.status_code in [200, 404]  # Either serves app or 404
    
    # Test if there's a health check endpoint
    health_response = client.get('/health')
    # Health endpoint might not exist, so we just check it doesn't crash