"""Migration guide: Moving from hardcoded prompt loading to PromptLoader.

This guide shows step-by-step how to refactor your project to use PromptLoader
for better testability and maintainability.
"""

# ============================================================================
# STEP 1: Add PromptLoader to your project
# ============================================================================

"""
1. Copy prompt_loader.py to src/demo/utils/prompt_loader.py
2. Update src/demo/utils/__init__.py:
   
   from .prompt_loader import PromptLoader, MockPromptLoader
   
   __all__ = ["PromptLoader", "MockPromptLoader", ...]
"""


# ============================================================================
# STEP 2: Create a configuration module
# ============================================================================

"""
Create src/demo/config.py:
"""

from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from demo.utils.prompt_loader import PromptLoader


class AppConfig:
    """Centralized application configuration."""
    
    def __init__(
        self,
        prompts_dir: Path = Path("src/prompts"),
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 10000,
        enable_prompt_cache: bool = True,
    ):
        self.prompts_dir = prompts_dir
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize shared dependencies
        self.prompt_loader = PromptLoader(
            prompts_dir=prompts_dir,
            enable_cache=enable_prompt_cache
        )
        
        self.llm = self._create_llm()
    
    def _create_llm(self):
        """Create LLM instance with retry logic."""
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        ).with_retry(
            retry_if_exception_type=(Exception,),
            wait_exponential_jitter=True,
            stop_after_attempt=3,
        )
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        import os
        
        return cls(
            model_name=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=float(os.getenv("TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("MAX_TOKENS", "10000")),
        )


# ============================================================================
# STEP 3: Refactor nodes to use factories
# ============================================================================

"""
Update each node file to use the factory pattern.

Before (src/demo/graph/nodes/n_draft.py):
"""

# OLD - DON'T DO THIS
from demo.graph.model import llm  # Hardcoded dependency
from demo.utils.loader import load_prompt  # Hardcoded loading

def create_draft(state: GraphState):
    prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    # ...


"""
After (src/demo/graph/nodes/n_draft.py):
"""

# NEW - DO THIS
def create_draft_node(llm, prompt_loader: PromptLoader):
    """Factory that creates a draft node."""
    
    def create_draft(state: GraphState):
        prompt_template = prompt_loader.get_formatted(
            "n_draft",
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
        )
        
        response = llm.with_structured_output(DraftResult).invoke(
            [HumanMessage(content=prompt_template)]
        )
        
        return {KEY_DRAFT: response.model_dump()["draft"]}
    
    return create_draft


# ============================================================================
# STEP 4: Update graph builders
# ============================================================================

"""
Before (src/demo/graph/graph.py):
"""

# OLD
from demo.graph.nodes.n_draft import create_draft  # Direct import
from demo.graph.nodes.n_input import input_check

def create_full_agent():
    agent_builder = StateGraph(GraphState)
    
    agent_builder.add_node(NODE_INPUT_CHECK, input_check)  # Hardcoded
    agent_builder.add_node(NODE_CREATE_DRAFT, create_draft)  # Hardcoded
    
    return agent_builder


"""
After (src/demo/graph/graph.py):
"""

# NEW
from demo.config import AppConfig
from demo.graph.nodes.n_draft import create_draft_node  # Import factory
from demo.graph.nodes.n_input import create_input_check_node  # Import factory

def create_full_agent(config: Optional[AppConfig] = None):
    """Create agent with dependency injection."""
    config = config or AppConfig()
    
    agent_builder = StateGraph(GraphState)
    
    # Create nodes with injected dependencies
    input_check = create_input_check_node(
        llm=config.llm,
        prompt_loader=config.prompt_loader
    )
    draft_node = create_draft_node(
        llm=config.llm,
        prompt_loader=config.prompt_loader
    )
    
    agent_builder.add_node(NODE_INPUT_CHECK, input_check)
    agent_builder.add_node(NODE_CREATE_DRAFT, draft_node)
    
    return agent_builder


# ============================================================================
# STEP 5: Update entry points (app.py)
# ============================================================================

"""
Before (src/demo/graph/app.py):
"""

# OLD
if __name__ == "__main__":
    data = load_data(input_path=args.input_file)
    
    config = {
        KEY_INPUT: data["input"],
        # ...
    }
    
    agent_builder = create_full_agent()  # No config
    agent = agent_builder.compile()
    response = agent.invoke(config)


"""
After (src/demo/graph/app.py):
"""

# NEW
from demo.config import AppConfig

if __name__ == "__main__":
    # Initialize configuration
    app_config = AppConfig(
        prompts_dir=Path("src/prompts"),
        model_name="gpt-4o",
        temperature=0,
    )
    
    # Load data
    data = load_data(input_path=args.input_file)
    
    # Create state
    state_config = {
        KEY_INPUT: data["input"],
        # ...
    }
    
    # Create agent with injected config
    agent_builder = create_full_agent(config=app_config)
    agent = agent_builder.compile()
    
    # Run
    response = agent.invoke(state_config)


# ============================================================================
# STEP 6: Update tests
# ============================================================================

"""
Before (tests/test_nodes.py):
"""

# OLD - Hard to test
def test_create_draft():
    state = {"input": {...}, "structure": {...}}
    result = create_draft(state)  # Uses hardcoded LLM
    assert result["draft"]  # Hard to control


"""
After (tests/test_nodes.py):
"""

# NEW - Easy to test
from unittest.mock import Mock
from demo.utils.prompt_loader import MockPromptLoader
from demo.graph.nodes.n_draft import create_draft_node

def test_create_draft():
    # Mock LLM
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.model_dump.return_value = {"draft": "Test draft"}
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
    
    # Mock prompts
    mock_loader = MockPromptLoader(prompts={
        "n_draft": "Create draft from: {manager_input}"
    })
    
    # Create node with mocks
    draft_node = create_draft_node(mock_llm, mock_loader)
    
    # Test
    state = {
        "input": {"rating": "exceeds"},
        "structure": {"sections": []}
    }
    
    result = draft_node(state)
    
    # Verify
    assert result["draft"] == "Test draft"
    mock_llm.with_structured_output.assert_called_once()


# ============================================================================
# STEP 7: Refactor remaining nodes
# ============================================================================

"""
Refactor in this order (easiest to hardest):

1. ✅ n_draft.py (simple prompt loading)
2. ✅ n_input.py (simple prompt loading)
3. ✅ n_rewriter.py (simple prompt loading)
4. ⚠️  n_fact_extractor.py (complex, has example loading)
5. ⚠️  n_fact_rewriter.py (depends on fact_extractor)

For n_fact_extractor.py, you'll need to also pass example data:
"""

def create_fact_extractor_node(llm, prompt_loader: PromptLoader):
    """Factory for fact extractor with example data."""
    
    # Load example data once during factory creation
    example_path = Path("docs/templates/claim_fact_pairs.json")
    with open(example_path) as f:
        example_data = json.load(f)
    
    def fc_extractor(state: GraphState):
        filled_prompt = prompt_loader.get_formatted(
            "n_fact_extractor",
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            review=state.get(KEY_DRAFT, ""),
            example=json.dumps(example_data, indent=2),
        )
        # ...
    
    return fc_extractor


# ============================================================================
# STEP 8: Clean up old code
# ============================================================================

"""
After migration is complete:

1. Remove src/demo/graph/model.py (hardcoded LLM)
2. Remove load_prompt, load_prompts from src/demo/utils/loader.py
3. Search for any remaining direct imports of `llm`
4. Run tests to verify everything works
"""


# ============================================================================
# MIGRATION CHECKLIST
# ============================================================================

"""
Day 1: Setup
- [ ] Add PromptLoader to project
- [ ] Create AppConfig class
- [ ] Write tests for PromptLoader

Day 2: Refactor simple nodes
- [ ] Refactor n_draft.py to use factory pattern
- [ ] Update tests for n_draft
- [ ] Refactor n_input.py
- [ ] Update tests for n_input

Day 3: Refactor complex nodes
- [ ] Refactor n_fact_extractor.py
- [ ] Refactor n_rewriter.py
- [ ] Update all tests

Day 4: Update graph builders
- [ ] Update graph.py to use factories
- [ ] Update app.py to use AppConfig
- [ ] Test end-to-end flow

Day 5: Cleanup
- [ ] Remove old loader code
- [ ] Remove hardcoded model.py
- [ ] Run full test suite
- [ ] Update documentation
"""


# ============================================================================
# ROLLBACK PLAN
# ============================================================================

"""
If you need to rollback:

1. Keep old code in nodes/deprecated/ folder during migration
2. Use feature flags to switch between old/new:

```python
USE_NEW_PATTERN = os.getenv("USE_NEW_PATTERN", "false").lower() == "true"

if USE_NEW_PATTERN:
    draft_node = create_draft_node(llm, loader)
else:
    from demo.graph.nodes.deprecated.n_draft import create_draft
    draft_node = create_draft
```

3. After 1-2 weeks of stable operation, delete deprecated folder
"""


# ============================================================================
# BENEFITS AFTER MIGRATION
# ============================================================================

"""
After migration you'll have:

✅ Testable nodes (mock LLM and prompts easily)
✅ Configurable LLMs (swap models without code changes)
✅ Cached prompts (faster loading)
✅ Validated prompts (catch errors early)
✅ Environment-specific prompts (dev vs prod)
✅ Better error messages
✅ Easier debugging
✅ Production-ready architecture
"""


if __name__ == "__main__":
    print("Migration guide ready!")
    print("\nNext steps:")
    print("1. Review the guide above")
    print("2. Start with Day 1 tasks")
    print("3. Test thoroughly at each step")
    print("4. Keep old code until migration is stable")
