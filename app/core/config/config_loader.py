"""
Configuration Loader
Utilities for loading and validating YAML configuration files
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .settings import get_settings

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

class ConfigLoader:
    """Configuration loader with validation"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def load_agent_config(self) -> Dict[str, Any]:
        """Load and validate agent configuration from YAML file"""
        config_path = self.settings.get_agent_config_path()
        
        if not config_path.exists():
            raise ConfigurationError(f"Agent configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            self._validate_agent_config(config)
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax in {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading agent config: {e}")
    
    def _validate_agent_config(self, config: Dict[str, Any]) -> None:
        """Validate agent configuration structure"""
        required_sections = [
            "agent_info",
            "system_prompt", 
            "planning_prompt",
            "synthesis_prompt",
            "tools"
        ]
        
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section: {section}")
        
        # Validate agent_info
        agent_info = config["agent_info"]
        required_info = ["name", "version", "description", "domain"]
        for field in required_info:
            if field not in agent_info:
                raise ConfigurationError(f"Missing required field in agent_info: {field}")
        
        # Validate tools section
        tools = config["tools"]
        required_tools = ["settlement_calculator", "bearing_capacity_calculator"]
        for tool in required_tools:
            if tool not in tools:
                raise ConfigurationError(f"Missing required tool configuration: {tool}")
    
    def get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        config = self.load_agent_config()
        return config["system_prompt"]
    
    def get_planning_prompt(self) -> str:
        """Get planning prompt template"""
        config = self.load_agent_config()
        return config["planning_prompt"]
    
    def get_synthesis_prompt(self) -> str:
        """Get synthesis prompt template"""
        config = self.load_agent_config()
        return config["synthesis_prompt"]
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool"""
        config = self.load_agent_config()
        tools = config.get("tools", {})
        
        if tool_name not in tools:
            raise ConfigurationError(f"Tool configuration not found: {tool_name}")
        
        return tools[tool_name]
    
    def get_retrieval_config(self) -> Dict[str, Any]:
        """Get RAG retrieval configuration"""
        config = self.load_agent_config()
        return config.get("retrieval", {
            "max_documents": self.settings.TOP_K_RETRIEVAL,
            "similarity_threshold": self.settings.SIMILARITY_THRESHOLD
        })
    
    def get_response_format_config(self) -> Dict[str, Any]:
        """Get response formatting configuration"""
        config = self.load_agent_config()
        return config.get("response_format", {
            "max_length": 2000,
            "include_sources": True,
            "include_calculations": True,
            "professional_tone": True
        })
    
    def get_error_messages(self) -> Dict[str, str]:
        """Get error message templates"""
        config = self.load_agent_config()
        return config.get("error_messages", {
            "calculation_error": "Calculation error occurred",
            "retrieval_error": "Could not retrieve information",
            "invalid_input": "Invalid input parameters",
            "general_error": "An error occurred"
        })
    
    def get_behavior_config(self) -> Dict[str, Any]:
        """Get agent behavior configuration"""
        config = self.load_agent_config()
        return config.get("behavior", {
            "conversation_style": "professional",
            "detail_level": "comprehensive", 
            "citation_style": "academic"
        })
    
def get_config_loader() -> ConfigLoader:
    """Get configuration loader instance"""
    return ConfigLoader()

# Convenience functions for common configurations
def get_system_prompt() -> str:
    """Get system prompt"""
    return get_config_loader().get_system_prompt()

def get_planning_prompt() -> str:
    """Get planning prompt"""
    return get_config_loader().get_planning_prompt()

def get_synthesis_prompt() -> str:
    """Get synthesis prompt"""
    return get_config_loader().get_synthesis_prompt()

def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """Get tool configuration"""
    return get_config_loader().get_tool_config(tool_name)

def get_retrieval_config() -> Dict[str, Any]:
    """Get retrieval configuration"""
    return get_config_loader().get_retrieval_config()

def validate_configuration() -> bool:
    """Validate all configuration files and settings"""
    try:
        # Test settings loading
        settings = get_settings()
        print(f"✅ Settings loaded successfully")
        print(f"   - OpenAI Model: {settings.OPENAI_MODEL}")
        print(f"   - Environment: {settings.ENVIRONMENT}")
        print(f"   - Log Level: {settings.LOG_LEVEL}")
        
        # Test agent config loading
        config_loader = get_config_loader()
        agent_config = config_loader.load_agent_config()
        print(f"✅ Agent config loaded successfully")
        print(f"   - Agent: {agent_config['agent_info']['name']} v{agent_config['agent_info']['version']}")
        print(f"   - Domain: {agent_config['agent_info']['domain']}")
        
        # Test required paths
        agent_config_path = settings.get_agent_config_path()
        logs_dir = settings.get_logs_directory()
        print(f"✅ Paths validated")
        print(f"   - Agent config: {agent_config_path}")
        print(f"   - Logs directory: {logs_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False