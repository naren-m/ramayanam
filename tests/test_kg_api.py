#!/usr/bin/env python3
"""
Knowledge Graph API Test Suite

Automated tests for all knowledge graph endpoints including:
- Statistics endpoint
- Entity search
- Entity retrieval
- Entity filtering
- Data validation
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration: float

class KnowledgeGraphAPITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record the result"""
        self.log(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            test_func()
            duration = time.time() - start_time
            result = TestResult(test_name, True, "✅ PASSED", duration)
            self.log(f"✅ {test_name} PASSED ({duration:.3f}s)")
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, f"❌ FAILED: {str(e)}", duration)
            self.log(f"❌ {test_name} FAILED: {str(e)}", "ERROR")
        
        self.results.append(result)
        return result.passed
    
    def test_api_health(self):
        """Test basic API connectivity"""
        response = requests.get(f"{self.base_url}/api/kg/statistics", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('success') is True, "API returned success=false"
        assert 'statistics' in data, "Missing statistics in response"
    
    def test_statistics_endpoint(self):
        """Test /api/kg/statistics endpoint"""
        response = requests.get(f"{self.base_url}/api/kg/statistics")
        assert response.status_code == 200
        
        data = response.json()
        stats = data['statistics']
        
        # Validate structure
        required_fields = ['entity_counts', 'total_entities', 'total_relationships', 'total_mentions', 'top_entities']
        for field in required_fields:
            assert field in stats, f"Missing required field: {field}"
        
        # Validate data types and values
        assert isinstance(stats['total_entities'], int), "total_entities should be an integer"
        assert isinstance(stats['total_mentions'], int), "total_mentions should be an integer"
        assert stats['total_entities'] > 0, "Should have at least one entity"
        assert stats['total_mentions'] > 0, "Should have at least one mention"
        
        # Validate entity counts
        assert isinstance(stats['entity_counts'], dict), "entity_counts should be a dictionary"
        total_from_counts = sum(stats['entity_counts'].values())
        assert total_from_counts == stats['total_entities'], "Entity counts don't match total"
        
        # Validate top entities
        assert isinstance(stats['top_entities'], list), "top_entities should be a list"
        for entity in stats['top_entities']:
            assert 'kg_id' in entity, "Top entity missing kg_id"
            assert 'labels' in entity, "Top entity missing labels"
            assert 'mention_count' in entity, "Top entity missing mention_count"
    
    def test_search_endpoint(self):
        """Test /api/kg/search endpoint"""
        # Test basic search
        response = requests.get(f"{self.base_url}/api/kg/search?q=rama")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'entities' in data
        assert 'count' in data
        assert 'query' in data
        assert data['query'] == 'rama'
        
        # Should find entities
        assert data['count'] > 0, "Search for 'rama' should return results"
        assert len(data['entities']) == data['count'], "Entity count mismatch"
        
        # Validate entity structure
        for entity in data['entities']:
            self._validate_entity_structure(entity)
        
        # Test search with type filter
        response = requests.get(f"{self.base_url}/api/kg/search?q=rama&type=Person")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        
        # Test empty search
        response = requests.get(f"{self.base_url}/api/kg/search?q=nonexistententity123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        assert data['count'] == 0
        
        # Test missing query parameter
        response = requests.get(f"{self.base_url}/api/kg/search")
        assert response.status_code == 400, "Should return 400 for missing query parameter"
    
    def test_entities_endpoint(self):
        """Test /api/kg/entities endpoint"""
        # Test basic entities list
        response = requests.get(f"{self.base_url}/api/kg/entities")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'entities' in data
        assert 'count' in data
        
        # Should have entities
        assert data['count'] > 0, "Should have at least one entity"
        assert len(data['entities']) > 0, "Should return entity list"
        
        # Validate entity structure
        for entity in data['entities']:
            self._validate_entity_structure(entity)
        
        # Test with type filter
        response = requests.get(f"{self.base_url}/api/kg/entities?type=Person")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        
        # All returned entities should be of type Person
        for entity in data['entities']:
            assert entity['entity_type'] == 'Person', f"Expected Person, got {entity['entity_type']}"
        
        # Test with limit
        response = requests.get(f"{self.base_url}/api/kg/entities?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data['entities']) <= 3, "Should respect limit parameter"
    
    def test_entity_detail_endpoint(self):
        """Test /api/kg/entities/{id} endpoint"""
        # First get an entity ID
        response = requests.get(f"{self.base_url}/api/kg/entities?limit=1")
        entities = response.json()['entities']
        assert len(entities) > 0, "Need at least one entity for detail test"
        
        entity_id = entities[0]['kg_id']
        
        # Test full URI
        response = requests.get(f"{self.base_url}/api/kg/entities/{entity_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'entity' in data
        assert 'relationships' in data
        assert 'mentions' in data
        assert 'stats' in data
        
        # Validate entity structure
        entity = data['entity']
        self._validate_entity_structure(entity)
        assert entity['kg_id'] == entity_id, "Entity ID should match requested ID"
        
        # Test short form (just the name part)
        short_id = entity_id.split('/')[-1]  # Get 'rama' from 'http://ramayanam.hanuma.com/entity/rama'
        response = requests.get(f"{self.base_url}/api/kg/entities/{short_id}")
        assert response.status_code == 200
        
        # Test non-existent entity
        response = requests.get(f"{self.base_url}/api/kg/entities/nonexistent")
        assert response.status_code == 404, "Should return 404 for non-existent entity"
    
    def test_relationships_endpoint(self):
        """Test /api/kg/relationships/{id} endpoint"""
        # Get an entity ID first
        response = requests.get(f"{self.base_url}/api/kg/entities?limit=1")
        entities = response.json()['entities']
        assert len(entities) > 0, "Need at least one entity for relationships test"
        
        entity_id = entities[0]['kg_id']
        short_id = entity_id.split('/')[-1]
        
        # Test relationships endpoint
        response = requests.get(f"{self.base_url}/api/kg/relationships/{short_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'entity_id' in data
        assert 'relationships' in data
        assert 'count' in data
        assert isinstance(data['relationships'], list)
    
    def test_extraction_endpoint(self):
        """Test /api/kg/extract endpoint (admin function)"""
        # This is a POST endpoint that triggers extraction
        # We'll test that it responds but not actually run extraction again
        response = requests.post(f"{self.base_url}/api/kg/extract")
        
        # Should return 200 and take some time
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('success') is True, "Extraction should succeed"
        assert 'statistics' in data, "Should return statistics after extraction"
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        # Get statistics
        stats_response = requests.get(f"{self.base_url}/api/kg/statistics")
        stats = stats_response.json()['statistics']
        
        # Get all entities
        entities_response = requests.get(f"{self.base_url}/api/kg/entities?limit=100")
        entities_data = entities_response.json()
        
        # Check consistency
        assert entities_data['count'] == stats['total_entities'], \
            f"Entity count mismatch: entities={entities_data['count']}, stats={stats['total_entities']}"
        
        # Count entities by type
        type_counts = {}
        for entity in entities_data['entities']:
            entity_type = entity['entity_type']
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        # Compare with statistics
        for entity_type, count in type_counts.items():
            assert stats['entity_counts'].get(entity_type, 0) == count, \
                f"Type count mismatch for {entity_type}: counted={count}, stats={stats['entity_counts'].get(entity_type, 0)}"
    
    def test_uri_format_validation(self):
        """Test that all entities use correct URI format"""
        response = requests.get(f"{self.base_url}/api/kg/entities")
        entities = response.json()['entities']
        
        for entity in entities:
            kg_id = entity['kg_id']
            assert kg_id.startswith('http://ramayanam.hanuma.com/entity/'), \
                f"Invalid URI format: {kg_id}"
            
            # Should not contain old domain
            assert 'example.org' not in kg_id, f"Contains old domain: {kg_id}"
    
    def test_performance_benchmarks(self):
        """Test API response times"""
        endpoints = [
            ('/api/kg/statistics', 'Statistics'),
            ('/api/kg/entities?limit=10', 'Entities List'),
            ('/api/kg/search?q=rama', 'Search'),
        ]
        
        for endpoint, name in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}")
            duration = time.time() - start_time
            
            assert response.status_code == 200, f"{name} endpoint failed"
            assert duration < 2.0, f"{name} too slow: {duration:.3f}s (should be < 2.0s)"
            
            self.log(f"⚡ {name}: {duration:.3f}s")
    
    def _validate_entity_structure(self, entity: Dict[str, Any]):
        """Validate entity data structure"""
        required_fields = ['kg_id', 'entity_type', 'labels']
        for field in required_fields:
            assert field in entity, f"Entity missing required field: {field}"
        
        # Validate labels structure
        labels = entity['labels']
        assert isinstance(labels, dict), "Labels should be a dictionary"
        assert 'en' in labels, "Entity should have English label"
        
        # Validate entity type
        valid_types = ['Person', 'Place', 'Event', 'Object', 'Concept']
        assert entity['entity_type'] in valid_types, f"Invalid entity type: {entity['entity_type']}"
        
        # Validate URI format
        assert entity['kg_id'].startswith('http://'), "kg_id should be a valid URI"
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        self.log("🚀 Starting Knowledge Graph API Test Suite")
        self.log(f"📡 Testing API at: {self.base_url}")
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("Statistics Endpoint", self.test_statistics_endpoint),
            ("Search Endpoint", self.test_search_endpoint),
            ("Entities Endpoint", self.test_entities_endpoint),
            ("Entity Detail Endpoint", self.test_entity_detail_endpoint),
            ("Relationships Endpoint", self.test_relationships_endpoint),
            ("Extraction Endpoint", self.test_extraction_endpoint),
            ("Data Consistency", self.test_data_consistency),
            ("URI Format Validation", self.test_uri_format_validation),
            ("Performance Benchmarks", self.test_performance_benchmarks),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        self.generate_report(passed, total)
        return passed == total
    
    def generate_report(self, passed: int, total: int):
        """Generate test report"""
        self.log("\n" + "="*60)
        self.log("📊 TEST REPORT")
        self.log("="*60)
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            self.log(f"{status} {result.name}: {result.duration:.3f}s")
        
        self.log("-"*60)
        self.log(f"📈 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED!")
        else:
            self.log(f"⚠️  {total - passed} tests failed")
            
        total_time = sum(r.duration for r in self.results)
        self.log(f"⏱️  Total time: {total_time:.3f}s")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Knowledge Graph API Test Suite")
    parser.add_argument("--url", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--timeout", default=30, type=int, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    # Set global timeout
    import socket
    socket.setdefaulttimeout(args.timeout)
    
    tester = KnowledgeGraphAPITester(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()