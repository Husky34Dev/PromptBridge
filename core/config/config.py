"""
Generic Configuration Manager for Multi-Agent Chatbot Framework

This module handles all configuration loading, validation, and management
for the chatbot framework. It's designed to be easily customizable for
any client by modifying the client_config/ files.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigManager:
    """Central configuration manager for the chatbot framework"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.client_config_path = self.base_path / "client_config"
        self._config_cache = {}
        
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration from environment variables"""
        return {
            "groq_api_key": os.getenv("GROQ_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "groq_model": os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            "routing_model": os.getenv("ROUTING_MODEL", "llama-3.1-8b-instant"),
            "max_tokens": int(os.getenv("MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("TEMPERATURE", "0.7"))
        }
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return {
            "backend_host": os.getenv("BACKEND_HOST", "backend"),
            "backend_port": int(os.getenv("BACKEND_PORT", "8000")),
            "frontend_host": os.getenv("FRONTEND_HOST", "127.0.0.1"),
            "frontend_port": int(os.getenv("FRONTEND_PORT", "3000")),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
        }
    
    def get_client_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load client-specific configuration from JSON files
        
        Args:
            config_name: Name of the config file (without .json extension)
            
        Returns:
            Dictionary with configuration data
        """
        if config_name in self._config_cache:
            return self._config_cache[config_name]
            
        config_file = self.client_config_path / f"{config_name}.json"
        
        if not config_file.exists():
            print(f"Warning: Config file {config_file} not found, using defaults")
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._config_cache[config_name] = config
                return config
        except Exception as e:
            print(f"Error loading config {config_name}: {e}")
            return {}
    
    def get_branding_config(self) -> Dict[str, Any]:
        """Get branding configuration for the frontend"""
        default_branding = {
            "company_name": "Generic Chatbot",
            "primary_color": "#2563eb",
            "secondary_color": "#64748b",
            "logo_path": "/static/assets/logo.png",
            "favicon_path": "/static/assets/favicon.ico",
            "contact_email": "support@company.com",
            "support_phone": "+1 (555) 123-4567"
        }
        
        branding = self.get_client_config("branding")
        return {**default_branding, **branding}
    
    def get_agents_config(self) -> Dict[str, Any]:
        """Get agents configuration"""
        default_agents = {
            "default_agent": "general_assistant",
            "agents": [
                {
                    "name": "general_assistant",
                    "description": "General purpose assistant",
                    "system_prompt": "You are a helpful, professional assistant.",
                    "tools": [],
                    "routing_keywords": ["general", "help", "question"]
                }
            ],
            "routing_rules": {
                "default_fallback": "general_assistant",
                "confidence_threshold": 0.7
            }
        }
        
        agents = self.get_client_config("agents_config")
        return {**default_agents, **agents}
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration"""
        default_tools = {
            "tools": [],
            "tool_timeout": 30,
            "max_tool_calls": 5
        }
        
        tools = self.get_client_config("tools_schema")
        return {**default_tools, **tools}
    
    def get_entity_patterns(self) -> Dict[str, Any]:
        """Get entity extraction patterns"""
        default_patterns = {
            "patterns": {},
            "extraction_enabled": True
        }
        
        patterns = self.get_client_config("entity_patterns")
        return {**default_patterns, **patterns}
    
    def get_reference_map(self) -> Dict[str, Any]:
        """Get reference mapping configuration"""
        default_map = {
            "mappings": {},
            "auto_resolve": True
        }
        
        ref_map = self.get_client_config("reference_map")
        return {**default_map, **ref_map}
    
    def reload_config(self) -> None:
        """Clear cache and reload all configurations"""
        self._config_cache.clear()
        
    def validate_config(self) -> bool:
        """Validate that all required configurations are present"""
        api_config = self.get_api_config()
        
        if not api_config.get("groq_api_key") and not api_config.get("openai_api_key"):
            print("Warning: No API keys configured. Set GROQ_API_KEY or OPENAI_API_KEY")
            return False
            
        # Validate that client config files exist
        required_configs = ["branding", "agents_config", "tools_schema"]
        for config in required_configs:
            config_file = self.client_config_path / f"{config}.json"
            if not config_file.exists():
                print(f"Warning: Required config file {config}.json not found")
                
        return True

# Global configuration instance
config_manager = ConfigManager()

# Legacy compatibility - can be removed if not needed
GROQ_API_KEY = config_manager.get_api_config().get("groq_api_key")
GROQ_MODEL = config_manager.get_api_config().get("groq_model")
ROUTING_MODEL = config_manager.get_api_config().get("routing_model")
SERVER_URL = f"http://{config_manager.get_server_config()['backend_host']}:{config_manager.get_server_config()['backend_port']}"
