# Agent Evaluation Framework

[![Build](https://github.com/Retsumdk/agent-evaluation-framework/workflows/CI/badge.svg)](https://github.com/Retsumdk/agent-evaluation-framework/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)](release)

A comprehensive, production-ready framework for evaluating AI agents across multiple dimensions of capability. Built for teams who need to benchmark, test, and improve their AI agents with measurable metrics.

## Why This Framework

Research shows leading AI agents complete only 30-35% of multi-step tasks[^1]. Without proper evaluation, teams ship agents that fail silently in production. This framework provides structured evaluation across:

- **Task completion** - Does the agent achieve its goals?
- **Tool usage efficiency** - Does it use the right tools, not too many?
- **Error recovery** - Can it recover from failures?
- **Latency** - Is it fast enough for user-facing apps?
- **Consistency** - Does it produce reliable results across runs?

## Installation

```bash
pip install agent-evaluation-framework
```

Or add to your project:

```bash
poetry add agent-evaluation-framework
```

## Quick Start

```python
from agent_eval import Evaluator, Benchmark, Metrics

# Define your agent
async def my_agent(input: str) -> str:
    # Your agent implementation
    return await agent.complete(input)

# Create evaluator
evaluator = Evaluator(
    agent=my_agent,
    benchmarks=[
        Benchmark.task_completion(),
        Benchmark.tool_efficiency(),
        Benchmark.error_recovery(),
        Benchmark.latency(),
    ],
    metrics=Metrics.default()
)

# Run evaluation
results = await evaluator.evaluate(
    test_suite="path/to/test_cases.json",
    iterations=3
)

# View results
print(results.summary())
print(results.metrics())
```

## Core Concepts

### Benchmarks

Benchmarks define what to test:

| Benchmark | What It Measures |
|-----------|-----------------|
| `task_completion` | Did the agent achieve the goal? |
| `tool_efficiency` | Optimal tool usage |
| `error_recovery` | Recovery from failures |
| `latency` | Response time |
| `consistency` | Stability across runs |
| `context_usage` | Token efficiency |

### Metrics

The framework calculates:

- **Success Rate** - % of tasks completed
- **Average Latency** - P50, P95, P99
- **Token Efficiency** - Tokens per successful task
- **Error Rate** - Failure frequency
- **Recovery Rate** - Failures that were recovered

### Test Suites

Define test cases in JSON:

```json
[
  {
    "id": "task_001",
    "input": "Find all files modified yesterday",
    "expected": "List of file paths",
    "context": {
      "files": ["a.txt", "b.txt"],
      "last_modified": "2025-01-01"
    }
  }
]
```

## Supported Agent Types

Works with any agent that implements the `AgentProtocol`:

```python
from agent_eval import AgentProtocol

class MyAgent(AgentProtocol):
    async def run(self, input: str, context: dict = None) -> str:
        # Your implementation
        pass
    
    async def tools(self) -> list[dict]:
        # Return available tools
        return [{"name": "search", "description": "Search files"}]
```

### Framework Adapters

Built-in adapters for popular frameworks:

- OpenAI Agents SDK
- LangChain Agents
- LangGraph
- Agno
- CrewAI
- Custom (bring your own)

```python
from agent_eval.adapters import langchain_adapter, openai_adapter

# Use with LangChain
evaluator = Evaluator(
    agent=langchain_adapter(my_langchain_agent),
    benchmarks=[...]
)
```

## Running Benchmarks

### Terminal-Bench Style

Test CLI capabilities:

```python
from agent_eval.benchmarks import terminal_bench

results = await evaluator.evaluate(
    benchmark=terminal_bench(
        tasks=[
            {"command": "ls -la", "expected_output": "file listing"},
            {"command": "grep -r 'pattern' .", "expected_output": "matches"},
        ]
    )
)
```

### Code Completion

Test code generation:

```python
from agent_eval.benchmarks import code_completion

results = await evaluator.evaluate(
    benchmark=code_completion(
        test_suite="tests/code_tasks.json",
        language="python",
        timeout=30
    )
)
```

### Multi-Agent

Test agent collaboration:

```python
from agent_eval.benchmarks import multi_agent

results = await evaluator.evaluate(
    benchmark=multi_agent(
        agents=[researcher, writer, reviewer],
        workflow="research_write_review"
    )
)
```

## Configuration

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-antik...

# Custom
AGENT_EVAL_LOG_LEVEL=INFO
AGENT_EVAL_DB_PATH=./eval.db
```

### Configuration File

```yaml
# eval.yaml
evaluation:
  iterations: 3
  timeout: 60
  parallel: 4
  
benchmarks:
  task_completion:
    threshold: 0.8
  latency:
    p95_threshold_ms: 5000
    
storage:
  backend: sqlite
  path: ./eval.db
  
reporting:
  format: json
  output: ./results/
```

## Output

The evaluator returns detailed results:

```python
results = await evaluator.evaluate(...)

# Summary
print(results.summary())
# Agent: my_agent
# Benchmarks: 4
# Success Rate: 85.2%
# Avg Latency: 2.3s
# Score: 82/100

# Detailed metrics
print(results.metrics())
# {
#   "task_completion": {"success_rate": 0.89, "score": 89},
#   "tool_efficiency": {"score": 78},
#   "error_recovery": {"score": 85},
#   "latency": {"score": 75}
# }

# Export
results.to_json("./results.json")
results.to_csv("./results.csv")
results.to_prometheus(port=9090)
```

## Integrations

### CI/CD

```yaml
# .github/workflows/eval.yml
- name: Agent Evaluation
  run: |
    agent-eval run \
      --agent ./agent.py \
      --benchmarks task_completion,latency \
      --threshold 75
```

### LangSmith

```python
from agent_eval.integrations import langsmith

evaluator = Evaluator(
    agent=my_agent,
    callbacks=[langsmith_callback(project="my-agent")]
)
```

### Braintrust

```python
from agent_eval.integrations import braintrust

evaluator = Evaluator(
    agent=my_agent,
    callbacks=[braintrust_callback(project="my-agent")]
)
```

## Extending

### Custom Benchmark

```python
from agent_eval import Benchmark, BenchmarkBuilder

class MyBenchmark(BenchmarkBuilder):
    name = "my_custom"
    
    async def run(self, agent, test_case):
        result = await agent.run(test_case.input)
        return self.score(result, test_case.expected)
    
    def score(self, result, expected) -> float:
        return float(result == expected)
```

### Custom Metrics

```python
from agent_eval import MetricsBuilder

class MyMetrics(MetricsBuilder):
    name = "my_metrics"
    
    async def calculate(self, traces):
        return {
            "my_metric": sum(t.my_value for t in traces) / len(traces)
        }
```

## API

### Evaluator

```python
class Evaluator:
    def __init__(
        self,
        agent: AgentProtocol,
        benchmarks: list[Benchmark],
        metrics: Metrics = Metrics.default()
    ):
        ...
    
    async def evaluate(
        self,
        test_suite: str | list[dict],
        iterations: int = 1,
        parallel: int = 1
    ) -> EvaluationResults:
        ...
```

### Benchmark

```python
class Benchmark:
    @staticmethod
    def task_completion(threshold: float = 0.8) -> Benchmark:
        ...
    
    @staticmethod
    def tool_efficiency(
        max_tools: int = 10,
        optimal_range: tuple = (1, 5)
    ) -> Benchmark:
        ...
    
    @staticmethod
    def error_recovery(
        max_retries: int = 3
    ) -> Benchmark:
        ...
    
    @staticmethod
    def latency(
        p50_threshold_ms: int = 1000,
        p95_threshold_ms: int = 5000
    ) -> Benchmark:
        ...
```

## 🔗 Related Repos

- [agent-a2a-bridge](https://github.com/Retsumdk/agent-a2a-bridge) — A2A protocol for multi-agent communication
- [agent-memory-store](https://github.com/Retsumdk/agent-memory-store) — Persistent memory for AI agents
- [prompt-version-control](https://github.com/Retsumdk/prompt-version-control) — Version control for AI prompts

## License

MIT

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

[^1]: https://introl.com/blog/ai-agents-infrastructure-building-reliable-agentic-systems-guide
