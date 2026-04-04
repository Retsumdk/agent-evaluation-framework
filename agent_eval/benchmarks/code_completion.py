"""Code completion benchmark."""

from ..benchmark import Benchmark


def code_completion(
    test_suite: str = None,
    language: str = "python",
    timeout: int = 30
) -> 'CodeCompletionBenchmark':
    """Create a code completion benchmark."""
    return CodeCompletionBenchmark(
        test_suite=test_suite,
        language=language,
        timeout=timeout
    )


class CodeCompletionBenchmark(Benchmark):
    """Benchmark for code generation tasks."""
    
    def __init__(self, test_suite: str = None, language: str = "python", timeout: int = 30):
        super().__init__("code_completion")
        self.test_suite = test_suite
        self.language = language
        self.timeout = timeout
    
    async def run(self, agent, test_case: dict, iterations: int = 1) -> dict:
        """Run code completion tasks."""
        result = await agent.run(
            test_case.get('input', ''),
            test_case.get('context')
        )
        
        return {
            'success': result.success,
            'score': 1.0 if result.success else 0.0,
            'latency_ms': result.latency_ms,
            'language': self.language,
        }
