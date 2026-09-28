"""
Benchmark definitions and implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable
import asyncio
import time


@dataclass
class BenchmarkResult:
    """Result from running a benchmark."""
    name: str
    score: float
    success_rate: float
    avg_latency_ms: float = 0
    details: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'score': self.score,
            'success_rate': self.success_rate,
            'avg_latency_ms': self.avg_latency_ms,
            'details': self.details,
        }


class Benchmark(ABC):
    """Base class for benchmarks."""
    
    def __init__(self, name: str, threshold: float = 0.8):
        self.name = name
        self.threshold = threshold
    
    @abstractmethod
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        """Run the benchmark on a single test case."""
        pass
    
    def calculate_result(self, results: list[dict]) -> BenchmarkResult:
        """Calculate the overall benchmark result."""
        if not results:
            return BenchmarkResult(name=self.name, score=0, success_rate=0)
        
        success_count = sum(1 for r in results if r.get('success', False))
        scores = [r.get('score', 0) for r in results]
        latencies = [r.get('latency_ms', 0) for r in results]
        
        return BenchmarkResult(
            name=self.name,
            score=sum(scores) / len(scores) if scores else 0,
            success_rate=success_count / len(results),
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
            details={
                'total_tests': len(results),
                'passed': success_count,
                'failed': len(results) - success_count,
            }
        )
    
    @staticmethod
    def task_completion(threshold: float = 0.8) -> 'TaskCompletionBenchmark':
        """Benchmark for task completion."""
        return TaskCompletionBenchmark(threshold=threshold)
    
    @staticmethod
    def tool_efficiency(
        max_tools: int = 10,
        optimal_range: tuple = (1, 5)
    ) -> 'ToolEfficiencyBenchmark':
        """Benchmark for tool usage efficiency."""
        return ToolEfficiencyBenchmark(max_tools=max_tools, optimal_range=optimal_range)
    
    @staticmethod
    def error_recovery(max_retries: int = 3) -> 'ErrorRecoveryBenchmark':
        """Benchmark for error recovery."""
        return ErrorRecoveryBenchmark(max_retries=max_retries)
    
    @staticmethod
    def latency(
        p50_threshold_ms: int = 1000,
        p95_threshold_ms: int = 5000
    ) -> 'LatencyBenchmark':
        """Benchmark for response latency."""
        return LatencyBenchmark(
            p50_threshold_ms=p50_threshold_ms,
            p95_threshold_ms=p95_threshold_ms,
        )
    
    @staticmethod
    def consistency() -> 'ConsistencyBenchmark':
        """Benchmark for consistency across runs."""
        return ConsistencyBenchmark()
    
    @staticmethod
    def context_usage() -> 'ContextUsageBenchmark':
        """Benchmark for token/context efficiency."""
        return ContextUsageBenchmark()


class TaskCompletionBenchmark(Benchmark):
    """Measures whether the agent achieves its task goal."""
    
    def __init__(self, threshold: float = 0.8):
        super().__init__("task_completion", threshold)
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        input_text = test_case.get('input', '')
        expected = test_case.get('expected', '')
        
        results = []
        for _ in range(iterations):
            result = await agent.run(input_text, test_case.get('context'))
            results.append(result)
        
        # Check if any run succeeded
        success = any(r.success for r in results)
        
        # Simple text matching score (can be customized)
        outputs = [r.output for r in results]
        scores = []
        for output in outputs:
            if expected and output:
                # Simple exact match for now
                score = 1.0 if expected.lower() in output.lower() else 0.0
            else:
                score = 1.0 if success else 0.0
            scores.append(score)
        
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        return {
            'success': success,
            'score': sum(scores) / len(scores),
            'latency_ms': avg_latency,
            'outputs': outputs,
        }


class ToolEfficiencyBenchmark(Benchmark):
    """Measures optimal tool usage."""
    
    def __init__(self, max_tools: int = 10, optimal_range: tuple = (1, 5)):
        super().__init__("tool_efficiency")
        self.max_tools = max_tools
        self.optimal_range = optimal_range
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        result = await agent.run(
            test_case.get('input', ''),
            test_case.get('context')
        )
        
        tools_used = len(result.tools_used) if result.tools_used else 0
        
        # Score based on how close to optimal range
        if tools_used == 0:
            score = 1.0  # No tools needed
        elif self.optimal_range[0] <= tools_used <= self.optimal_range[1]:
            score = 1.0
        elif tools_used > self.max_tools:
            score = 0.0
        else:
            # Linear falloff
            distance = min(
                abs(tools_used - self.optimal_range[0]),
                abs(tools_used - self.optimal_range[1])
            )
            score = max(0, 1.0 - (distance / self.max_tools))
        
        return {
            'success': score >= self.threshold,
            'score': score,
            'latency_ms': result.latency_ms,
            'tools_used': tools_used,
        }


class ErrorRecoveryBenchmark(Benchmark):
    """Measures ability to recover from errors."""
    
    def __init__(self, max_retries: int = 3):
        super().__init__("error_recovery")
        self.max_retries = max_retries
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        # Simulate an error scenario by providing bad context
        error_context = {**test_case.get('context', {}), '_force_error': True}
        
        result = await agent.run(
            test_case.get('input', ''),
            error_context
        )
        
        # Score based on whether agent recovered or handled gracefully
        if result.success:
            score = 1.0
        elif result.error and not result.output:
            score = 0.0
        else:
            score = 0.5  # Partial - returned something
        
        return {
            'success': result.success,
            'score': score,
            'latency_ms': result.latency_ms,
            'error': result.error,
        }


class LatencyBenchmark(Benchmark):
    """Measures response latency."""
    
    def __init__(
        self,
        p50_threshold_ms: int = 1000,
        p95_threshold_ms: int = 5000
    ):
        super().__init__("latency")
        self.p50_threshold = p50_threshold_ms
        self.p95_threshold = p95_threshold_ms
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        results = []
        for _ in range(iterations):
            result = await agent.run(
                test_case.get('input', ''),
                test_case.get('context')
            )
            results.append(result)
        
        latencies = [r.latency_ms for r in results]
        latencies.sort()
        
        p50 = latencies[len(latencies) // 2] if latencies else 0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
        
        # Score based on thresholds
        if p95 <= self.p95_threshold:
            if p50 <= self.p50_threshold:
                score = 1.0
            else:
                score = 0.7
        else:
            score = 0.3
        
        return {
            'success': score >= self.threshold,
            'score': score,
            'latency_ms': sum(latencies) / len(latencies),
            'p50_ms': p50,
            'p95_ms': p95,
        }


class ConsistencyBenchmark(Benchmark):
    """Measures consistency across multiple runs."""
    
    def __init__(self):
        super().__init__("consistency")
    
    async def run(self, agent, test_case: dict, iterations: int = 3) -> dict:
        results = []
        for _ in range(iterations):
            result = await agent.run(
                test_case.get('input', ''),
                test_case.get('context')
            )
            results.append(result)
        
        # Check success consistency
        successes = [r.success for r in results]
        success_rate = sum(successes) / len(successes)
        
        # Check output consistency (for successful runs)
        successful_outputs = [r.output for r in results if r.success]
        
        if len(successful_outputs) > 1:
            # Simple consistency check - same output
            all_same = all(o == successful_outputs[0] for o in successful_outputs)
            score = 1.0 if all_same else 0.5
        else:
            score = success_rate
        
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        return {
            'success': success_rate >= self.threshold,
            'score': score,
            'latency_ms': avg_latency,
            'consistency': success_rate,
        }


class ContextUsageBenchmark(Benchmark):
    """Measures token/context efficiency."""
    
    def __init__(self):
        super().__init__("context_usage")
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        result = await agent.run(
            test_case.get('input', ''),
            test_case.get('context')
        )
        
        # Estimate token usage (would need actual token counting in production)
        input_tokens = len(test_case.get('input', '').split())
        output_tokens = len(result.output.split()) if result.output else 0
        total_tokens = input_tokens + output_tokens
        
        # Score based on efficiency (lower is better for simple tasks)
        if result.success:
            # Good: achieved goal with reasonable token usage
            score = min(1.0, 1000 / max(total_tokens, 1))
        else:
            score = 0.0
        
        return {
            'success': result.success,
            'score': score,
            'latency_ms': result.latency_ms,
            'tokens': total_tokens,
        }


# Convenience function for creating benchmarks
def create_benchmark(name: str, **kwargs) -> Benchmark:
    """Create a benchmark by name with optional parameters."""
    benchmarks = {
        'task_completion': TaskCompletionBenchmark,
        'tool_efficiency': ToolEfficiencyBenchmark,
        'error_recovery': ErrorRecoveryBenchmark,
        'latency': LatencyBenchmark,
        'consistency': ConsistencyBenchmark,
        'context_usage': ContextUsageBenchmark,
    }
    
    if name not in benchmarks:
        raise ValueError(f"Unknown benchmark: {name}")
    
    return benchmarks[name](**kwargs)


class BenchmarkBuilder:
    """Fluent builder for composing a benchmark suite.

    Example:
        benchmarks = (
            BenchmarkBuilder()
            .add_named("task_completion")
            .add_named("tool_efficiency", max_tools=8)
            .add(Benchmark.consistency())
            .build()
        )
    """

    def __init__(self):
        self._benchmarks: list[Benchmark] = []

    def add(self, benchmark: Benchmark) -> "BenchmarkBuilder":
        self._benchmarks.append(benchmark)
        return self

    def add_named(self, name: str, **kwargs) -> "BenchmarkBuilder":
        self._benchmarks.append(create_benchmark(name, **kwargs))
        return self

    def build(self) -> list[Benchmark]:
        return list(self._benchmarks)
