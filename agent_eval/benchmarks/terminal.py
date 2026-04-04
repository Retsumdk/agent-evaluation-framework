"""
Terminal/CLI benchmark for testing shell command execution.
"""

from ..benchmark import Benchmark, BenchmarkResult
from ..protocol import AgentResult


def terminal_bench(tasks: list[dict]) -> 'TerminalBenchmark':
    """
    Create a terminal benchmark.
    
    Args:
        tasks: List of {"command": "...", "expected_output": "..."}
    """
    return TerminalBenchmark(tasks)


class TerminalBenchmark(Benchmark):
    """Benchmark for CLI/terminal task execution."""
    
    def __init__(self, tasks: list[dict]):
        super().__init__("terminal")
        self.tasks = tasks
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        """Run terminal tasks."""
        # This would require a shell-capable agent
        # Simplified for framework purposes
        result = await agent.run(test_case.get('input', ''), test_case.get('context'))
        
        return {
            'success': result.success,
            'score': 1.0 if result.success else 0.0,
            'latency_ms': result.latency_ms,
        }
