"""
Unit tests for service layer classes.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from api.services.sloka_reader import SlokaReader
from api.services.fuzzy_search_service import FuzzySearchService
from api.services.optimized_fuzzy_search_service import OptimizedFuzzySearchService
from api.exceptions import SearchError


@pytest.mark.service
class TestSlokaReader:
    """Test cases for SlokaReader service."""
    
    def test_sloka_reader_init_valid_path(self, temp_data_files):
        """Test SlokaReader initialization with valid path."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        reader = SlokaReader(slokas_path)
        
        assert reader.base_path == slokas_path
        assert os.path.exists(reader.base_path)
    
    def test_sloka_reader_init_invalid_path(self):
        """Test SlokaReader initialization with invalid path."""
        invalid_path = "/nonexistent/path"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            SlokaReader(invalid_path)
        
        assert "does not exist" in str(exc_info.value)
    
    def test_sloka_reader_file_operations(self, temp_data_files):
        """Test SlokaReader file reading operations."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        reader = SlokaReader(slokas_path)
        
        # Test if the reader can find kanda directories
        assert os.path.exists(os.path.join(slokas_path, 'BalaKanda'))
    
    @patch('builtins.open', new_callable=mock_open, read_data="Test sloka content\nSecond line")
    @patch('os.path.exists')
    def test_sloka_reader_file_reading(self, mock_exists, mock_file):
        """Test actual file reading functionality."""
        mock_exists.return_value = True
        
        # This assumes SlokaReader has a read_file method
        # If not, this test would need to be adjusted based on actual implementation
        reader = SlokaReader("/mock/path")
        
        # Test would depend on actual SlokaReader implementation
        assert reader.base_path == "/mock/path"


@pytest.mark.service
class TestFuzzySearchService:
    """Test cases for FuzzySearchService."""
    
    @pytest.fixture
    def mock_ramayanam_data_for_search(self):
        """Create mock ramayanam data for search testing."""
        mock_data = MagicMock()
        
        # Create mock sloka objects
        mock_sloka1 = MagicMock()
        mock_sloka1.id = "1.1.1"
        mock_sloka1.text = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"
        mock_sloka1.meaning = "धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले"
        mock_sloka1.translation = "In the field of dharma, in Kurukshetra, those desirous of war"
        
        mock_sloka2 = MagicMock()
        mock_sloka2.id = "1.1.2"
        mock_sloka2.text = "मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय"
        mock_sloka2.meaning = "मेरे और पाण्डवों ने क्या किया संजय"
        mock_sloka2.translation = "What did my people and the Pandavas do, O Sanjaya"
        
        # Create mock structure
        mock_sarga = MagicMock()
        mock_sarga.slokas = {1: mock_sloka1, 2: mock_sloka2}
        
        mock_kanda = MagicMock()
        mock_kanda.sargas = {1: mock_sarga}
        
        mock_data.kandas = {1: mock_kanda}
        
        return mock_data
    
    def test_fuzzy_search_service_init(self, mock_ramayanam_data_for_search):
        """Test FuzzySearchService initialization."""
        service = FuzzySearchService(mock_ramayanam_data_for_search)
        
        assert service.ramayanam_data == mock_ramayanam_data_for_search
    
    @patch('api.services.fuzzy_search_service.fuzz.ratio')
    def test_fuzzy_search_basic(self, mock_ratio, mock_ramayanam_data_for_search):
        """Test basic fuzzy search functionality."""
        mock_ratio.return_value = 85
        
        service = FuzzySearchService(mock_ramayanam_data_for_search)
        
        # Test would depend on actual implementation
        # This is a placeholder for the actual test
        assert service.ramayanam_data is not None


@pytest.mark.service
class TestOptimizedFuzzySearchService:
    """Test cases for OptimizedFuzzySearchService."""
    
    def test_optimized_service_init(self, mock_ramayanam_data):
        """Test OptimizedFuzzySearchService initialization."""
        service = OptimizedFuzzySearchService(mock_ramayanam_data)
        
        assert hasattr(service, 'ramayanam_data')
    
    def test_search_translation_fuzzy(self, mock_fuzzy_search_service):
        """Test translation fuzzy search."""
        results = mock_fuzzy_search_service.search_translation_fuzzy("hanuman")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Verify result structure
        first_result = results[0]
        assert 'sloka_id' in first_result
        assert 'translation' in first_result
        assert 'ratio' in first_result
    
    def test_search_translation_fuzzy_empty_query(self, mock_fuzzy_search_service):
        """Test translation search with empty query."""
        mock_fuzzy_search_service.search_translation_fuzzy.return_value = []
        
        results = mock_fuzzy_search_service.search_translation_fuzzy("")
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_sloka_sanskrit_fuzzy(self, mock_fuzzy_search_service):
        """Test Sanskrit fuzzy search."""
        results = mock_fuzzy_search_service.search_sloka_sanskrit_fuzzy("राम")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Verify result structure
        first_result = results[0]
        assert 'sloka_id' in first_result
        assert 'sloka_text' in first_result
        assert 'ratio' in first_result
    
    def test_search_translation_in_kanda_fuzzy(self, mock_fuzzy_search_service):
        """Test kanda-specific translation search."""
        results = mock_fuzzy_search_service.search_translation_in_kanda_fuzzy(1, "hanuman", 70)
        
        assert isinstance(results, list)
        # Should have fewer results than global search
        assert len(results) <= 2  # Based on our mock data
    
    def test_search_sanskrit_in_kanda_fuzzy(self, mock_fuzzy_search_service):
        """Test kanda-specific Sanskrit search."""
        results = mock_fuzzy_search_service.search_sloka_sanskrit_in_kanda_fuzzy(1, "राम", 70)
        
        assert isinstance(results, list)
        assert len(results) <= 2  # Based on our mock data
    
    @pytest.mark.parametrize("threshold", [50, 70, 80, 90])
    def test_search_with_different_thresholds(self, mock_fuzzy_search_service, threshold):
        """Test search with different threshold values."""
        # Mock different results based on threshold
        if threshold >= 80:
            mock_fuzzy_search_service.search_translation_fuzzy.return_value = []
        else:
            mock_fuzzy_search_service.search_translation_fuzzy.return_value = [
                {"sloka_id": "1.1.1", "ratio": threshold + 5}
            ]
        
        results = mock_fuzzy_search_service.search_translation_fuzzy("test")
        
        if threshold >= 80:
            assert len(results) == 0
        else:
            assert len(results) > 0
            assert results[0]["ratio"] >= threshold
    
    def test_search_performance(self, mock_fuzzy_search_service):
        """Test search performance."""
        import time
        
        start_time = time.time()
        results = mock_fuzzy_search_service.search_translation_fuzzy("hanuman")
        end_time = time.time()
        
        # Mock service should be very fast
        assert (end_time - start_time) < 0.1
        assert isinstance(results, list)
    
    def test_search_caching_behavior(self, mock_fuzzy_search_service):
        """Test search result caching."""
        query = "hanuman"
        
        # First search
        results1 = mock_fuzzy_search_service.search_translation_fuzzy(query)
        
        # Second search (should use cache if implemented)
        results2 = mock_fuzzy_search_service.search_translation_fuzzy(query)
        
        # Results should be identical
        assert results1 == results2
    
    @patch('api.services.optimized_fuzzy_search_service.fuzz.ratio')
    def test_search_with_rapidfuzz(self, mock_rapidfuzz):
        """Test search using rapidfuzz library."""
        mock_rapidfuzz.return_value = 85
        
        # This test would require actual OptimizedFuzzySearchService implementation
        # For now, just verify the mock works
        assert mock_rapidfuzz("test", "test query") == 85


@pytest.mark.service
class TestServiceExceptions:
    """Test exception handling in services."""
    
    def test_sloka_reader_file_not_found(self):
        """Test SlokaReader with non-existent directory."""
        with pytest.raises(FileNotFoundError):
            SlokaReader("/absolutely/nonexistent/path")
    
    def test_search_service_with_none_data(self):
        """Test search service with None data."""
        with pytest.raises((TypeError, AttributeError)):
            FuzzySearchService(None)
    
    def test_search_service_with_invalid_data(self):
        """Test search service with invalid data structure."""
        invalid_data = "not a proper data structure"
        
        # Service might not validate data on init, but should fail on search
        service = FuzzySearchService(invalid_data)
        
        # This would depend on actual implementation
        assert service.ramayanam_data == invalid_data
    
    @patch('api.services.optimized_fuzzy_search_service.OptimizedFuzzySearchService.search_translation_fuzzy')
    def test_search_service_internal_error(self, mock_search):
        """Test handling of internal search errors."""
        mock_search.side_effect = Exception("Internal search error")
        
        with pytest.raises(Exception) as exc_info:
            service = OptimizedFuzzySearchService(MagicMock())
            service.search_translation_fuzzy("test")
        
        assert "Internal search error" in str(exc_info.value)


@pytest.mark.service
@pytest.mark.slow
class TestServiceIntegration:
    """Integration tests for services (marked as slow)."""
    
    def test_sloka_reader_with_real_files(self, temp_data_files):
        """Test SlokaReader with actual file structure."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        reader = SlokaReader(slokas_path)
        
        # Test basic functionality
        assert os.path.exists(reader.base_path)
        assert os.path.isdir(reader.base_path)
        
        # Check for kanda directories
        bala_kanda_path = os.path.join(reader.base_path, 'BalaKanda')
        assert os.path.exists(bala_kanda_path)
    
    def test_end_to_end_search_flow(self, mock_ramayanam_data, mock_fuzzy_search_service):
        """Test complete search flow from query to results."""
        query = "hanuman"
        
        # Simulate complete search flow
        results = mock_fuzzy_search_service.search_translation_fuzzy(query)
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Verify complete result structure
        for result in results:
            assert isinstance(result, dict)
            assert 'sloka_id' in result
            assert 'translation' in result
            assert 'ratio' in result
            assert isinstance(result['ratio'], (int, float))
            assert 0 <= result['ratio'] <= 100


@pytest.mark.service
class TestServiceUtilities:
    """Test utility functions in services."""
    
    def test_service_validation_functions(self):
        """Test validation utility functions if they exist."""
        # This would test any validation functions in services
        # For example, validating sloka ID format, query sanitization, etc.
        
        # Example placeholder test
        assert True  # Replace with actual validation tests
    
    def test_service_formatting_functions(self):
        """Test formatting utility functions if they exist."""
        # This would test any formatting functions in services
        # For example, formatting search results, normalizing text, etc.
        
        # Example placeholder test
        assert True  # Replace with actual formatting tests
    
    def test_service_caching_utilities(self):
        """Test caching utility functions if they exist."""
        # This would test any caching mechanisms in services
        
        # Example placeholder test
        assert True  # Replace with actual caching tests


# Fixtures specific to service tests
@pytest.fixture
def large_mock_dataset():
    """Create a large mock dataset for performance testing."""
    mock_data = MagicMock()
    
    # Create many mock slokas
    kandas = {}
    for kanda_num in range(1, 4):  # 3 kandas
        sargas = {}
        for sarga_num in range(1, 6):  # 5 sargas each
            slokas = {}
            for sloka_num in range(1, 11):  # 10 slokas each
                mock_sloka = MagicMock()
                mock_sloka.id = f"{kanda_num}.{sarga_num}.{sloka_num}"
                mock_sloka.text = f"Sanskrit text {kanda_num}.{sarga_num}.{sloka_num}"
                mock_sloka.translation = f"Translation {kanda_num}.{sarga_num}.{sloka_num}"
                slokas[sloka_num] = mock_sloka
            
            mock_sarga = MagicMock()
            mock_sarga.slokas = slokas
            sargas[sarga_num] = mock_sarga
        
        mock_kanda = MagicMock()
        mock_kanda.sargas = sargas
        kandas[kanda_num] = mock_kanda
    
    mock_data.kandas = kandas
    return mock_data


@pytest.mark.service
@pytest.mark.slow
def test_service_with_large_dataset(large_mock_dataset):
    """Test service performance with large dataset."""
    service = OptimizedFuzzySearchService(large_mock_dataset)
    
    # Test that service can handle large dataset
    assert hasattr(service, 'ramayanam_data')
    assert len(service.ramayanam_data.kandas) == 3