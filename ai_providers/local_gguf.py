import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from .base import AIProvider

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class LocalGGUFProvider(AIProvider):
    def __init__(self, model_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path or "models/nous-hermes-2-solar-10.7b.Q4_K_M.gguf"
        self.llm = None
        self.is_loaded = False

    def load_model(self) -> bool:
        if Llama is None:
            self.logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return False

        try:
            if not os.path.exists(self.model_path):
                self.logger.error(f"Model file not found: {self.model_path}")
                return False

            cpu_count = os.cpu_count() or 4
            gpu_layers = 20

            self.logger.info(f"Loading GGUF model: {self.model_path}")
            self.logger.info(f"Using {cpu_count} CPU threads and offloading {gpu_layers} layers to GPU.")

            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,
                n_threads=cpu_count,
                n_gpu_layers=gpu_layers,
                verbose=False
            )
            self.is_loaded = True
            self.logger.info("Model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.logger.warning("Falling back to CPU-only mode.")
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=4096, n_threads=os.cpu_count(), verbose=False)
                self.is_loaded = True
                self.logger.info("Model loaded successfully in CPU-only mode.")
                return True
            except Exception as fallback_e:
                self.logger.error(f"Failed to load model in CPU-only mode: {fallback_e}")
                return False

    def query(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        if not self.is_loaded:
            if not self.load_model():
                return "Error: Model not available"

        try:
            response = self.llm(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["Human:", "Assistant:", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            return f"Error: {str(e)}"

    def generate_pentest_strategy(self, target_info: Dict[str, Any]) -> str:
        prompt = f"""
        You are a cybersecurity expert. Based on the following target information,
        suggest the next penetration testing steps:

        Target: {target_info.get('target', 'Unknown')}
        Open Ports: {target_info.get('ports', [])}
        Services: {target_info.get('services', [])}
        Technologies: {target_info.get('technologies', [])}

        Provide specific recommendations for:
        1. Which vulnerabilities to test for
        2. Which tools to use
        3. Attack vectors to explore
        4. Exploitation techniques

        Response:
        """
        return self.query(prompt, max_tokens=500)

    def analyze_vulnerability(self, vuln_data: Dict[str, Any]) -> str:
        prompt = f"""
        Analyze this vulnerability and provide exploitation guidance:

        Vulnerability: {vuln_data.get('name', 'Unknown')}
        Severity: {vuln_data.get('severity', 'Unknown')}
        Description: {vuln_data.get('description', 'No description')}
        Target: {vuln_data.get('target', 'Unknown')}

        Provide:
        1. Exploitation difficulty
        2. Required tools
        3. Step-by-step exploitation approach
        4. Potential impact

        Response:
        """
        return self.query(prompt, max_tokens=400)
