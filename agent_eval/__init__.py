"""
Agent Evaluation Framework

A comprehensive framework for evaluating AI agents across multiple dimensions of capability.
"""

from .evaluator import Evaluator, EvaluationResults
from .protocol import AgentProtocol
from .benchmark import Benchmark, BenchmarkBuilder
from .metrics import Metrics, MetricsBuilder

__version__ = "0.1.0"
__all__ = [
    "Evaluator",
    "EvaluationResults", 
    "AgentProtocol",
    "Benchmark",
    "BenchmarkBuilder",
    "Metrics",
    "MetricsBuilder",
]
