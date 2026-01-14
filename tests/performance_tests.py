"""Performance tests for the distributed system."""

import time
import statistics
import json
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Performance metrics collection."""
    
    def __init__(self):
        self.latencies: List[float] = []
        self.throughputs: List[float] = []
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.transaction_times: List[float] = []
        self.failover_times: List[float] = []
    
    def record_latency(self, latency: float):
        """Record a latency measurement."""
        self.latencies.append(latency)
    
    def record_throughput(self, throughput: float):
        """Record a throughput measurement."""
        self.throughputs.append(throughput)
    
    def record_cpu_usage(self, cpu: float):
        """Record CPU usage."""
        self.cpu_usage.append(cpu)
    
    def record_memory_usage(self, memory: float):
        """Record memory usage."""
        self.memory_usage.append(memory)
    
    def record_transaction_time(self, time: float):
        """Record transaction execution time."""
        self.transaction_times.append(time)
    
    def record_failover_time(self, time: float):
        """Record failover time."""
        self.failover_times.append(time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for all metrics."""
        stats = {}
        
        if self.latencies:
            stats["latency"] = {
                "mean": statistics.mean(self.latencies),
                "median": statistics.median(self.latencies),
                "min": min(self.latencies),
                "max": max(self.latencies),
                "p95": self._percentile(self.latencies, 95),
                "p99": self._percentile(self.latencies, 99)
            }
        
        if self.throughputs:
            stats["throughput"] = {
                "mean": statistics.mean(self.throughputs),
                "median": statistics.median(self.throughputs),
                "min": min(self.throughputs),
                "max": max(self.throughputs)
            }
        
        if self.cpu_usage:
            stats["cpu_usage"] = {
                "mean": statistics.mean(self.cpu_usage),
                "max": max(self.cpu_usage)
            }
        
        if self.memory_usage:
            stats["memory_usage"] = {
                "mean": statistics.mean(self.memory_usage),
                "max": max(self.memory_usage)
            }
        
        if self.transaction_times:
            stats["transaction_time"] = {
                "mean": statistics.mean(self.transaction_times),
                "min": min(self.transaction_times),
                "max": max(self.transaction_times)
            }
        
        if self.failover_times:
            stats["failover_time"] = {
                "mean": statistics.mean(self.failover_times),
                "min": min(self.failover_times),
                "max": max(self.failover_times)
            }
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def save_results(self, filename: str):
        """Save results to a file."""
        stats = self.get_statistics()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Results saved to {filename}")


def test_latency(metrics: PerformanceMetrics, num_requests: int = 100):
    """Test latency."""
    logger.info(f"Testing latency with {num_requests} requests...")
    
    for i in range(num_requests):
        start = time.time()
        # Simulate request
        time.sleep(0.001)  # Simulate network delay
        latency = (time.time() - start) * 1000  # Convert to ms
        metrics.record_latency(latency)
    
    logger.info("Latency test completed")


def test_throughput(metrics: PerformanceMetrics, duration: float = 10.0):
    """Test throughput."""
    logger.info(f"Testing throughput for {duration} seconds...")
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration:
        # Simulate request
        time.sleep(0.001)
        request_count += 1
    
    throughput = request_count / duration
    metrics.record_throughput(throughput)
    logger.info(f"Throughput: {throughput:.2f} requests/second")


def test_transaction_performance(metrics: PerformanceMetrics, num_transactions: int = 50):
    """Test transaction performance."""
    logger.info(f"Testing transaction performance with {num_transactions} transactions...")
    
    for i in range(num_transactions):
        start = time.time()
        # Simulate 2PC transaction
        time.sleep(0.01)  # Phase 1
        time.sleep(0.01)  # Phase 2
        transaction_time = time.time() - start
        metrics.record_transaction_time(transaction_time)
    
    logger.info("Transaction performance test completed")


def test_failover_performance(metrics: PerformanceMetrics, num_failovers: int = 10):
    """Test failover performance."""
    logger.info(f"Testing failover performance with {num_failovers} failovers...")
    
    for i in range(num_failovers):
        start = time.time()
        # Simulate failover
        time.sleep(0.1)  # Detection
        time.sleep(0.1)  # Selection
        time.sleep(0.1)  # Recovery
        failover_time = time.time() - start
        metrics.record_failover_time(failover_time)
    
    logger.info("Failover performance test completed")


def main():
    """Main function for performance tests."""
    logger.info("Starting performance tests...")
    
    metrics = PerformanceMetrics()
    
    # Run tests
    test_latency(metrics, num_requests=100)
    test_throughput(metrics, duration=5.0)
    test_transaction_performance(metrics, num_transactions=50)
    test_failover_performance(metrics, num_failovers=10)
    
    # Get and print statistics
    stats = metrics.get_statistics()
    print("\n" + "="*50)
    print("Performance Test Results")
    print("="*50)
    print(json.dumps(stats, indent=2))
    print("="*50)
    
    # Save results
    metrics.save_results("performance_results.json")
    
    logger.info("Performance tests completed")


if __name__ == "__main__":
    main()
