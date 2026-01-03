"""Production-ready configuration for Performance Review AI system.

This module provides type-safe, validated configuration management using Pydantic Settings.

Usage:
    from demo.config import get_config
    
    config = get_config()
    llm = config.create_llm()
    loader = config.create_prompt_loader()
"""

import logging
from pathlib import Path
from typing import Literal, Optional

from langchain_openai import ChatOpenAI
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from demo.utils.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


# ============================================================================
# Main Configuration Class
# ============================================================================

class AppConfig(BaseSettings):
    """Application configuration with validation and type safety.
    
    Configuration is loaded from (in order of precedence):
    1. Environment variables
    2. .env file
    3. Default values
    
    Example .env file:
        OPENAI_API_KEY=sk-...
        ENVIRONMENT=development
        MODEL_NAME=gpt-4o
        TEMPERATURE=0.0
        DEBUG=false
    """
    
    # ========================================
    # Environment
    # ========================================
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Runtime environment",
        alias="ENVIRONMENT"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
        alias="DEBUG"
    )
    
    # ========================================
    # API Keys
    # ========================================
    openai_api_key: str = Field(
        ...,  # Required
        description="OpenAI API key",
        min_length=20,
        alias="OPENAI_API_KEY"
    )
    
    langsmith_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key for tracing (optional)",
        alias="LANGSMITH_API_KEY"
    )
    
    langsmith_project: str = Field(
        default="performance-review-ai",
        description="LangSmith project name",
        alias="LANGSMITH_PROJECT"
    )
    
    # ========================================
    # Model Configuration
    # ========================================
    model_name: str = Field(
        default="gpt-4o",
        description="OpenAI model name",
        alias="MODEL_NAME"
    )
    
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Model temperature (0.0 = deterministic, 2.0 = creative)",
        alias="TEMPERATURE"
    )
    
    max_tokens: int = Field(
        default=10000,
        gt=0,
        le=128000,
        description="Maximum tokens per request",
        alias="MAX_TOKENS"
    )
    
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for LLM calls",
        alias="MAX_RETRIES"
    )
    
    request_timeout: float = Field(
        default=60.0,
        gt=0,
        description="Request timeout in seconds",
        alias="REQUEST_TIMEOUT"
    )
    
    # ========================================
    # Paths
    # ========================================
    prompts_dir: Path = Field(
        default=Path("src/prompts"),
        description="Directory containing prompt templates",
        alias="PROMPTS_DIR"
    )
    
    data_dir: Path = Field(
        default=Path("data"),
        description="Directory for input/output data",
        alias="DATA_DIR"
    )
    
    output_dir: Path = Field(
        default=Path("data/output"),
        description="Directory for output files",
        alias="OUTPUT_DIR"
    )
    
    # ========================================
    # Performance Review Settings
    # ========================================
    enable_prompt_cache: bool = Field(
        default=True,
        description="Cache loaded prompts for performance",
        alias="ENABLE_PROMPT_CACHE"
    )
    
    enable_fact_checking: bool = Field(
        default=True,
        description="Enable fact-checking loop",
        alias="ENABLE_FACT_CHECKING"
    )
    
    max_fact_check_revisions: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum fact-check revision iterations",
        alias="MAX_FACT_CHECK_REVISIONS"
    )
    
    min_bullets: int = Field(
        default=3,
        ge=1,
        description="Minimum number of bullet points required",
        alias="MIN_BULLETS"
    )
    
    min_ratings: int = Field(
        default=2,
        ge=0,
        description="Minimum number of rated bullet points required",
        alias="MIN_RATINGS"
    )
    
    # ========================================
    # Logging
    # ========================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
        alias="LOG_LEVEL"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
        alias="LOG_FORMAT"
    )
    
    # ========================================
    # Pydantic Configuration
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,  # Allow both field name and alias
    )
    
    # ========================================
    # Validators
    # ========================================
    @field_validator("prompts_dir", "data_dir", "output_dir")
    @classmethod
    def ensure_directory_exists(cls, v: Path) -> Path:
        """Ensure directory exists or create it."""
        if not v.exists():
            logger.info(f"Creating directory: {v}")
            v.mkdir(parents=True, exist_ok=True)
        return v.resolve()  # Return absolute path
    
    @model_validator(mode="after")
    def validate_production_settings(self):
        """Validate configuration is appropriate for environment."""
        if self.environment == "production":
            if self.debug:
                raise ValueError("Debug mode cannot be enabled in production")
            
            if self.temperature > 0.5:
                logger.warning(
                    f"High temperature ({self.temperature}) in production. "
                    "This may lead to inconsistent results."
                )
            
            if not self.langsmith_api_key:
                logger.warning(
                    "LangSmith not configured for production. "
                    "Observability will be limited."
                )
        
        return self
    
    # ========================================
    # Properties
    # ========================================
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    # ========================================
    # Factory Methods
    # ========================================
    def create_llm(self) -> ChatOpenAI:
        """Create configured LLM instance.
        
        Returns:
            ChatOpenAI instance with retry logic
        """
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.request_timeout,
            api_key=self.openai_api_key,
        )
        
        # Add retry logic
        llm = llm.with_retry(
            retry_if_exception_type=(Exception,),
            wait_exponential_jitter=True,
            stop_after_attempt=self.max_retries,
        )
        
        return llm
    
    def create_prompt_loader(self) -> PromptLoader:
        """Create configured PromptLoader instance.
        
        Returns:
            PromptLoader instance
        """
        return PromptLoader(
            prompts_dir=self.prompts_dir,
            enable_cache=self.enable_prompt_cache,
            validate_on_load=not self.is_production,  # Skip validation in prod for speed
        )
    
    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=self.log_format,
        )
        
        # Set LangChain logging
        logging.getLogger("langchain").setLevel(self.log_level)
        logging.getLogger("openai").setLevel(self.log_level)
        
        logger.info(f"Logging configured: level={self.log_level}")
    
    def setup_langsmith(self) -> None:
        """Configure LangSmith tracing if API key is available."""
        import os
        
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_TRACING_V2"] = "true"
            os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
            
            logger.info(f"LangSmith tracing enabled: project={self.langsmith_project}")
        else:
            logger.debug("LangSmith API key not provided, tracing disabled")
    
    def model_dump_safe(self) -> dict:
        """Dump config without exposing secrets.
        
        Returns:
            Dictionary with secrets masked
        """
        config_dict = self.model_dump()
        
        # Mask secrets
        if "openai_api_key" in config_dict:
            config_dict["openai_api_key"] = "***MASKED***"
        if "langsmith_api_key" in config_dict and config_dict["langsmith_api_key"]:
            config_dict["langsmith_api_key"] = "***MASKED***"
        
        return config_dict


# ============================================================================
# Singleton Pattern (Optional)
# ============================================================================

_config_instance: Optional[AppConfig] = None


def get_config(force_reload: bool = False) -> AppConfig:
    """Get application configuration (singleton).
    
    Args:
        force_reload: Force reload configuration from environment
        
    Returns:
        AppConfig instance
    
    Example:
        >>> config = get_config()
        >>> llm = config.create_llm()
    """
    global _config_instance
    
    if _config_instance is None or force_reload:
        _config_instance = AppConfig()
        _config_instance.setup_logging()
        _config_instance.setup_langsmith()
        
        logger.info(
            f"Configuration loaded: environment={_config_instance.environment}, "
            f"model={_config_instance.model_name}"
        )
    
    return _config_instance


# ============================================================================
# Testing Utilities
# ============================================================================

def create_test_config(**overrides) -> AppConfig:
    """Create configuration for testing.
    
    Args:
        **overrides: Field overrides
        
    Returns:
        AppConfig instance with test defaults
        
    Example:
        >>> config = create_test_config(
        ...     model_name="gpt-4o-mini",
        ...     enable_fact_checking=False
        ... )
    """
    defaults = {
        "openai_api_key": "test-key-12345678901234567890",
        "environment": "development",
        "debug": True,
        "enable_prompt_cache": False,  # Disable cache in tests
        "max_fact_check_revisions": 1,  # Faster tests
        "log_level": "DEBUG",
    }
    
    defaults.update(overrides)
    return AppConfig(**defaults)


# ============================================================================
# CLI Utilities
# ============================================================================

def print_config() -> None:
    """Print current configuration (for debugging)."""
    config = get_config()
    
    print("=" * 60)
    print("Application Configuration")
    print("=" * 60)
    
    safe_config = config.model_dump_safe()
    
    for key, value in safe_config.items():
        print(f"{key:30} = {value}")
    
    print("=" * 60)


if __name__ == "__main__":
    # Print current configuration
    print_config()
