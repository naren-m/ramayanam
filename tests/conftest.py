"""
Pytest configuration and fixtures for the Ramayanam application.
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.app import app as flask_app
from api.config import Config
from api.models.sloka_model import Sloka
from api.services.optimized_fuzzy_search_service import OptimizedFuzzySearchService


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary directory for test data
    test_data_dir = tempfile.mkdtemp()
    
    # Set test configuration
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATA_BASE_PATH': test_data_dir,
    })
    
    yield flask_app
    
    # Cleanup
    shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    """Create a test runner for the Flask application's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def mock_ramayanam_data():
    """Mock Ramayanam data structure for testing."""
    mock_data = MagicMock()
    
    # Mock kanda details
    mock_data.kandaDetails = {
        1: {"name": "BalaKanda"},
        2: {"name": "AyodhyaKanda"},
        3: {"name": "AranyaKanda"},
    }
    
    # Mock kandas structure
    mock_kanda = MagicMock()
    mock_sarga = MagicMock()
    mock_sloka = MagicMock()
    
    mock_sloka.id = "1.1.1"
    mock_sloka.text = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"
    mock_sloka.meaning = "धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले"
    mock_sloka.translation = "In the field of dharma, in Kurukshetra, those desirous of war"
    
    mock_sarga.slokas = {1: mock_sloka}
    mock_kanda.sargas = {1: mock_sarga}
    mock_data.kandas = {1: mock_kanda}
    
    return mock_data


@pytest.fixture
def sample_sloka():
    """Create a sample Sloka model for testing."""
    return Sloka(
        sloka_id="1.1.1",
        sloka_text="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
        meaning="धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले",
        translation="In the field of dharma, in Kurukshetra, those desirous of war"
    )


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "sloka_id": "1.1.1",
            "sloka_text": "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
            "meaning": "धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले",
            "translation": "In the field of dharma, in Kurukshetra, those desirous of war",
            "kanda": 1,
            "sarga": 1,
            "sloka": 1,
            "ratio": 95,
            "sloka_id": "1.1.1"
        },
        {
            "sloka_id": "1.1.2",
            "sloka_text": "मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय",
            "meaning": "मेरे और पाण्डवों ने क्या किया संजय",
            "translation": "What did my people and the Pandavas do, O Sanjaya",
            "kanda": 1,
            "sarga": 1,
            "sloka": 2,
            "ratio": 87,
            "sloka_id": "1.1.2"
        }
    ]


@pytest.fixture
def mock_fuzzy_search_service(mock_ramayanam_data, sample_search_results):
    """Mock fuzzy search service."""
    service = MagicMock(spec=OptimizedFuzzySearchService)
    service.search_translation_fuzzy.return_value = sample_search_results
    service.search_sloka_sanskrit_fuzzy.return_value = sample_search_results
    service.search_translation_in_kanda_fuzzy.return_value = sample_search_results[:1]
    service.search_sloka_sanskrit_in_kanda_fuzzy.return_value = sample_search_results[:1]
    return service


@pytest.fixture(autouse=True)
def mock_services(mock_ramayanam_data, mock_fuzzy_search_service):
    """Auto-use fixture to mock external services."""
    with patch('api.controllers.sloka_controller.ramayanam_data', mock_ramayanam_data), \
         patch('api.controllers.sloka_controller.fuzzy_search_service', mock_fuzzy_search_service):
        yield


@pytest.fixture
def api_headers():
    """Common API headers for testing."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def temp_data_files():
    """Create temporary data files for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample sloka files
    slokas_dir = os.path.join(temp_dir, 'slokas', 'Slokas', 'BalaKanda')
    os.makedirs(slokas_dir, exist_ok=True)
    
    # Sample sloka file
    with open(os.path.join(slokas_dir, 'BalaKanda_sarga_1_sloka.txt'), 'w', encoding='utf-8') as f:
        f.write("धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः\n")
        f.write("मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय\n")
    
    # Sample meaning file
    with open(os.path.join(slokas_dir, 'BalaKanda_sarga_1_meaning.txt'), 'w', encoding='utf-8') as f:
        f.write("धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले\n")
        f.write("मेरे और पाण्डवों ने क्या किया संजय\n")
    
    # Sample translation file
    with open(os.path.join(slokas_dir, 'BalaKanda_sarga_1_translation.txt'), 'w', encoding='utf-8') as f:
        f.write("In the field of dharma, in Kurukshetra, those desirous of war\n")
        f.write("What did my people and the Pandavas do, O Sanjaya\n")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = MagicMock()
    config.DEFAULT_FUZZY_THRESHOLD = 70
    config.DEFAULT_PAGE_SIZE = 10
    config.MAX_PAGE_SIZE = 50
    config.STREAM_BATCH_SIZE = 5
    config.SLOKAS_PATH = "/tmp/test/slokas"
    return config


# Parametrized fixtures for different test scenarios
@pytest.fixture(params=[
    ("hanuman", "english"),
    ("राम", "sanskrit"),
    ("sita", "english"),
    ("लक्ष्मण", "sanskrit")
])
def search_queries(request):
    """Parametrized search queries for testing."""
    query, search_type = request.param
    return {"query": query, "type": search_type}


@pytest.fixture(params=[1, 2, 3])
def kanda_numbers(request):
    """Parametrized kanda numbers for testing."""
    return request.param


@pytest.fixture(params=[70, 80, 90])
def threshold_values(request):
    """Parametrized threshold values for testing."""
    return request.param


# Custom markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "service: Service layer tests")
    config.addinivalue_line("markers", "model: Model tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_data: Tests that require real data files")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add markers based on test name patterns
        if "test_api" in item.name or "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "test_service" in item.name or "service" in str(item.fspath):
            item.add_marker(pytest.mark.service)
        elif "test_model" in item.name or "model" in str(item.fspath):
            item.add_marker(pytest.mark.model)


# Session-scoped error tracking
@pytest.fixture(scope='session', autouse=True)
def test_session_cleanup():
    """Session-wide cleanup and error tracking."""
    errors = []
    
    yield errors
    
    # Log any session-wide issues
    if errors:
        print(f"\nSession completed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")


# Helper functions available to all tests
@pytest.fixture
def assert_valid_sloka():
    """Helper function to validate sloka structure."""
    def _assert_valid_sloka(sloka_data):
        required_fields = ['sloka_id', 'sloka_text', 'meaning', 'translation']
        assert all(field in sloka_data for field in required_fields), \
            f"Missing required fields in sloka: {required_fields}"
        assert isinstance(sloka_data['sloka_id'], str), "sloka_id should be string"
        assert len(sloka_data['sloka_text']) > 0, "sloka_text should not be empty"
    
    return _assert_valid_sloka


@pytest.fixture
def assert_valid_search_response():
    """Helper function to validate search response structure."""
    def _assert_valid_search_response(response_data):
        assert 'results' in response_data, "Response should contain 'results'"
        assert 'pagination' in response_data, "Response should contain 'pagination'"
        assert isinstance(response_data['results'], list), "Results should be a list"
        
        pagination = response_data['pagination']
        required_pagination_fields = ['page', 'page_size', 'total_results', 'total_pages', 'has_next', 'has_prev']
        assert all(field in pagination for field in required_pagination_fields), \
            f"Missing pagination fields: {required_pagination_fields}"
    
    return _assert_valid_search_response