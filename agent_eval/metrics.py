"""
Metrics calculation and reporting.
"""

from dataclasses import dataclass, field
from typing import Any
import statistics


@dataclass
class Metrics:
    """Default metrics calculator."""
    
    @staticmethod
    def default() -> 'Metrics':
        return Metrics()
    
    def calculate(self, results: list) -> dict:
        """Calculate metrics from benchmark results."""
        if not results:
            return {}
        
        metrics = {}
        
        # Success rate across all benchmarks
        success_rates = [r.success_rate for r in results if hasattr(r, 'success_rate')]
        if success_rates:
            metrics['success_rate'] = sum(success_rates) / len(success_rates)
        
        # Average score
        scores = [r.score for r in results if hasattr(r, 'score')]
        if scores:
            metrics['avg_score'] = sum(scores) / len(scores)
        
        # Latency percentiles
        latencies = [r.avg_latency_ms for r in results if hasattr(r, 'avg_latency_ms') and r.avg_latency_ms > 0]
        if latencies:
            latencies_sorted = sorted(latencies)
            metrics['latency_p50'] = latencies_sorted[len(latencies_sorted) // 2]
            metrics['latency_p95'] = latencies_sorted[int(len(latencies_sorted) * 0.95)]
            metrics['latency_p99'] = latencies_sorted[int(len(latencies_sorted) * 0.99)]
            metrics['avg_latency'] = sum(latencies) / len(latencies)
        
        # Per-benchmark breakdown
        for r in results:
            if hasattr(r, 'name'):
                metrics[r.name] = {
                    'score': r.score,
                    'success_rate': r.success_rate,
                    'latency_ms': r.avg_latency_ms,
                }
        
        return metrics


class MetricsBuilder:
    """Base class for custom metrics calculators."""
    
    name: str = "custom_metrics"
    
    async def calculate(self, results: list) -> dict:
        """Calculate custom metrics."""
        raise NotImplementedError
