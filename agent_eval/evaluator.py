"""
Core evaluator for running agent evaluations.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Protocol, Optional
import json

from .protocol import AgentProtocol
from .benchmark import Benchmark, BenchmarkResult
from .metrics import Metrics, MetricsCalculator


@dataclass
class EvaluationResults:
    """Results from an evaluation run."""
    agent_name: str
    benchmark_results: list[BenchmarkResult]
    metrics: dict
    summary: dict
    
    def summary(self) -> str:
        return f"""
Agent: {self.agent_name}
Benchmarks: {len(self.benchmark_results)}
Success Rate: {self.summary.get('success_rate', 0):.1%}
Avg Latency: {self.summary.get('avg_latency', 0):.2f}s
Score: {self.summary.get('overall_score', 0)}/100
        """.strip()
    
    def metrics(self) -> dict:
        return self.metrics
    
    def to_json(self, path: str):
        with open(path, 'w') as f:
            json.dump({
                'agent_name': self.agent_name,
                'benchmark_results': [r.to_dict() for r in self.benchmark_results],
                'metrics': self.metrics,
                'summary': self.summary
            }, f, indent=2)
    
    def to_csv(self, path: str):
        import csv
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Benchmark', 'Score', 'Success Rate', 'Latency (ms)'])
            for r in self.benchmark_results:
                writer.writerow([r.name, r.score, r.success_rate, r.avg_latency_ms])


class Evaluator:
    """
    Main evaluator class for running agent evaluations.
    
    Usage:
        evaluator = Evaluator(agent=my_agent, benchmarks=[...])
        results = await evaluator.evaluate(test_suite=[...])
    """
    
    def __init__(
        self,
        agent: AgentProtocol,
        benchmarks: list[Benchmark],
        metrics: Optional[Metrics] = None,
        name: Optional[str] = None,
    ):
        self.agent = agent
        self.benchmarks = benchmarks
        self.metrics = metrics or Metrics.default()
        self.name = name or agent.name if hasattr(agent, 'name') else 'unknown'
        self._results: list[BenchmarkResult] = []
    
    async def evaluate(
        self,
        test_suite: list[dict] | str,
        iterations: int = 1,
        parallel: int = 1,
    ) -> EvaluationResults:
        """
        Run evaluation on a test suite.
        
        Args:
            test_suite: List of test cases or path to JSON file
            iterations: Number of times to run each test
            parallel: Number of tests to run in parallel
            
        Returns:
            EvaluationResults with detailed metrics
        """
        # Load test suite
        if isinstance(test_suite, str):
            with open(test_suite) as f:
                test_cases = json.load(f)
        else:
            test_cases = test_suite
        
        # Run each benchmark
        for benchmark in self.benchmarks:
            result = await self._run_benchmark(
                benchmark, test_cases, iterations, parallel
            )
            self._results.append(result)
        
        # Calculate overall metrics
        metrics = self.metrics.calculate(self._results)
        
        # Build summary
        total_score = sum(r.score for r in self._results) / len(self._results) if self._results else 0
        success_rates = [r.success_rate for r in self._results]
        avg_latencies = [r.avg_latency_ms for r in self._results if r.avg_latency_ms]
        
        summary = {
            'overall_score': total_score,
            'success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
            'avg_latency': sum(avg_latencies) / len(avg_latencies) if avg_latencies else 0,
        }
        
        return EvaluationResults(
            agent_name=self.name,
            benchmark_results=self._results,
            metrics=metrics,
            summary=summary,
        )
    
    async def _run_benchmark(
        self,
        benchmark: Benchmark,
        test_cases: list[dict],
        iterations: int,
        parallel: int,
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        results = []
        
        semaphore = asyncio.Semaphore(parallel)
        
        async def run_test(test_case):
            async with semaphore:
                return await benchmark.run(self.agent, test_case, iterations)
        
        # Run all tests
        tasks = [run_test(tc) for tc in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        
        # Calculate benchmark result
        return benchmark.calculate_result(valid_results)
