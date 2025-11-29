"""
Performance tests and benchmarks.

Test Coverage:
- Queue processing throughput
- Concurrent agent handling
- Memory efficiency
- Response time under load
"""
import pytest
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.smart_queue import SmartAgentQueue, QueueManager, QueueStatus
from src.models.content import ContentResult, ContentType
from src.models.route import Route, RoutePoint
from src.core.resilience.circuit_breaker import CircuitBreaker
from src.core.resilience.rate_limiter import TokenBucket, RateLimiter


class TestQueuePerformance:
    """Performance tests for SmartAgentQueue."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up fast timeouts for performance testing."""
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 0.5
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 1.0
        SmartAgentQueue.EXPECTED_AGENTS = 3
        SmartAgentQueue.MIN_REQUIRED_FOR_SOFT = 2
        SmartAgentQueue.MIN_REQUIRED_FOR_HARD = 1
        yield
        SmartAgentQueue.SOFT_TIMEOUT_SECONDS = 15.0
        SmartAgentQueue.HARD_TIMEOUT_SECONDS = 30.0

    def test_queue_processing_speed(self):
        """Test queue can process results quickly."""
        queue = SmartAgentQueue("perf_test_1")

        def submit_all():
            for agent in ["video", "music", "text"]:
                result = ContentResult(
                    content_type=ContentType.VIDEO,
                    title="Test",
                    source="Test"
                )
                queue.submit_success(agent, result)

        start = time.time()
        thread = threading.Thread(target=submit_all)
        thread.start()

        results, metrics = queue.wait_for_results()
        thread.join()

        elapsed = time.time() - start

        assert len(results) == 3
        assert elapsed < 0.1  # Should be very fast with no delays
        assert metrics.wait_time_ms < 100

    def test_queue_throughput_multiple_points(self):
        """Test processing multiple points in parallel."""
        num_points = 20
        results = []
        lock = threading.Lock()
        processing_times = []

        def process_point(point_id):
            queue = SmartAgentQueue(point_id)
            start = time.time()

            for agent in ["video", "music", "text"]:
                result = ContentResult(
                    content_type=ContentType.VIDEO,
                    title=f"Test {point_id}",
                    source="Test"
                )
                queue.submit_success(agent, result)

            point_results, _ = queue.wait_for_results()
            elapsed = time.time() - start

            with lock:
                results.append(len(point_results))
                processing_times.append(elapsed)

        start_total = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(process_point, f"point_{i}")
                for i in range(num_points)
            ]
            for f in as_completed(futures):
                f.result()

        total_elapsed = time.time() - start_total

        # All points should complete successfully
        assert len(results) == num_points
        assert all(r == 3 for r in results)

        # Should process efficiently in parallel
        avg_time = statistics.mean(processing_times)
        print(f"\nThroughput: {num_points} points in {total_elapsed:.2f}s")
        print(f"Average per point: {avg_time:.4f}s")
        print(f"Points per second: {num_points/total_elapsed:.1f}")

        # Performance assertion
        assert total_elapsed < 5.0  # Should process 20 points in under 5 seconds

    def test_queue_memory_efficiency(self):
        """Test queue doesn't leak memory across many operations."""
        import gc

        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())

        for i in range(100):
            queue = SmartAgentQueue(f"mem_test_{i}")
            for agent in ["video", "music", "text"]:
                result = ContentResult(
                    content_type=ContentType.VIDEO,
                    title="Test",
                    source="Test"
                )
                queue.submit_success(agent, result)
            queue.wait_for_results()

        gc.collect()
        final_objects = len(gc.get_objects())

        # Allow some growth but not excessive
        object_growth = final_objects - initial_objects
        print(f"\nObject growth: {object_growth}")

        # Should not grow excessively (allow ~10 objects per queue)
        assert object_growth < 1000


class TestConcurrencyPerformance:
    """Performance tests for concurrent operations."""

    def test_thread_pool_scalability(self):
        """Test performance with varying thread pool sizes."""
        num_tasks = 50
        results_by_pool_size = {}

        for pool_size in [4, 8, 16]:
            results = []
            lock = threading.Lock()

            def task():
                time.sleep(0.01)  # Simulate work
                with lock:
                    results.append(1)

            start = time.time()

            with ThreadPoolExecutor(max_workers=pool_size) as executor:
                futures = [executor.submit(task) for _ in range(num_tasks)]
                for f in as_completed(futures):
                    f.result()

            elapsed = time.time() - start
            results_by_pool_size[pool_size] = elapsed

            print(f"\nPool size {pool_size}: {elapsed:.3f}s for {num_tasks} tasks")

            assert len(results) == num_tasks

        # More threads should generally be faster (up to a point)
        # Don't assert specific values as they depend on system

    def test_lock_contention(self):
        """Test performance under high lock contention."""
        lock = threading.Lock()
        counter = [0]
        num_increments = 1000
        num_threads = 10

        def increment():
            for _ in range(num_increments // num_threads):
                with lock:
                    counter[0] += 1

        start = time.time()

        threads = [threading.Thread(target=increment) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = time.time() - start

        assert counter[0] == num_increments
        print(f"\nLock contention test: {num_increments} increments in {elapsed:.3f}s")

        # Should complete in reasonable time
        assert elapsed < 1.0


class TestResiliencePerformance:
    """Performance tests for resilience patterns."""

    def test_circuit_breaker_overhead(self):
        """Test circuit breaker adds minimal overhead."""
        CircuitBreaker._registry.clear()

        iterations = 10000

        # Baseline without circuit breaker
        start = time.time()
        for _ in range(iterations):
            pass  # Minimal work
        baseline = time.time() - start

        # With circuit breaker
        cb = CircuitBreaker(name="perf_test", failure_threshold=1000)
        start = time.time()
        for _ in range(iterations):
            with cb:
                pass  # Same minimal work
        with_cb = time.time() - start

        overhead = with_cb - baseline
        overhead_per_call = (overhead / iterations) * 1000000  # microseconds

        print(f"\nCircuit breaker overhead: {overhead_per_call:.2f}μs per call")

        # Overhead should be minimal (< 100 microseconds per call)
        assert overhead_per_call < 100

    def test_rate_limiter_throughput(self):
        """Test rate limiter allows expected throughput."""
        RateLimiter._registry.clear()

        # Allow 1000 requests per second
        limiter = RateLimiter(
            name="throughput_test",
            max_calls=1000,
            period=1.0,
            algorithm="token_bucket",
            block=False
        )

        allowed = 0
        start = time.time()

        # Try to make 500 requests quickly
        for _ in range(500):
            if limiter.acquire():
                allowed += 1

        elapsed = time.time() - start

        print(f"\nRate limiter: {allowed} allowed in {elapsed:.3f}s")

        # Should allow at least 400 (80% of requested)
        assert allowed >= 400

    def test_token_bucket_refill_rate(self):
        """Test token bucket refills at expected rate."""
        bucket = TokenBucket(rate=100, capacity=100)

        # Empty the bucket
        bucket.acquire(tokens=100)
        assert bucket.available_tokens < 1

        # Wait for refill
        time.sleep(0.5)  # Should refill ~50 tokens

        available = bucket.available_tokens

        print(f"\nToken refill: {available:.1f} tokens after 0.5s")

        # Should have refilled 40-60 tokens
        assert 40 <= available <= 60


class TestModelPerformance:
    """Performance tests for data models."""

    def test_route_creation_speed(self):
        """Test route creation with many points."""
        num_points = 1000

        start = time.time()

        points = [
            RoutePoint(
                id=f"p{i}",
                index=i,
                address=f"Point {i}",
                latitude=31.0 + i * 0.001,
                longitude=35.0
            )
            for i in range(num_points)
        ]

        route = Route(
            source="Start",
            destination="End",
            points=points
        )

        elapsed = time.time() - start

        print(f"\nRoute creation: {num_points} points in {elapsed:.3f}s")

        assert route.point_count == num_points
        assert elapsed < 1.0  # Should be fast

    def test_point_lookup_speed(self):
        """Test point lookup performance."""
        num_points = 1000

        points = [
            RoutePoint(
                id=f"point_{i}",
                index=i,
                address=f"Point {i}",
                latitude=31.0 + i * 0.001,
                longitude=35.0
            )
            for i in range(num_points)
        ]

        route = Route(source="Start", destination="End", points=points)

        # Time multiple lookups
        lookups = 100
        start = time.time()

        for i in range(lookups):
            point_id = f"point_{i * 10}"  # Look up every 10th point
            found = route.get_point_by_id(point_id)
            assert found is not None

        elapsed = time.time() - start
        per_lookup = (elapsed / lookups) * 1000  # milliseconds

        print(f"\nPoint lookup: {per_lookup:.3f}ms per lookup ({num_points} points)")

        # Should be reasonably fast (< 1ms per lookup)
        assert per_lookup < 1.0

    def test_content_result_serialization(self):
        """Test content result serialization speed."""
        iterations = 1000

        result = ContentResult(
            point_id="test",
            content_type=ContentType.VIDEO,
            title="Test Video",
            description="A test video description",
            url="https://youtube.com/watch?v=test",
            source="YouTube",
            relevance_score=8.5,
            duration_seconds=300,
            metadata={"views": 100000, "likes": 5000}
        )

        start = time.time()

        for _ in range(iterations):
            _ = result.model_dump()

        elapsed = time.time() - start
        per_serialization = (elapsed / iterations) * 1000  # milliseconds

        print(f"\nSerialization: {per_serialization:.4f}ms per result")

        # Should be very fast
        assert per_serialization < 1.0


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for key operations."""

    def test_benchmark_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)
        print("Run individual performance tests for detailed metrics.")
        print("=" * 60)

