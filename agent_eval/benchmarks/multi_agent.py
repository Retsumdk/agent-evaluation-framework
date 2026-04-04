"""Multi-agent collaboration benchmark."""

from ..benchmark import Benchmark


def multi_agent(
    agents: list,
    workflow: str = "sequential"
) -> 'MultiAgentBenchmark':
    """Create a multi-agent benchmark."""
    return MultiAgentBenchmark(agents=agents, workflow=workflow)


class MultiAgentBenchmark(Benchmark):
    """Benchmark for multi-agent workflows."""
    
    def __init__(self, agents: list, workflow: str = "sequential"):
        super().__init__("multi_agent")
        self.agents = agents
        self.workflow = workflow
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        """Run multi-agent tasks."""
        # This runs the primary agent which should coordinate
        result = await agent.run(
            test_case.get('input', ''),
            test_case.get('context')
        )
        
        return {
            'success': result.success,
            'score': 1.0 if result.success else 0.0,
            'latency_ms': result.latency_ms,
            'workflow': self.workflow,
            'agents': len(self.agents),
        }
