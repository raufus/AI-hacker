"""
AI-Powered Payload Crafting Module.

This module uses a local GGUF language model to generate context-aware and evasive payloads
for various penetration testing scenarios, such as reverse shells, SQL injection, and XSS.
"""
import logging
from typing import Dict, Any
from llama_cpp import Llama
from config.config_manager import ConfigManager

class PayloadCrafter:
    """Crafts payloads using an AI model based on the target context."""

    def __init__(self):
        """Initializes the PayloadCrafter, loading the AI model."""
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.llm = None
        self._load_model()

    def _load_model(self):
        """Loads the GGUF model from the path specified in the config."""
        model_path = self.config.get_setting('llm.model_path')
        if not model_path:
            self.logger.error("LLM model path is not configured. Payload crafter cannot operate.")
            return

        try:
            self.logger.info(f"Loading GGUF model from: {model_path}")
            # Model parameters can be fine-tuned in config.yaml
            self.llm = Llama(
                model_path=model_path,
                n_ctx=self.config.get_setting('llm.n_ctx', 4096),
                n_gpu_layers=self.config.get_setting('llm.n_gpu_layers', -1), # -1 for all layers on GPU
                verbose=self.config.get_setting('llm.verbose', False)
            )
            self.logger.info("GGUF model loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load the GGUF model: {e}")
            self.llm = None

    def generate_payload(self, context: Dict[str, Any]) -> str:
        """
        Generates a payload based on the provided context using the AI model.

        Args:
            context: A dictionary containing information about the target, such as:
                     'type': (e.g., 'reverse_shell', 'sqli', 'xss')
                     'target_os': (e.g., 'windows', 'linux')
                     'lhost': The local host for reverse shells.
                     'lport': The local port for reverse shells.
                     'bad_chars': A string of characters to avoid in the payload.
                     'technique': Specific technique (e.g., 'powershell_tcp', 'python_pty')

        Returns:
            A string containing the generated payload, or an empty string on failure.
        """
        if not self.llm:
            self.logger.error("Cannot generate payload: LLM is not loaded.")
            return ""

        prompt = self._create_prompt_from_context(context)
        self.logger.info(f"Generating payload with context: {context}")

        try:
            response = self.llm(
                prompt,
                max_tokens=self.config.get_setting('llm.max_tokens', 512),
                stop=["```", "\n\n"], # Stop generation at the end of a code block or paragraph
                temperature=self.config.get_setting('llm.temperature', 0.3),
                echo=False
            )
            
            payload = response['choices'][0]['text'].strip()
            # Clean up the payload from any surrounding text or code block markers
            if '```' in payload:
                payload = payload.split('```')[1].strip()
            
            self.logger.info(f"Successfully generated payload.")
            self.logger.debug(f"Generated Payload: \n{payload}")
            return payload

        except Exception as e:
            self.logger.error(f"An error occurred during payload generation: {e}")
            return ""

    def suggest_msf_payload(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggests a Metasploit payload and its options based on the context.

        Args:
            context: A dictionary containing 'exploit_name', 'target_os', 'lhost', 'lport'.

        Returns:
            A dictionary like {'name': 'windows/meterpreter/reverse_tcp', 'options': {'LHOST': '1.2.3.4', 'LPORT': 4444}}
        """
        if not self.llm:
            self.logger.error("Cannot suggest payload: LLM is not loaded.")
            return {}

        prompt = self._create_msf_prompt_from_context(context)
        self.logger.info(f"Suggesting Metasploit payload with context: {context}")

        try:
            response = self.llm(
                prompt,
                max_tokens=150,
                stop=["\n\n"],
                temperature=0.2,
                echo=False
            )
            
            suggestion_text = response['choices'][0]['text'].strip()
            # Expected format: PAYLOAD: windows/meterpreter/reverse_tcp, OPTIONS: {'LHOST': '10.0.0.1', 'LPORT': 4444}
            payload_name = suggestion_text.split('PAYLOAD:')[1].split(',')[0].strip()
            options_str = suggestion_text.split('OPTIONS:')[1].strip()
            options = eval(options_str) # Use eval carefully, assuming trusted LLM output format

            result = {'name': payload_name, 'options': options}
            self.logger.info(f"AI suggested Metasploit payload: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to parse AI suggestion for MSF payload: {e}")
            self.logger.debug(f"Raw AI output: {suggestion_text}")
            return {}

    def _create_msf_prompt_from_context(self, context: Dict[str, Any]) -> str:
        """
        Creates a prompt to ask the AI for a Metasploit payload suggestion.
        """
        prompt = (
            "You are a Metasploit framework expert. Your task is to select the best payload for a given exploit and target. "
            "Provide the full payload name and its required options in a single line."
            "Format your response EXACTLY as follows: PAYLOAD: <payload_name>, OPTIONS: {'LHOST': '<lhost>', 'LPORT': <lport>}"
        )

        prompt += f"\n\n--- CONTEXT ---"
        prompt += f"\nExploit: {context.get('exploit_name', 'unknown')}"
        prompt += f"\nTarget OS: {context.get('target_os', 'linux')}"
        prompt += f"\nLHOST: {context.get('lhost', '127.0.0.1')}"
        prompt += f"\nLPORT: {context.get('lport', 4444)}"
        prompt += "\n\n--- RESPONSE ---"
        return prompt

    def _create_prompt_from_context(self, context: Dict[str, Any]) -> str:
        """
        Creates a detailed, role-play prompt for the AI model to generate a payload.
        """
        # Base prompt: Role-play as a master penetration tester
        prompt = (
            "You are a world-class cybersecurity expert and master penetration tester. "
            "Your task is to generate a raw, functional payload for a specific scenario. "
            "The payload must be stealthy, efficient, and ready to execute. "
            "Provide ONLY the raw code for the payload, without any explanations, comments, or markdown."
        )

        # Add context-specific instructions
        p_type = context.get('type', 'generic')
        prompt += f"\n\n--- CONTEXT ---\nPayload Type: {p_type}"

        if p_type == 'reverse_shell':
            prompt += f"\nTarget OS: {context.get('target_os', 'linux')}"
            prompt += f"\nLHOST: {context.get('lhost', '127.0.0.1')}"
            prompt += f"\nLPORT: {context.get('lport', 4444)}"
            prompt += f"\nTechnique: {context.get('technique', 'Provide the most reliable one.')}"
        
        elif p_type == 'sqli':
            prompt += f"\nDatabase Type: {context.get('db_type', 'generic SQL')}"
            prompt += f"\nGoal: {context.get('goal', 'dump user table')}"

        if context.get('bad_chars'):
            prompt += f"\nAvoid these characters: \"{context['bad_chars']}\""
        
        prompt += "\n\n--- PAYLOAD ---\n"
        return prompt
