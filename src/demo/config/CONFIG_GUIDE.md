# Configuration Management Guide

Complete guide to professional configuration management for your LangGraph project.

## 📚 Table of Contents

1. [Why Pydantic Settings?](#why-pydantic-settings)
2. [Project Structure](#project-structure)
3. [Environment Management](#environment-management)
4. [Secrets Management](#secrets-management)
5. [Testing with Config](#testing-with-config)
6. [Deployment](#deployment)
7. [Best Practices](#best-practices)

## 🎯 Why Pydantic Settings?

### The Problem with Simple Approaches

```python
# ❌ PROBLEM: No validation
temperature = float(os.getenv("TEMPERATURE"))  # Crashes if not set

# ❌ PROBLEM: No type safety
model_name = os.getenv("MODEL_NAME", "gpt-4")  # IDE doesn't know the type

# ❌ PROBLEM: Secrets in code
API_KEY = "sk-12345"  # NEVER do this!
```

### The Solution: Pydantic Settings

```python
# ✅ SOLUTION: Validation, type safety, no secrets in code
from demo.config import get_config

config = get_config()  # Validated, typed, secure
llm = config.create_llm()
```

**Benefits:**
- ✅ Automatic validation (catches errors early)
- ✅ Type safety (IDE autocomplete)
- ✅ Environment variable parsing
- ✅ .env file support
- ✅ Documentation via Field descriptions
- ✅ Computed properties
- ✅ Easy testing

## 📁 Project Structure

```
your-project/
├── .env.example              # Template (commit to git)
├── .env                      # Your secrets (in .gitignore)
├── .env.development          # Dev environment
├── .env.staging              # Staging environment
├── .env.production           # Production environment (on server only)
│
├── src/
│   └── demo/
│       ├── config.py         # Main config module
│       └── utils/
│           └── prompt_loader.py
│
└── tests/
    └── test_config.py        # Config tests
```

### Key Files

**1. .env.example** - Template for others
```bash
# Commit this to git
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o
ENVIRONMENT=development
```

**2. .env** - Your actual secrets (NEVER commit)
```bash
# In .gitignore
OPENAI_API_KEY=sk-actual-secret-key
MODEL_NAME=gpt-4o
```

**3. config.py** - Configuration class
```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o"
    # ...
```

## 🌍 Environment Management

### Approach 1: Multiple .env Files

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

**Usage:**
```bash
# Load development config
ENV_FILE=.env.development python app.py

# Load production config
ENV_FILE=.env.production python app.py
```

**Implementation:**
```python
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
    )
```

### Approach 2: Environment Variable

```bash
# Set environment
export ENVIRONMENT=production

# Run application
python app.py
```

**Implementation:**
```python
class AppConfig(BaseSettings):
    environment: Literal["development", "staging", "production"] = "development"
    
    @model_validator(mode="after")
    def validate_environment(self):
        if self.environment == "production":
            # Apply production constraints
            if self.debug:
                raise ValueError("Debug mode not allowed in production")
        return self
```

### Approach 3: Factory Methods (Recommended)

```python
class AppConfig(BaseSettings):
    @classmethod
    def for_development(cls):
        return cls(
            environment="development",
            debug=True,
            model_name="gpt-4o-mini",  # Cheaper
        )
    
    @classmethod
    def for_production(cls):
        return cls(
            environment="production",
            debug=False,
            model_name="gpt-4o",
            max_retries=5,  # More resilient
        )
    
    @classmethod
    def from_env(cls):
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            return cls.for_production()
        return cls.for_development()
```

**Usage:**
```python
# Auto-detect from ENVIRONMENT variable
config = AppConfig.from_env()

# Or explicit
config = AppConfig.for_production()
```

## 🔒 Secrets Management

### Development: .env File

```bash
# .env (local development)
OPENAI_API_KEY=sk-dev-key
```

✅ Good for: Local development
❌ Bad for: Production, team sharing

### Staging/Production: Secret Managers

#### Option 1: AWS Secrets Manager

```python
import boto3
import json

def load_secrets_from_aws():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    
    response = client.get_secret_value(
        SecretId="prod/performance-review-ai"
    )
    
    return json.loads(response["SecretString"])

# In config.py
class AppConfig(BaseSettings):
    def __init__(self, **kwargs):
        if os.getenv("ENVIRONMENT") == "production":
            kwargs.update(load_secrets_from_aws())
        super().__init__(**kwargs)
```

#### Option 2: Azure Key Vault

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def load_secrets_from_azure():
    vault_url = "https://my-vault.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    return {
        "openai_api_key": client.get_secret("openai-api-key").value,
    }
```

#### Option 3: Docker Secrets

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: performance-review-ai
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

```python
# config.py
def read_secret_file(path: str) -> str:
    with open(path) as f:
        return f.read().strip()

class AppConfig(BaseSettings):
    openai_api_key: str = Field(default="")
    
    def __init__(self, **kwargs):
        # Read from file if specified
        if key_file := os.getenv("OPENAI_API_KEY_FILE"):
            kwargs["openai_api_key"] = read_secret_file(key_file)
        
        super().__init__(**kwargs)
```

### Security Checklist

- [ ] .env in .gitignore
- [ ] .env.example committed (no secrets)
- [ ] Different keys per environment
- [ ] Keys rotated regularly
- [ ] Secrets masked in logs
- [ ] Use secret manager in production
- [ ] Principle of least privilege

## 🧪 Testing with Config

### Approach 1: Override in Test

```python
# tests/test_nodes.py
import pytest
from demo.config import AppConfig
from demo.graph.nodes.n_draft import create_draft_node

def test_draft_creation():
    # Create test config
    config = AppConfig(
        openai_api_key="test-key-12345678901234567890",
        model_name="gpt-4o-mini",
        enable_fact_checking=False,  # Faster tests
        debug=True,
    )
    
    # Create node with test config
    draft_node = create_draft_node(
        llm=config.create_llm(),
        prompt_loader=config.create_prompt_loader()
    )
    
    # Test it
    result = draft_node(test_state)
    assert result["draft"]
```

### Approach 2: Fixture

```python
# tests/conftest.py
import pytest
from demo.config import AppConfig

@pytest.fixture
def test_config():
    """Reusable test configuration."""
    return AppConfig(
        openai_api_key="test-key-12345678901234567890",
        model_name="gpt-4o-mini",
        enable_prompt_cache=False,
        debug=True,
    )

# tests/test_nodes.py
def test_draft_creation(test_config):
    llm = test_config.create_llm()
    loader = test_config.create_prompt_loader()
    # ...
```

### Approach 3: Mock Environment

```python
import os
from unittest.mock import patch

@patch.dict(os.environ, {
    "OPENAI_API_KEY": "test-key-12345678901234567890",
    "MODEL_NAME": "gpt-4o-mini",
    "DEBUG": "true",
})
def test_config_from_env():
    from demo.config import get_config
    
    config = get_config(force_reload=True)
    assert config.model_name == "gpt-4o-mini"
```

### Test Config Utility

```python
# demo/config.py
def create_test_config(**overrides) -> AppConfig:
    """Create configuration for testing."""
    defaults = {
        "openai_api_key": "test-key-12345678901234567890",
        "environment": "development",
        "debug": True,
        "enable_prompt_cache": False,
    }
    defaults.update(overrides)
    return AppConfig(**defaults)

# In tests
config = create_test_config(model_name="gpt-4o-mini")
```

## 🚀 Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ src/
COPY .env.production .env

# Don't commit .env.production to git!
# Instead, inject at runtime:
# docker run -e OPENAI_API_KEY=sk-... my-app

CMD ["python", "src/demo/graph/app.py"]
```

```bash
# Build
docker build -t performance-review-ai .

# Run with environment variables
docker run \
  -e OPENAI_API_KEY=sk-... \
  -e ENVIRONMENT=production \
  performance-review-ai
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
type: Opaque
stringData:
  openai-api-key: sk-...
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: performance-review-ai
spec:
  template:
    spec:
      containers:
      - name: app
        image: performance-review-ai:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        - name: ENVIRONMENT
          value: production
```

### AWS Lambda

```python
# lambda_handler.py
import os
from demo.config import AppConfig

def lambda_handler(event, context):
    # Config from environment variables
    config = AppConfig()
    
    # Process request
    # ...
```

```bash
# Set environment variables in Lambda console
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
MODEL_NAME=gpt-4o
```

## 📋 Best Practices

### 1. Validation

```python
class AppConfig(BaseSettings):
    temperature: float = Field(ge=0.0, le=2.0)  # Range validation
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v
```

### 2. Environment-Specific Defaults

```python
class AppConfig(BaseSettings):
    @model_validator(mode="after")
    def set_environment_defaults(self):
        if self.environment == "production":
            # Production defaults
            self.max_retries = max(self.max_retries, 5)
            self.log_level = "WARNING"
        elif self.environment == "development":
            # Development defaults
            self.debug = True
            self.log_level = "DEBUG"
        
        return self
```

### 3. Computed Properties

```python
class AppConfig(BaseSettings):
    @property
    def llm_kwargs(self) -> dict:
        """Get kwargs for LLM initialization."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
```

### 4. Safe Logging

```python
class AppConfig(BaseSettings):
    def model_dump_safe(self) -> dict:
        """Dump config without secrets."""
        config = self.model_dump()
        config["openai_api_key"] = "***MASKED***"
        return config

# Usage
logger.info(f"Config: {config.model_dump_safe()}")
```

### 5. Singleton Pattern

```python
_config: Optional[AppConfig] = None

def get_config(force_reload: bool = False) -> AppConfig:
    """Get singleton config instance."""
    global _config
    
    if _config is None or force_reload:
        _config = AppConfig()
        _config.setup_logging()
    
    return _config
```

## 🎯 Quick Reference

### Loading Config

```python
from demo.config import get_config

# Get singleton
config = get_config()

# Force reload
config = get_config(force_reload=True)

# Create new instance
config = AppConfig()
```

### Using Config

```python
# Create LLM
llm = config.create_llm()

# Create prompt loader
loader = config.create_prompt_loader()

# Check environment
if config.is_production:
    # Production logic
    pass
```

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional (have defaults)
export MODEL_NAME=gpt-4o
export TEMPERATURE=0.0
export ENVIRONMENT=production
```

## ⚠️ Common Mistakes

### ❌ Mistake 1: Secrets in Code
```python
# NEVER do this!
OPENAI_API_KEY = "sk-12345"
```

### ❌ Mistake 2: No Validation
```python
# This can crash at runtime!
temperature = float(os.getenv("TEMPERATURE"))
```

### ❌ Mistake 3: Committing .env
```bash
# Add to .gitignore!
.env
.env.production
*.env
!.env.example
```

### ❌ Mistake 4: Hardcoded Paths
```python
# Bad: Won't work on other machines
prompts_dir = "/Users/alice/projects/app/prompts"

# Good: Relative or configurable
prompts_dir = Path("src/prompts")
```

## 📚 Additional Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App Config](https://12factor.net/config)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/products/key-vault)

---

**Ready to implement?** Start with `config.py` and `.env.example`!
