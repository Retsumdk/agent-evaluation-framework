"""Braintrust integration for evaluation."""

class BraintrustCallback:
    """Callback for Braintrust integration."""
    
    def __init__(self, project: str = "agent-eval", api_key: str = None):
        self.project = project
        self.api_key = api_key
    
    def on_start(self, test_case: dict):
        """Called when a test starts."""
        pass
    
    def on_complete(self, result: dict):
        """Called when a test completes."""
        pass
    
    def on_error(self, error: Exception):
        """Called on error."""
        pass


def braintrust_callback(project: str = "agent-eval", **kwargs) -> BraintrustCallback:
    """Create a Braintrust callback."""
    return BraintrustCallback(project=project, **kwargs)
