"""
Benchmarks for specific evaluation scenarios.
"""

from .terminal import terminal_bench
from .code_completion import code_completion
from .multi_agent import multi_agent

__all__ = [
    "terminal_bench",
    "code_completion",
    "multi_agent",
]
