"""Configuration Best Practices - From Basic to Production-Ready.

This guide shows the evolution of config.py from simple to enterprise-grade,
following 12-Factor App principles and modern Python best practices.
"""

from pathlib import Path
from typing import Optional, Literal
from enum import Enum
import os


# ============================================================================
# ❌ ANTI-PATTERN 1: Hardcoded Values (Never do this)
# ============================================================================

class BadConfig:
    """DON'T DO THIS - Hardcoded values, secrets in code."""
    
    OPENAI_API_KEY = "sk-1234567890abcdef"  # ❌ Secret in code!
    MODEL_NAME = "gpt-4o"  # ❌ Can't change without code change
    PROMPTS_DIR = "/absolute/path/to/prompts"  # ❌ Breaks on other machines
    TEMPERATURE = 0.7


# ============================================================================
# ⚠️ ANTI-PATTERN 2: Environment Variables Only (Better but fragile)
# ============================================================================

class BetterButFragileConfig:
    """Better, but no validation or defaults."""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ⚠️ Could be None
    MODEL_NAME = os.getenv("MODEL_NAME")  # ⚠️ No default
    TEMPERATURE = float(os.getenv("TEMPERATURE"))  # ⚠️ Crashes if not set


# ============================================================================
# ✅ APPROACH 1: Simple Config with Defaults (Good for POCs)
# ============================================================================

class SimpleConfig:
    """Simple approach: Environment variables with sensible defaults.
    
    Pros:
    - Easy to understand
    - No dependencies
    - Works for small projects
    
    Cons:
    - No validation
    - No type safety
    - Manual type conversion
    """
    
    def __init__(self):
        # API Keys (required, fail fast)
        self.openai_api_key = self._get_required("OPENAI_API_KEY")
        
        # Model settings (with defaults)
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o")
        self.temperature = float(os.getenv("TEMPERATURE", "0.0"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "10000"))
        
        # Paths (relative to project root)
        self.prompts_dir = Path(os.getenv("PROMPTS_DIR", "src/prompts"))
        self.data_dir = Path(os.getenv("DATA_DIR", "data"))
        
        # Feature flags
        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    def _get_required(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable '{key}' not set. "
                f"Please set it in your .env file or environment."
            )
        return value


# ============================================================================
# ✅ APPROACH 2: Pydantic Settings (Recommended for Production)
# ============================================================================

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Production-ready configuration using Pydantic Settings.
    
    Benefits:
    - Automatic validation
    - Type safety
    - Environment variable parsing
    - Documentation via Field descriptions
    - .env file support
    - IDE autocomplete
    
    Example .env file:
        OPENAI_API_KEY=sk-...
        MODEL_NAME=gpt-4o
        ENVIRONMENT=production
        TEMPERATURE=0.0
    """
    
    # ========================================
    # Environment
    # ========================================
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Runtime environment"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # ========================================
    # API Keys & Credentials
    # ========================================
    openai_api_key: str = Field(
        ...,  # Required field
        description="OpenAI API key",
        min_length=20  # Basic validation
    )
    
    langsmith_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key (optional)"
    )
    
    # ========================================
    # Model Configuration
    # ========================================
    model_name: str = Field(
        default="gpt-4o",
        description="OpenAI model name"
    )
    
    temperature: float = Field(
        default=0.0,
        ge=0.0,  # Greater than or equal to 0
        le=2.0,  # Less than or equal to 2
        description="Model temperature"
    )
    
    max_tokens: int = Field(
        default=10000,
        gt=0,
        le=128000,
        description="Maximum tokens per request"
    )
    
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    
    # ========================================
    # Paths
    # ========================================
    prompts_dir: Path = Field(
        default=Path("src/prompts"),
        description="Directory containing prompt templates"
    )
    
    data_dir: Path = Field(
        default=Path("data"),
        description="Directory for input/output data"
    )
    
    # ========================================
    # Feature Flags
    # ========================================
    enable_prompt_cache: bool = Field(
        default=True,
        description="Cache loaded prompts"
    )
    
    enable_fact_checking: bool = Field(
        default=True,
        description="Enable fact-checking loop"
    )
    
    max_fact_check_revisions: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum fact-check revision iterations"
    )
    
    # ========================================
    # Logging
    # ========================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # ========================================
    # Pydantic Settings Configuration
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_file_encoding="utf-8",
        case_sensitive=False,  # OPENAI_API_KEY == openai_api_key
        extra="ignore",  # Ignore extra fields in .env
    )
    
    # ========================================
    # Validators
    # ========================================
    @field_validator("prompts_dir", "data_dir")
    @classmethod
    def validate_directory_exists(cls, v: Path) -> Path:
        """Validate that directory exists or can be created."""
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v
    
    @model_validator(mode="after")
    def validate_environment_consistency(self):
        """Validate that configuration is consistent for environment."""
        if self.environment == "production":
            if self.debug:
                raise ValueError("Debug mode cannot be enabled in production")
            if self.temperature > 0.5:
                raise ValueError("High temperature not recommended for production")
        
        return self
    
    # ========================================
    # Computed Properties
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
    # Helper Methods
    # ========================================
    def get_model_kwargs(self) -> dict:
        """Get kwargs for LLM initialization."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


# ============================================================================
# ✅ APPROACH 3: Environment-Specific Configs (Advanced)
# ============================================================================

class EnvironmentConfig(AppSettings):
    """Base config with environment-specific overrides."""
    
    @classmethod
    def for_development(cls) -> "EnvironmentConfig":
        """Create development config."""
        return cls(
            environment="development",
            debug=True,
            model_name="gpt-4o-mini",  # Cheaper for dev
            enable_prompt_cache=True,
            log_level="DEBUG",
        )
    
    @classmethod
    def for_staging(cls) -> "EnvironmentConfig":
        """Create staging config."""
        return cls(
            environment="staging",
            debug=False,
            model_name="gpt-4o",
            enable_prompt_cache=True,
            log_level="INFO",
        )
    
    @classmethod
    def for_production(cls) -> "EnvironmentConfig":
        """Create production config."""
        return cls(
            environment="production",
            debug=False,
            model_name="gpt-4o",
            enable_prompt_cache=True,
            log_level="WARNING",
            max_retries=5,  # More retries in prod
        )
    
    @classmethod
    def from_env(cls) -> "EnvironmentConfig":
        """Auto-detect environment and load appropriate config."""
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            return cls.for_production()
        elif env == "staging":
            return cls.for_staging()
        else:
            return cls.for_development()


# ============================================================================
# ✅ APPROACH 4: Secrets Management (Production)
# ============================================================================

class SecureConfig(AppSettings):
    """Config with secure secrets management.
    
    Supports multiple secret backends:
    - Environment variables (dev)
    - AWS Secrets Manager (prod)
    - Azure Key Vault (prod)
    - HashiCorp Vault (prod)
    """
    
    secrets_backend: Literal["env", "aws", "azure", "vault"] = Field(
        default="env",
        description="Secrets management backend"
    )
    
    def __init__(self, **kwargs):
        # Load secrets from backend before Pydantic validation
        if kwargs.get("secrets_backend") == "aws":
            kwargs.update(self._load_from_aws())
        elif kwargs.get("secrets_backend") == "azure":
            kwargs.update(self._load_from_azure())
        
        super().__init__(**kwargs)
    
    def _load_from_aws(self) -> dict:
        """Load secrets from AWS Secrets Manager."""
        try:
            import boto3
            import json
            
            client = boto3.client("secretsmanager")
            response = client.get_secret_value(
                SecretId=os.getenv("AWS_SECRET_NAME", "app/api-keys")
            )
            
            return json.loads(response["SecretString"])
        except ImportError:
            raise ImportError("boto3 not installed. Run: pip install boto3")
        except Exception as e:
            raise ValueError(f"Failed to load secrets from AWS: {e}")
    
    def _load_from_azure(self) -> dict:
        """Load secrets from Azure Key Vault."""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = os.getenv("AZURE_VAULT_URL")
            if not vault_url:
                raise ValueError("AZURE_VAULT_URL not set")
            
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            return {
                "openai_api_key": client.get_secret("openai-api-key").value,
                "langsmith_api_key": client.get_secret("langsmith-api-key").value,
            }
        except ImportError:
            raise ImportError("azure-keyvault-secrets not installed")
        except Exception as e:
            raise ValueError(f"Failed to load secrets from Azure: {e}")


# ============================================================================
# 📝 USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Example 1: Basic usage."""
    config = AppSettings()
    
    print(f"Environment: {config.environment}")
    print(f"Model: {config.model_name}")
    print(f"Temperature: {config.temperature}")


def example_override_in_code():
    """Example 2: Override in code (useful for testing)."""
    config = AppSettings(
        openai_api_key="test-key",
        model_name="gpt-4o-mini",
        debug=True
    )
    
    print(f"Debug mode: {config.debug}")


def example_environment_specific():
    """Example 3: Environment-specific configuration."""
    # Auto-detect from ENVIRONMENT variable
    config = EnvironmentConfig.from_env()
    
    if config.is_production:
        print("Running in production mode")
        # Use production settings
    else:
        print("Running in development mode")
        # Use development settings


def example_with_langchain():
    """Example 4: Using with LangChain."""
    from langchain_openai import ChatOpenAI
    
    config = AppSettings()
    
    # Create LLM from config
    llm = ChatOpenAI(**config.get_model_kwargs())
    
    # Use in application
    response = llm.invoke("Hello!")


def example_validation_error():
    """Example 5: Configuration validation."""
    try:
        config = AppSettings(
            openai_api_key="sk-test",
            temperature=3.0,  # Invalid: > 2.0
        )
    except Exception as e:
        print(f"Validation failed: {e}")


def example_testing():
    """Example 6: Configuration for testing."""
    from unittest.mock import Mock
    
    # Create test config with mocked values
    test_config = AppSettings(
        openai_api_key="test-key-12345678901234567890",
        model_name="gpt-4o-mini",
        enable_prompt_cache=False,  # Disable cache in tests
        debug=True,
    )
    
    # Use in tests
    assert test_config.debug is True


# ============================================================================
# 🔒 SECURITY BEST PRACTICES
# ============================================================================

"""
1. NEVER commit secrets to git:
   - Add .env to .gitignore
   - Use .env.example as template
   - Store secrets in secret manager (production)

2. Validate all inputs:
   - Use Pydantic validators
   - Check ranges, formats, types
   - Fail fast on invalid config

3. Use different secrets per environment:
   - Dev: Test API keys
   - Staging: Separate keys
   - Production: Rotated secrets

4. Audit configuration:
   - Log config loading (without secrets)
   - Monitor for changes
   - Alert on suspicious values

5. Principle of least privilege:
   - Only load secrets that are needed
   - Scope secrets to environments
   - Rotate regularly
"""


# ============================================================================
# 📋 .env FILE TEMPLATE
# ============================================================================

ENV_FILE_TEMPLATE = """
# .env.example - Copy to .env and fill in your values
# DO NOT commit .env to git!

# ========================================
# Environment
# ========================================
ENVIRONMENT=development  # development, staging, production
DEBUG=true

# ========================================
# API Keys (REQUIRED)
# ========================================
OPENAI_API_KEY=sk-...  # Get from https://platform.openai.com

# Optional
LANGSMITH_API_KEY=  # Get from https://smith.langchain.com

# ========================================
# Model Configuration
# ========================================
MODEL_NAME=gpt-4o
TEMPERATURE=0.0
MAX_TOKENS=10000
MAX_RETRIES=3

# ========================================
# Paths
# ========================================
PROMPTS_DIR=src/prompts
DATA_DIR=data

# ========================================
# Feature Flags
# ========================================
ENABLE_PROMPT_CACHE=true
ENABLE_FACT_CHECKING=true
MAX_FACT_CHECK_REVISIONS=3

# ========================================
# Logging
# ========================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
"""


if __name__ == "__main__":
    print("Configuration Best Practices Examples")
    print("=" * 50)
    
    # Example usage
    print("\n1. Basic usage:")
    example_basic_usage()
    
    print("\n2. Environment-specific:")
    example_environment_specific()
    
    print("\n3. Validation:")
    example_validation_error()
