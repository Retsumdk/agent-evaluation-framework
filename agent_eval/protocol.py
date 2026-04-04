"""
Agent protocol definition.
"""

from typing import Any, Protocol, Optional
from dataclasses import dataclass


@dataclass
class AgentResult:
    """Result from an agent run."""
    output: str
    success: bool
    tools_used: list[dict] = None
    latency_ms: float = 0
    error: Optional[str] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if self.metadata is None:
            self.metadata = {}


class AgentProtocol(Protocol):
    """
    Protocol defining the interface for agents to be evaluated.
    
    Any agent implementing these methods can be evaluated by the framework.
    """
    
    @property
    def name(self) -> str:
        """Agent name for reporting."""
        ...
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        """
        Run the agent with input and optional context.
        
        Args:
            input: The input prompt/task
            context: Optional context dict
            
        Returns:
            AgentResult with output and metadata
        """
        ...
    
    async def tools(self) -> list[dict]:
        """
        Return list of available tools.
        
        Returns:
            List of tool definitions with 'name' and 'description'
        """
        ...


class SimpleAgent:
    """
    Simple agent implementation for testing and examples.
    """
    
    def __init__(
        self,
        name: str = "simple_agent",
        handler: callable = None,
        tools: list[dict] = None,
    ):
        self._name = name
        self._handler = handler
        self._tools = tools or []
    
    @property
    def name(self) -> str:
        return self._name
    
    async def run(self, input: str, context: dict = None) -> AgentResult:
        import time
        start = time.time()
        
        try:
            if self._handler:
                output = await self._handler(input, context)
            else:
                output = f"Processed: {input}"
            
            return AgentResult(
                output=output,
                success=True,
                tools_used=self._tools,
                latency_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return AgentResult(
                output="",
                success=False,
                tools_used=self._tools,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )
    
    async def tools(self) -> list[dict]:
        return self._tools
