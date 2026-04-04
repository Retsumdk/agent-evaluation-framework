"""Agno adapter for agent evaluation."""

from ..protocol import AgentProtocol, AgentResult


def agno_adapter(agent):
    """Wrap an Agno agent for evaluation."""
    return AgnoAgentWrapper(agent)


class AgnoAgentWrapper(AgentProtocol):
    """Wrapper for Agno agents."""
    
    def __init__(self, agent, name: str = "agno_agent"):
        self.agent = agent
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            result = await self.agent.arun(input)
            
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
        if hasattr(self.agent, 'tools'):
            return [{'name': t.name, 'description': t.description} for t in self.agent.tools]
        return []
