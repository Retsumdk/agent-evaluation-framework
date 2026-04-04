"""LangGraph adapter for agent evaluation."""

from ..protocol import AgentProtocol, AgentResult


def langgraph_adapter(graph, config: dict = None):
    """Wrap a LangGraph workflow for evaluation."""
    return LangGraphAgentWrapper(graph, config)


class LangGraphAgentWrapper(AgentProtocol):
    """Wrapper for LangGraph workflows."""
    
    def __init__(self, graph, config: dict = None, name: str = "langgraph_agent"):
        self.graph = graph
        self.config = config or {}
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            result = await self.graph.ainvoke(
                {"input": input, **(context or {})},
                self.config
            )
            
            output = result.get('output', str(result)) if isinstance(result, dict) else str(result)
            
            return AgentResult(
                output=str(output),
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
        return []
