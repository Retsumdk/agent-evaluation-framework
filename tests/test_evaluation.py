"""Tests for the agent evaluation framework core."""

import asyncio
import json

import agent_eval
from agent_eval import (
    AgentResult,
    Benchmark,
    BenchmarkBuilder,
    BenchmarkResult,
    Evaluator,
    Metrics,
    TaskCompletionBenchmark,
)
from agent_eval.benchmark import ToolEfficiencyBenchmark
from agent_eval.protocol import AgentProtocol


class MockAgent:
    """Minimal agent satisfying AgentProtocol for testing."""

    @property
    def name(self) -> str:
        return "mock-agent"

    async def run(self, input: str, context: dict = None) -> AgentResult:
        expected = (context or {}).get("expected", "")
        success = expected.lower() in input.lower() if expected else True
        return AgentResult(
            output=input.upper(),
            success=success,
            tools_used=[{"name": "search"}],
            latency_ms=10.0,
        )

    async def tools(self) -> list:
        return []


def test_package_imports_and_version():
    assert agent_eval.__version__ == "0.1.0"
    for symbol in (
        "Evaluator",
        "EvaluationResults",
        "AgentProtocol",
        "Benchmark",
        "BenchmarkBuilder",
        "Metrics",
        "MetricsBuilder",
    ):
        assert hasattr(agent_eval, symbol)


def test_agent_result_defaults():
    result = AgentResult(output="hi", success=True)
    assert result.tools_used == []
    assert result.metadata == {}
    assert result.error is None


def test_benchmark_result_to_dict():
    r = BenchmarkResult(name="t", score=0.5, success_rate=1.0, avg_latency_ms=4.0, details={"k": 1})
    d = r.to_dict()
    assert d == {"name": "t", "score": 0.5, "success_rate": 1.0, "avg_latency_ms": 4.0, "details": {"k": 1}}


def test_calculate_result_aggregation():
    bench = Benchmark.task_completion()
    runs = [
        {"success": True, "score": 1.0, "latency_ms": 10.0},
        {"success": False, "score": 0.0, "latency_ms": 30.0},
        {"success": True, "score": 0.5, "latency_ms": 20.0},
    ]
    result = bench.calculate_result(runs)
    assert result.name == "task_completion"
    assert result.success_rate == 2 / 3
    assert result.score == 0.5
    assert result.avg_latency_ms == 20.0
    assert result.details == {"total_tests": 3, "passed": 2, "failed": 1}


def test_calculate_result_empty():
    bench = Benchmark.task_completion()
    result = bench.calculate_result([])
    assert result.score == 0
    assert result.success_rate == 0


def test_task_completion_benchmark_run():
    bench = Benchmark.task_completion()
    agent = MockAgent()
    case = {"input": "hello world", "expected": "hello", "context": {"expected": "hello"}}
    out = asyncio.run(bench.run(agent, case))
    assert out["success"] is True
    assert out["score"] == 1.0
    assert out["latency_ms"] == 10.0
    assert out["outputs"] == ["HELLO WORLD"]


def test_task_completion_scores_miss():
    bench = Benchmark.task_completion()
    agent = MockAgent()
    case = {"input": "goodbye", "expected": "hello", "context": {"expected": "hello"}}
    out = asyncio.run(bench.run(agent, case))
    assert out["success"] is False
    assert out["score"] == 0.0


def test_tool_efficiency_optimal_range():
    bench = ToolEfficiencyBenchmark(max_tools=10, optimal_range=(1, 5))
    agent = MockAgent()
    out = asyncio.run(bench.run(agent, {"input": "x"}))
    assert out["tools_used"] == 1
    assert out["score"] == 1.0
    assert out["success"] is True


def test_tool_efficiency_over_max_scores_zero():
    class ToolHeavyAgent(MockAgent):
        async def run(self, input: str, context: dict = None) -> AgentResult:
            result = await super().run(input, context)
            result.tools_used = [{"name": f"t{i}"} for i in range(12)]
            return result

    bench = ToolEfficiencyBenchmark(max_tools=10, optimal_range=(1, 5))
    out = asyncio.run(bench.run(ToolHeavyAgent(), {"input": "x"}))
    assert out["tools_used"] == 12
    assert out["score"] == 0.0
    assert out["success"] is False


def test_metrics_calculate():
    results = [
        BenchmarkResult(name="b1", score=0.8, success_rate=1.0, avg_latency_ms=100.0),
        BenchmarkResult(name="b2", score=0.6, success_rate=0.5, avg_latency_ms=300.0),
    ]
    m = Metrics.default().calculate(results)
    assert m["success_rate"] == 0.75
    assert m["avg_score"] == 0.7
    assert m["avg_latency"] == 200.0
    assert m["latency_p50"] == 300.0
    assert m["b1"]["score"] == 0.8


def test_metrics_empty():
    assert Metrics.default().calculate([]) == {}


def test_evaluator_end_to_end(tmp_path):
    evaluator = Evaluator(agent=MockAgent(), benchmarks=[Benchmark.task_completion()])
    suite = [{"input": "do the thing", "expected": "do", "context": {"expected": "do"}}]
    results = asyncio.run(evaluator.evaluate(suite))
    assert results.agent_name == "mock-agent"
    assert len(results.benchmark_results) == 1
    assert results.summary["overall_score"] == 1.0
    assert results.summary["success_rate"] == 1.0
    assert results.metrics["success_rate"] == 1.0
    assert "task_completion" in results.metrics

    out_json = tmp_path / "results.json"
    results.to_json(str(out_json))
    loaded = json.loads(out_json.read_text())
    assert loaded["agent_name"] == "mock-agent"
    assert loaded["benchmark_results"][0]["name"] == "task_completion"

    out_csv = tmp_path / "results.csv"
    results.to_csv(str(out_csv))
    lines = out_csv.read_text().strip().splitlines()
    assert lines[0] == "Benchmark,Score,Success Rate,Latency (ms)"
    assert len(lines) == 2


def test_evaluation_results_render_summary():
    results = asyncio.run(
        Evaluator(agent=MockAgent(), benchmarks=[Benchmark.task_completion()]).evaluate(
            [{"input": "go", "context": {}}]
        )
    )
    text = results.render_summary()
    assert "Agent: mock-agent" in text
    assert "Benchmarks: 1" in text
    assert "Score: 1.0/100" in text
