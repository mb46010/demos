# PromptLoader - Professional Prompt Management for LangGraph

A robust, production-ready prompt management system for your LangGraph performance review project.

## 🎯 Why PromptLoader?

Your current code has hardcoded dependencies that make testing difficult:

```python
# ❌ Current approach - hard to test
from demo.graph.model import llm
from demo.utils.loader import load_prompt

def create_draft(state):
    prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    # Uses hardcoded llm - can't mock easily
    response = llm.invoke(prompt_template)
```

With PromptLoader:

```python
# ✅ New approach - fully testable
def create_draft_node(llm, prompt_loader: PromptLoader):
    def create_draft(state):
        # Handles list vs string automatically
        prompt = prompt_loader.get_formatted(
            "n_draft",
            manager_input=state["input"],
            structure=state["structure"]
        )
        response = llm.invoke(prompt)
    return create_draft
```

## 📦 What's Included

1. **prompt_loader.py** - Main PromptLoader class
2. **prompt_loader_examples.py** - Usage examples
3. **test_prompt_loader.py** - Complete test suite
4. **n_draft_refactored.py** - Refactored node example
5. **MIGRATION_GUIDE.py** - Step-by-step migration instructions

## 🚀 Quick Start

### 1. Basic Usage

```python
from pathlib import Path
from demo.prompt_loader import PromptLoader

# Initialize
loader = PromptLoader(prompts_dir=Path("src/prompts"))

# Load a prompt
prompt = loader.load("n_draft")

# Load with formatting
formatted = loader.get_formatted(
    "n_draft",
    manager_input='{"rating": "exceeds"}',
    review_template_structure='{"sections": []}'
)
```

### 2. Dependency Injection

```python
from demo.config import AppConfig
from demo.graph.nodes.n_draft import create_draft_node

# Create config with dependencies
config = AppConfig(
    prompts_dir=Path("src/prompts"),
    model_name="gpt-4o"
)

# Create node with injected dependencies
draft_node = create_draft_node(
    llm=config.llm,
    prompt_loader=config.prompt_loader
)

# Use in graph
graph.add_node("create_draft", draft_node)
```

### 3. Testing

```python
from demo.prompt_loader import MockPromptLoader
from unittest.mock import Mock

def test_draft_creation():
    # Mock LLM
    mock_llm = Mock()
    mock_llm.invoke.return_value = "Generated draft"
    
    # Mock prompts
    mock_loader = MockPromptLoader(prompts={
        "n_draft": "Create draft: {input}"
    })
    
    # Test node
    node = create_draft_node(mock_llm, mock_loader)
    result = node({"input": "test"})
    
    assert result["draft"] == "Generated draft"
```

## ✨ Features

### Caching
```python
loader = PromptLoader(enable_cache=True)
prompt1 = loader.load("n_draft")  # Loads from file
prompt2 = loader.load("n_draft")  # Loads from cache
```

### Validation
```python
loader = PromptLoader(validate_on_load=True)
results = loader.validate_all()

# Check for errors
errors = {name: err for name, err in results.items() if err}
if errors:
    print(f"Found {len(errors)} invalid prompts")
```

### Error Messages
```python
# FileNotFoundError with helpful context
>>> loader.load("missing_prompt")
FileNotFoundError: Prompt file not found: src/prompts/missing_prompt.json
Available prompts: n_draft, n_input, n_rewriter, n_fact_extractor
```

### List vs String Handling
```python
# Automatically handles both formats
loader.get_formatted("prompt_as_list")   # Joins with \n
loader.get_formatted("prompt_as_string") # Returns as-is
```

## 📁 Installation

### Step 1: Copy Files

```bash
# Copy PromptLoader to your project
cp prompt_loader.py src/demo/utils/

# Update __init__.py
echo "from .prompt_loader import PromptLoader, MockPromptLoader" >> src/demo/utils/__init__.py
```

### Step 2: Create Config

```bash
# Create config module
cp config.py src/demo/
```

### Step 3: Run Tests

```bash
# Install pytest if needed
pip install pytest

# Run tests
pytest test_prompt_loader.py -v
```

## 🔄 Migration Path

Follow the **MIGRATION_GUIDE.py** for step-by-step instructions.

**Summary:**
1. Day 1: Setup PromptLoader and AppConfig
2. Day 2: Refactor simple nodes (n_draft, n_input)
3. Day 3: Refactor complex nodes (n_fact_extractor, n_rewriter)
4. Day 4: Update graph builders and entry points
5. Day 5: Cleanup and documentation

## 🧪 Testing Strategy

### Unit Tests
```python
# Test individual nodes with mocked dependencies
def test_draft_node():
    mock_llm = Mock()
    mock_loader = MockPromptLoader(...)
    
    node = create_draft_node(mock_llm, mock_loader)
    result = node(test_state)
    
    assert result["draft"]
```

### Integration Tests
```python
# Test with real prompts but mocked LLM
def test_graph_flow():
    config = AppConfig()
    config.llm = Mock()  # Mock only LLM
    
    agent = create_full_agent(config)
    result = agent.invoke(test_state)
    
    assert result["draft"]
```

### End-to-End Tests
```python
# Test with real everything
def test_e2e():
    config = AppConfig()  # Real LLM, real prompts
    
    agent = create_full_agent(config)
    result = agent.invoke(real_state)
    
    assert result["draft"]
```

## 📊 Comparison: Before vs After

| Feature | Before | After |
|---------|--------|-------|
| **Testability** | ❌ Hard (hardcoded LLM) | ✅ Easy (injected deps) |
| **Prompt Caching** | ❌ No | ✅ Yes |
| **Error Messages** | ⚠️ Generic | ✅ Detailed |
| **List Handling** | ⚠️ Manual | ✅ Automatic |
| **Validation** | ❌ No | ✅ Yes |
| **Reusability** | ❌ Low | ✅ High |
| **Configuration** | ⚠️ Scattered | ✅ Centralized |

## 🎓 Learning Resources

This implementation follows best practices from:
- **LangChain Academy** - Dependency injection patterns
- **LangGraph 101** - Factory pattern for nodes
- **Production case studies** - Configuration management

See the **MIGRATION_GUIDE.py** for links to official resources.

## 🐛 Common Issues

### Issue 1: Import errors after migration
```python
# Make sure to update imports
# OLD: from demo.utils.loader import load_prompt
# NEW: from demo.utils.prompt_loader import PromptLoader
```

### Issue 2: Tests fail with "No such file"
```python
# Use MockPromptLoader in tests, not real PromptLoader
mock_loader = MockPromptLoader(prompts={"test": "..."})
```

### Issue 3: Prompts not found
```python
# Check prompts directory
loader = PromptLoader(prompts_dir=Path("src/prompts"))
print(loader.list_available())  # Shows all available prompts
```

## 📝 Files Overview

```
.
├── prompt_loader.py              # Main class (200 lines)
├── prompt_loader_examples.py     # 8 usage examples
├── test_prompt_loader.py         # Comprehensive tests
├── n_draft_refactored.py         # Refactored node example
├── MIGRATION_GUIDE.py            # Step-by-step migration
└── README.md                     # This file
```

## 🚦 Next Steps

1. **Read** MIGRATION_GUIDE.py
2. **Copy** prompt_loader.py to your project
3. **Run** test_prompt_loader.py to verify
4. **Refactor** one node as a test
5. **Expand** to all nodes
6. **Test** thoroughly
7. **Deploy** with confidence

## 💡 Pro Tips

1. **Start small** - Refactor one node first
2. **Keep old code** - Don't delete until migration is stable
3. **Test incrementally** - Test after each refactor
4. **Use feature flags** - Allow rollback if needed
5. **Cache on startup** - Warm cache in production

## 🤝 Contributing

Found a bug? Have a suggestion?
- File an issue
- Submit a PR
- Ask in LangChain Discord

## 📄 License

Same as your project (add your license here)

---

**Ready to make your prompts professional? Start with the MIGRATION_GUIDE.py!**
