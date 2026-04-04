"""
OpenAI Agents SDK adapter for agent evaluation.
"""

from ..protocol import AgentProtocol, AgentResult


def openai_adapter(agent):
    """Wrap an OpenAI Agents SDK agent for evaluation."""
    return OpenAIAgentWrapper(agent)


class OpenAIAgentWrapper(AgentProtocol):
    """Wrapper for OpenAI Agents SDK agents."""
    
    def __init__(self, agent, name: str = "openai_agent"):
        self.agent = agent
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            # Run the agent
            result = await self.agent.run(input)
            
            return AgentResult(
                output=result.output,
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
            return [
                {'name': t.name, 'description': t.description}
                for t in self.agent.tools
            ]
        return []
