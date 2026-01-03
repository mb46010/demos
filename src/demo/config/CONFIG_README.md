# Configuration Best Practices - Complete Package

**Production-ready configuration management for your LangGraph project**

## 📦 What's Included

This package contains **everything** you need for professional configuration management:

### Core Files
1. **config.py** - Production-ready Pydantic Settings configuration
2. **env.example.txt** - Template .env file (rename to .env)
3. **config_best_practices.py** - Learning resource with 4 approaches
4. **CONFIG_GUIDE.md** - Comprehensive documentation

### Supporting Files  
5. **REFACTORING_EXAMPLE.py** - Before/after comparison with migration plan
6. **prompt_loader.py** - PromptLoader class (from previous package)
7. **test_prompt_loader.py** - Tests for PromptLoader

## 🎯 Quick Start (5 Minutes)

### 1. Copy Core Files
```bash
# Copy config module
cp config.py src/demo/config.py

# Create .env file
cp env.example.txt .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Install Dependencies
```bash
pip install pydantic-settings>=2.0.0
```

### 3. Test It
```python
from demo.config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"Model: {config.model_name}")

# Create LLM
llm = config.create_llm()
```

## 📚 Learning Path

**Total time: ~2 hours to master**

### Beginner (30 minutes)
1. Read the **Quick Start** above
2. Review **config_best_practices.py** - See 4 approaches from simple to advanced
3. Look at **env.example.txt** - Understand what settings are available

### Intermediate (1 hour)  
1. Read **CONFIG_GUIDE.md** - Deep dive into:
   - Why Pydantic Settings?
   - Environment management
   - Secrets management
   - Testing strategies

2. Study **config.py** - See production-ready implementation with:
   - Field validation
   - Environment-specific logic
   - Factory methods
   - Safe logging

### Advanced (30 minutes)
1. Review **REFACTORING_EXAMPLE.py** - See exactly how to migrate your code
2. Plan your refactoring using the 7-phase guide
3. Implement with the rollback plan for safety

## 🚀 Integration with Your Project

### Current Structure
```
your-project/
├── src/
│   └── demo/
│       ├── graph/
│       │   ├── model.py          # ❌ Hardcoded LLM
│       │   └── nodes/
│       │       └── n_draft.py    # ❌ Imports hardcoded LLM
│       └── utils/
│           └── loader.py         # ⚠️ Manual prompt loading
```

### After Integration
```
your-project/
├── .env                          # ✅ Your secrets (gitignored)
├── .env.example                  # ✅ Template (committed)
│
├── src/
│   └── demo/
│       ├── config.py             # ✅ NEW: Configuration
│       ├── graph/
│       │   ├── nodes/
│       │   │   └── n_draft.py    # ✅ REFACTORED: Factory pattern
│       │   └── graph.py          # ✅ REFACTORED: Accepts config
│       └── utils/
│           └── prompt_loader.py  # ✅ NEW: Better prompt loading
```

## 🎓 Configuration Approaches Explained

### Approach 1: Simple (Good for POCs)
```python
class SimpleConfig:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o")
```
✅ Easy to understand  
❌ No validation  
❌ Manual type conversion  

### Approach 2: Pydantic Settings (Recommended)
```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    openai_api_key: str  # Validated
    model_name: str = "gpt-4o"  # Type-safe
    temperature: float = Field(ge=0.0, le=2.0)  # Range validation
```
✅ Automatic validation  
✅ Type safety  
✅ IDE autocomplete  
✅ .env file support  

### Approach 3: Environment-Specific (Production)
```python
class AppConfig(BaseSettings):
    @classmethod
    def for_production(cls):
        return cls(
            environment="production",
            debug=False,
            max_retries=5,
        )
```
✅ Environment-aware defaults  
✅ Production safeguards  

### Approach 4: Secrets Management (Enterprise)
```python
class SecureConfig(AppSettings):
    def _load_from_aws(self):
        # Load from AWS Secrets Manager
        pass
```
✅ Secure secret storage  
✅ Automatic rotation  

## 🔐 Security Best Practices

### ✅ DO
- Store secrets in .env (local) or secret manager (production)
- Add .env to .gitignore
- Commit .env.example as template
- Use different keys per environment
- Validate all configuration
- Mask secrets in logs

### ❌ DON'T
- Commit .env to git
- Hardcode secrets in code
- Use production keys in development
- Share API keys via chat/email
- Log secrets
- Use same keys across environments

## 🧪 Testing

### Test Configuration
```python
from demo.config import create_test_config

def test_something():
    config = create_test_config(
        model_name="gpt-4o-mini",  # Cheaper
        enable_fact_checking=False,  # Faster
    )
    
    # Use config in test
```

### Mock LLM
```python
from unittest.mock import Mock

mock_llm = Mock()
mock_llm.invoke.return_value = "Test response"

# Use mock in tests
```

## 📊 Comparison Table

| Feature | Before | After |
|---------|--------|-------|
| **Configuration** | Hardcoded in code | Environment variables |
| **Validation** | None | Pydantic validators |
| **Type Safety** | No | Yes (full typing) |
| **Testing** | Hard (hardcoded deps) | Easy (dependency injection) |
| **Secrets** | In code 😱 | In .env / secret manager |
| **Environments** | One size fits all | Dev/staging/prod |
| **Error Messages** | Generic | Specific & helpful |
| **IDE Support** | None | Autocomplete & hints |

## 🔄 Migration Timeline

**Realistic timeline for your project:**

| Phase | Time | Tasks |
|-------|------|-------|
| **Setup** | 1 hour | Create config.py, .env, install deps |
| **Refactor Nodes** | 3 hours | Update 4 node files |
| **Update Graph** | 1 hour | Refactor graph builders |
| **Update Tests** | 2 hours | Add config to tests |
| **Cleanup** | 1 hour | Remove old code |
| **Verification** | 1 hour | Test everything |
| **TOTAL** | ~9 hours | Spread over 2-3 days |

## 🎯 Files Overview

### Must Read (Start Here)
- **README.md** (this file) - Overview
- **CONFIG_GUIDE.md** - Comprehensive guide
- **config.py** - Production implementation

### Learning Resources
- **config_best_practices.py** - 4 approaches explained
- **REFACTORING_EXAMPLE.py** - Before/after code

### Implementation Files
- **env.example.txt** - Template (rename to .env)
- **prompt_loader.py** - Better prompt loading
- **test_prompt_loader.py** - Test suite

## 🆘 Troubleshooting

### Issue 1: "No module named 'pydantic_settings'"
```bash
pip install pydantic-settings
```

### Issue 2: "Required environment variable 'OPENAI_API_KEY' not set"
```bash
# Create .env file
cp env.example.txt .env

# Edit .env and add:
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue 3: "Validation error: temperature"
```python
# Temperature must be between 0.0 and 2.0
# Fix in .env:
TEMPERATURE=0.7  # Not 7.0
```

### Issue 4: Import errors after refactoring
```python
# Old import
from demo.graph.model import llm  # ❌ Doesn't exist anymore

# New pattern
from demo.config import get_config
config = get_config()
llm = config.create_llm()
```

## 💡 Pro Tips

1. **Start small** - Refactor one node first to test the pattern
2. **Use feature flags** - Allow rollback if needed
3. **Test incrementally** - Test after each refactor
4. **Keep old code** - In deprecated/ folder until stable
5. **Document changes** - Help your team understand

## 🌟 Benefits You'll Get

After implementing this configuration system:

✅ **No more hardcoded values** - Change settings via .env  
✅ **Secure secrets** - Never commit API keys again  
✅ **Easy testing** - Mock any dependency  
✅ **Type safety** - Catch errors before runtime  
✅ **Environment awareness** - Different settings for dev/prod  
✅ **Better errors** - Know exactly what's wrong  
✅ **Team friendly** - .env.example makes onboarding easy  
✅ **Production ready** - Used by companies like Klarna, Uber  

## 📖 What to Read Next

**Based on your experience level:**

### Beginner
1. Start with **env.example.txt** - See what settings exist
2. Read **config_best_practices.py** Approach 1 & 2
3. Implement simple config in your project

### Intermediate  
1. Read full **CONFIG_GUIDE.md**
2. Study **config.py** implementation
3. Plan your refactoring

### Advanced
1. Review **REFACTORING_EXAMPLE.py**
2. Implement secret manager integration
3. Set up CI/CD with environment-specific configs

## 🎓 Additional Resources

- [Pydantic Settings Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App](https://12factor.net/config)
- [LangChain Academy](https://academy.langchain.com/)

---

**Ready to make your configuration professional?**

Start with:
1. **CONFIG_GUIDE.md** - Understand the why
2. **config.py** - See the how  
3. **REFACTORING_EXAMPLE.py** - Plan your migration

Good luck! 🚀
