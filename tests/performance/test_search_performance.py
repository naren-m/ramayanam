"""
Performance tracking tests for search functionality.

This module benchmarks search performance and saves metrics to a commitable file
for tracking performance changes over time.
"""

import pytest
import time
import json
import os
import statistics
import psutil
import gc
from datetime import datetime
from pathlib import Path

from api.services.fuzzy_search_service import FuzzySearchService
from api.services.optimized_fuzzy_search_service import OptimizedFuzzySearchService
from ramayanam import Ramayanam


class PerformanceTracker:
    """Track and save performance metrics."""
    
    def __init__(self):
        self.metrics_file = Path(__file__).parent / "performance_metrics.json"
        self.current_run = {
            "timestamp": datetime.now().isoformat(),
            "git_branch": self._get_git_branch(),
            "git_commit": self._get_git_commit(),
            "system_info": self._get_system_info(),
            "benchmark_results": {}
        }
    
    def _get_git_branch(self):
        """Get current git branch."""
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_git_commit(self):
        """Get current git commit hash."""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_system_info(self):
        """Get system information."""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}"
        }
    
    def benchmark_function(self, func, *args, iterations=5, warmup=1):
        """
        Benchmark a function with multiple iterations.
        
        Args:
            func: Function to benchmark
            *args: Arguments to pass to function
            iterations: Number of timing iterations
            warmup: Number of warmup runs (not timed)
            
        Returns:
            dict: Performance statistics
        """
        # Warmup runs
        for _ in range(warmup):
            try:
                func(*args)
            except Exception:
                pass  # Ignore warmup errors
        
        # Force garbage collection before timing
        gc.collect()
        
        # Timed runs
        times = []
        memory_usage = []
        result_counts = []
        
        for _ in range(iterations):
            # Measure memory before
            mem_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            start_time = time.perf_counter()
            try:
                result = func(*args)
                success = True
                result_count = len(result) if hasattr(result, '__len__') else 1
            except Exception as e:
                success = False
                result_count = 0
                print(f"Benchmark error: {e}")
            
            end_time = time.perf_counter()
            
            # Measure memory after
            mem_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            if success:
                times.append(end_time - start_time)
                memory_usage.append(mem_after - mem_before)
                result_counts.append(result_count)
        
        if not times:
            return {
                "error": "All benchmark iterations failed",
                "iterations": 0
            }
        
        return {
            "iterations": len(times),
            "avg_time_ms": round(statistics.mean(times) * 1000, 3),
            "min_time_ms": round(min(times) * 1000, 3),
            "max_time_ms": round(max(times) * 1000, 3),
            "std_dev_ms": round(statistics.stdev(times) * 1000, 3) if len(times) > 1 else 0,
            "avg_memory_mb": round(statistics.mean(memory_usage), 2),
            "avg_result_count": round(statistics.mean(result_counts), 1)
        }
    
    def add_benchmark(self, name, service_type, query, threshold, stats):
        """Add benchmark results."""
        if service_type not in self.current_run["benchmark_results"]:
            self.current_run["benchmark_results"][service_type] = {}
        
        self.current_run["benchmark_results"][service_type][name] = {
            "query": query,
            "threshold": threshold,
            "stats": stats
        }
    
    def save_metrics(self):
        """Save current metrics to file."""
        # Load existing metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    all_metrics = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                all_metrics = {"runs": []}
        else:
            all_metrics = {"runs": []}
        
        # Add current run
        all_metrics["runs"].append(self.current_run)
        
        # Keep only last 50 runs to prevent file from growing too large
        all_metrics["runs"] = all_metrics["runs"][-50:]
        
        # Save back to file
        self.metrics_file.parent.mkdir(exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2, sort_keys=True)
        
        return self.metrics_file


@pytest.fixture(scope="module")
def ramayanam_data():
    """Load Ramayanam data once for all tests."""
    try:
        return Ramayanam.load()
    except Exception as e:
        pytest.skip(f"Could not load Ramayanam data: {e}")


@pytest.fixture(scope="module") 
def fuzzy_search_service(ramayanam_data):
    """Create FuzzySearchService instance."""
    return FuzzySearchService(ramayanam_data)


@pytest.fixture(scope="module")
def optimized_fuzzy_search_service(ramayanam_data):
    """Create OptimizedFuzzySearchService instance."""
    return OptimizedFuzzySearchService(ramayanam_data)


@pytest.fixture(scope="module")
def performance_tracker():
    """Create performance tracker."""
    return PerformanceTracker()


# Benchmark queries - diverse set for comprehensive testing
BENCHMARK_QUERIES = [
    # High frequency words (should benefit from indexing)
    {"query": "rama", "threshold": 70, "description": "common_word_high_results"},
    {"query": "hanuman", "threshold": 70, "description": "common_character_medium_results"},
    
    # Specific phrases (should benefit from caching)
    {"query": "devotion to rama", "threshold": 70, "description": "phrase_search_medium_results"},
    {"query": "forest exile", "threshold": 70, "description": "story_context_low_results"},
    
    # Low frequency words (less benefit from indexing)
    {"query": "celestial", "threshold": 70, "description": "uncommon_word_low_results"},
    {"query": "weapon", "threshold": 70, "description": "specific_object_very_low_results"},
    
    # High threshold (fewer results)
    {"query": "sita", "threshold": 85, "description": "high_threshold_fewer_results"},
    
    # Sanskrit terms
    {"query": "dharma", "threshold": 70, "description": "sanskrit_concept_varied_results"},
]


@pytest.mark.performance
class TestSearchPerformance:
    """Performance tests for search functionality."""
    
    def test_fuzzy_search_service_performance(self, fuzzy_search_service, performance_tracker):
        """Benchmark FuzzySearchService performance."""
        for query_config in BENCHMARK_QUERIES:
            query = query_config["query"]
            threshold = query_config["threshold"] 
            description = query_config["description"]
            
            # Test translation search
            stats = performance_tracker.benchmark_function(
                fuzzy_search_service.search_translation_fuzzy,
                query,
                1000,  # max_results
                iterations=3,  # Fewer iterations to keep tests fast
                warmup=1
            )
            
            performance_tracker.add_benchmark(
                f"translation_{description}",
                "FuzzySearchService",
                query,
                threshold,
                stats
            )
            
            # Test Sanskrit search  
            stats = performance_tracker.benchmark_function(
                fuzzy_search_service.search_sloka_sanskrit_fuzzy,
                query,
                threshold,
                1000,  # max_results
                iterations=3,
                warmup=1
            )
            
            performance_tracker.add_benchmark(
                f"sanskrit_{description}",
                "FuzzySearchService", 
                query,
                threshold,
                stats
            )
    
    def test_optimized_search_service_performance(self, optimized_fuzzy_search_service, performance_tracker):
        """Benchmark OptimizedFuzzySearchService performance."""
        for query_config in BENCHMARK_QUERIES:
            query = query_config["query"]
            threshold = query_config["threshold"]
            description = query_config["description"]
            
            # Test translation search
            stats = performance_tracker.benchmark_function(
                optimized_fuzzy_search_service.search_translation_fuzzy,
                query,
                1000,  # max_results
                iterations=3,
                warmup=1
            )
            
            performance_tracker.add_benchmark(
                f"translation_{description}",
                "OptimizedFuzzySearchService",
                query,
                threshold,
                stats
            )
            
            # Test Sanskrit search
            stats = performance_tracker.benchmark_function(
                optimized_fuzzy_search_service.search_sloka_sanskrit_fuzzy,
                query,
                threshold,
                1000,  # max_results
                iterations=3,
                warmup=1
            )
            
            performance_tracker.add_benchmark(
                f"sanskrit_{description}",
                "OptimizedFuzzySearchService",
                query, 
                threshold,
                stats
            )
    
    def test_cache_performance(self, optimized_fuzzy_search_service, performance_tracker):
        """Test cache hit performance."""
        query = "rama"
        
        # First search (cache miss)
        stats_miss = performance_tracker.benchmark_function(
            optimized_fuzzy_search_service.search_translation_fuzzy,
            query,
            1000,
            iterations=1,
            warmup=0
        )
        
        # Second search (cache hit)  
        stats_hit = performance_tracker.benchmark_function(
            optimized_fuzzy_search_service.search_translation_fuzzy,
            query,
            1000,
            iterations=3,
            warmup=0
        )
        
        # Calculate cache benefit
        if stats_miss["avg_time_ms"] > 0 and stats_hit["avg_time_ms"] > 0:
            cache_speedup = stats_miss["avg_time_ms"] / stats_hit["avg_time_ms"]
        else:
            cache_speedup = 1.0
        
        performance_tracker.add_benchmark(
            "cache_miss_vs_hit",
            "OptimizedFuzzySearchService",
            query,
            70,
            {
                "cache_miss_time_ms": stats_miss["avg_time_ms"],
                "cache_hit_time_ms": stats_hit["avg_time_ms"],
                "cache_speedup": round(cache_speedup, 2),
                "cache_stats": (optimized_fuzzy_search_service.get_cache_stats() 
                              if hasattr(optimized_fuzzy_search_service, 'get_cache_stats') 
                              else {})
            }
        )
    
    def test_save_performance_metrics(self, performance_tracker):
        """Save performance metrics to file."""
        metrics_file = performance_tracker.save_metrics()
        
        # Verify file was created and is valid JSON
        assert metrics_file.exists(), "Performance metrics file was not created"
        
        with open(metrics_file, 'r') as f:
            data = json.load(f)
        
        assert "runs" in data, "Metrics file missing 'runs' key"
        assert len(data["runs"]) > 0, "No performance runs saved"
        
        latest_run = data["runs"][-1]
        assert "timestamp" in latest_run, "Latest run missing timestamp"
        assert "benchmark_results" in latest_run, "Latest run missing benchmark results"
        
        print(f"\n✅ Performance metrics saved to: {metrics_file}")
        print(f"📊 Benchmark results for {len(BENCHMARK_QUERIES)} queries across 2 services")
        
        # Print summary of latest results
        if "OptimizedFuzzySearchService" in latest_run["benchmark_results"]:
            optimized_results = latest_run["benchmark_results"]["OptimizedFuzzySearchService"]
            translation_times = [
                result["stats"]["avg_time_ms"] 
                for name, result in optimized_results.items() 
                if "translation_" in name and "avg_time_ms" in result["stats"]
            ]
            if translation_times:
                avg_translation_time = statistics.mean(translation_times)
                print(f"📈 Average translation search time: {avg_translation_time:.1f}ms")
        
        # Show git info for tracking
        print(f"🔄 Git branch: {latest_run['git_branch']}")
        print(f"🔍 Git commit: {latest_run['git_commit']}")


if __name__ == "__main__":
    # Allow running performance tests directly
    pytest.main([__file__, "-v", "-m", "performance"])