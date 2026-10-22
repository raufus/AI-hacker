
"""
AI Engine wrapper delegating to AI providers.
"""
import os
import logging
from typing import Optional, Dict, Any
from ai_providers.local_gguf import LocalGGUFProvider

class LLMEngine:
    def __init__(self, provider: str = "local_gguf", model_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.provider_name = provider

        if provider == "local_gguf":
            self.provider = LocalGGUFProvider(model_path)
        else:
            self.logger.warning(f"Provider {provider} not supported, falling back to local_gguf")
            self.provider = LocalGGUFProvider(model_path)

    def load_model(self) -> bool:
        return self.provider.load_model()

    def query(self, prompt: str, max_tokens: int = 1024) -> str:
        return self.provider.query(prompt, max_tokens)
    
    def ask_ai(self, prompt: str) -> str:
        """Simplified interface for asking AI"""
        return self.query(prompt)
    
    def generate_pentest_strategy(self, target_info: dict) -> str:
        return self.provider.generate_pentest_strategy(target_info)
    
    def analyze_vulnerability(self, vuln_data: dict) -> str:
        return self.provider.analyze_vulnerability(vuln_data)
