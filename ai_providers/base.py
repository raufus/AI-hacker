from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    """Base interface for all AI providers."""

    @abstractmethod
    def load_model(self) -> bool:
        """Initialize or load the model. Returns True if successful."""
        pass

    @abstractmethod
    def query(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """Send a prompt to the AI and get a response."""
        pass

    @abstractmethod
    def generate_pentest_strategy(self, target_info: Dict[str, Any]) -> str:
        """Generate penetration testing strategy based on target info."""
        pass

    @abstractmethod
    def analyze_vulnerability(self, vuln_data: Dict[str, Any]) -> str:
        """Analyze vulnerability data and suggest exploitation steps."""
        pass
