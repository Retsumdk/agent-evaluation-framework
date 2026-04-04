"""
LangChain adapter for agent evaluation.
"""

from ..protocol import AgentProtocol, AgentResult


def langchain_adapter(chain):
    """
    Wrap a LangChain agent/chain for evaluation.
    
    Usage:
        from langchain.agents import load_agent
        from agent_eval.adapters import langchain_adapter
        
        agent = load_agent(...)
        eval_agent = langchain_adapter(agent)
        
        evaluator = Evaluator(agent=eval_agent, benchmarks=[...])
    """
    return LangChainAgentWrapper(chain)


class LangChainAgentWrapper(AgentProtocol):
    """Wrapper for LangChain agents."""
    
    def __init__(self, chain, name: str = "langchain_agent"):
        self.chain = chain
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            # Run the chain with input
            # LangChain chains can be sync or async
            try:
                output = await self.chain.ainvoke(
                    {"input": input, **(context or {})}
                )
            except TypeError:
                # Fallback to sync invoke
                output = self.chain.invoke(
                    {"input": input, **(context or {})}
                )
            
            # Extract output text
            if isinstance(output, dict):
                output = output.get('output', str(output))
            
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
        # Try to extract tools from the chain
        tools = []
        if hasattr(self.chain, 'tools'):
            for tool in self.chain.tools:
                tools.append({
                    'name': getattr(tool, 'name', tool.__class__.__name__),
                    'description': getattr(tool, 'description', ''),
                })
        return tools
