"""CrewAI adapter for agent evaluation."""

from ..protocol import AgentProtocol, AgentResult


def crewai_adapter(crew):
    """Wrap a CrewAI crew for evaluation."""
    return CrewAIWrapper(crew)


class CrewAIWrapper(AgentProtocol):
    """Wrapper for CrewAI crews."""
    
    def __init__(self, crew, name: str = "crewai_agent"):
        self.crew = crew
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            result = await self.crew.kickoff(inputs={"task": input, **(context or {})})
            
            return AgentResult(
                output=str(result),
                success=True,
                latency_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return AgentResult(
                output="",
                success=False,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )
    
    async def tools(self) -> list[dict]:
        if hasattr(self.crew, 'agents'):
            tools = []
            for agent in self.crew.agents:
                if hasattr(agent, 'tools'):
                    tools.extend([
                        {'name': t.name, 'description': t.description}
                        for t in agent.tools
                    ])
            return tools
        return []
