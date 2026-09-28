"""
Agent Evaluation Framework

A comprehensive framework for evaluating AI agents across multiple dimensions of capability.
"""

from .evaluator import Evaluator, EvaluationResults
from .protocol import AgentProtocol, AgentResult
from .benchmark import (
    Benchmark,
    BenchmarkBuilder,
    BenchmarkResult,
    TaskCompletionBenchmark,
    ToolEfficiencyBenchmark,
    ErrorRecoveryBenchmark,
    LatencyBenchmark,
    ConsistencyBenchmark,
    ContextUsageBenchmark,
    create_benchmark,
)
from .metrics import Metrics, MetricsBuilder

__version__ = "0.1.0"
__all__ = [
    "Evaluator",
    "EvaluationResults", 
    "AgentProtocol",
    "AgentResult",
    "Benchmark",
    "BenchmarkBuilder",
    "BenchmarkResult",
    "TaskCompletionBenchmark",
    "ToolEfficiencyBenchmark",
    "ErrorRecoveryBenchmark",
    "LatencyBenchmark",
    "ConsistencyBenchmark",
    "ContextUsageBenchmark",
    "create_benchmark",
    "Metrics",
    "MetricsBuilder",
]
