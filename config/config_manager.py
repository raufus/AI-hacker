"""
Configuration management system
"""
import yaml
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file: str = "config/config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                user_config = yaml.safe_load(f) or {}
            
            # Merge with defaults to ensure all keys are present
            default_config = self._get_default_config()
            
            # Deep merge user config into defaults
            def merge_configs(default, user):
                for key, value in user.items():
                    if isinstance(value, dict) and isinstance(default.get(key), dict):
                        default[key] = merge_configs(default[key], value)
                    else:
                        default[key] = value
                return default

            self.config = merge_configs(default_config, user_config)
            self._save_config() # Save the merged config

        except Exception as e:
            self.logger.error(f"Error loading or merging config: {e}")
            self.config = self._get_default_config()
    
    def _create_default_config(self):
        """Create default configuration file from the default settings."""
        default_config = self._get_default_config()
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

    def _find_burp_suite_jar(self) -> Optional[str]:
        """Find the Burp Suite JAR file in the tools directory."""
        # Note: This now relies on the default config structure, not a live one.
        tools_dir_path = Path('tools')
        # Search for standard Burp Suite JAR names (Community and Pro)
        for pattern in ['burpsuite_community*.jar', 'burpsuite_pro*.jar']:
            found_files = list(tools_dir_path.rglob(pattern))
            if found_files:
                self.logger.info(f"Found Burp Suite JAR: {found_files[0]}")
                return str(found_files[0])
        self.logger.warning("Could not find a Burp Suite JAR file in the 'tools' directory.")
        return None

    def _get_default_config(self) -> Dict:
        """Get the complete default configuration dictionary."""
        default_config = {
            "system": {
                "log_level": "INFO",
                "max_concurrent_scans": 5,
                "resource_limits": {
                    "memory": 8192,  # MB
                    "cpu": 80,      # %
                    "disk": 90      # %
                }
            },
            "network": {
                "timeout": 30,      # seconds
                "retries": 3,
                "scan_rate": "normal",
                "max_connections": 100
            },
            "security": {
                "require_authorization": True,
                "max_scan_duration": 3600,  # seconds
                "log_all_actions": True,
                "allow_list": [
                    "192.168.1.0/24",
                    "10.0.0.0/8"
                ]
            },
            "database": {
                "path": "data/ai_hackeros.db",
                "backup_interval": 24,  # hours
                "max_backups": 7
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "max_requests": 100,
                "rate_limit": 60  # requests per minute
            },
            "tools": {
                "tools_path": "tools"
            },
            "metasploit": {
                "host": "127.0.0.1",
                "port": 55553,
                "user": "msf",
                "password": "msf_password"
            },
            "burp_suite": {
                # "jar_path": self._find_burp_suite_jar(), # Disabled to prioritize user-defined path
                "jar_path": None, # Default to None, will be loaded from user's config
                "proxy_host": "127.0.0.1",
                "proxy_port": 8080
            },
            "llm": {
                "model_path": "models/nous-hermes-2-solar-10.7b.Q4_K_M.gguf",
                "n_ctx": 4096,
                "n_threads": os.cpu_count() or 8, # Use available cores
                "n_gpu_layers": 40, # Default GPU layers
                "verbose": False
            }
        }
        return default_config
    
    def get_config(self, section: str = None) -> Dict:
        """Get configuration section"""
        if section:
            return self.config.get(section, {})
        return self.config

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting using dot notation."""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            self.logger.warning(f"Configuration key '{key}' not found. Using default: {default}")
            return default
    
    def update_config(self, section: str, data: Dict):
        """Update configuration section"""
        if section in self.config:
            self.config[section].update(data)
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_sections = ["system", "network", "security", "database", "api"]
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required section: {section}")
                return False
                
        # Validate system settings
        if not isinstance(self.config["system"]["max_concurrent_scans"], int):
            self.logger.error("Invalid max_concurrent_scans value")
            return False
            
        # Validate network settings
        if not isinstance(self.config["network"]["timeout"], int):
            self.logger.error("Invalid network timeout value")
            return False
            
        return True
    
    def get_resource_limits(self) -> Dict:
        """Get resource limits"""
        return self.config["system"]["resource_limits"]
    
    def get_security_settings(self) -> Dict:
        """Get security settings"""
        return self.config["security"]
    
    def get_api_settings(self) -> Dict:
        """Get API settings"""
        return self.config["api"]
    
    def get_database_settings(self) -> Dict:
        """Get database settings"""
        return self.config["database"]
