"""Examples of using PromptLoader in the performance review system."""

from pathlib import Path
from demo.prompt_loader import PromptLoader, MockPromptLoader
from demo.graph.state import GraphState


# ============================================================================
# Example 1: Basic Usage
# ============================================================================

def example_basic_usage():
    """Basic prompt loading."""
    # Initialize loader
    loader = PromptLoader(prompts_dir=Path("src/prompts"))
    
    # Load a single prompt
    draft_prompt = loader.load("n_draft")
    print(f"Draft prompt type: {type(draft_prompt)}")
    
    # Load with formatting
    formatted = loader.get_formatted(
        "n_draft",
        manager_input='{"rating": "exceeds"}',
        review_template_structure='{"sections": []}'
    )
    print(f"Formatted length: {len(formatted)}")
    
    # List all available prompts
    available = loader.list_available()
    print(f"Available prompts: {available}")


# ============================================================================
# Example 2: Refactored Node (OLD vs NEW)
# ============================================================================

# OLD APPROACH (current code)
def create_draft_old(state: GraphState):
    """OLD: Hardcoded prompt loading."""
    from demo.utils.loader import load_prompt
    
    prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw
    
    # ... rest of the code


# NEW APPROACH (with dependency injection)
def create_draft_node_factory(llm, prompt_loader: PromptLoader):
    """Factory that returns a configured node with injected dependencies."""
    
    def create_draft(state: GraphState):
        """Create draft with injected PromptLoader."""
        # Much cleaner - loader handles list vs string
        prompt_template = prompt_loader.get_formatted(
            "n_draft",
            manager_input=state["input"],
            review_template_structure=state["structure"]
        )
        
        # Use LLM
        response = llm.invoke(prompt_template)
        return {"draft": response}
    
    return create_draft


# ============================================================================
# Example 3: Configuration Class
# ============================================================================

class AppConfig:
    """Centralized configuration for dependency injection."""
    
    def __init__(
        self,
        prompts_dir: Path = Path("src/prompts"),
        llm=None,
        enable_prompt_cache: bool = True,
    ):
        self.prompts_dir = prompts_dir
        self.enable_prompt_cache = enable_prompt_cache
        
        # Initialize shared dependencies
        self.prompt_loader = PromptLoader(
            prompts_dir=prompts_dir,
            enable_cache=enable_prompt_cache
        )
        
        self.llm = llm or self._get_default_llm()
    
    def _get_default_llm(self):
        """Get default LLM configuration."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=0)


# ============================================================================
# Example 4: Updated Graph Builder
# ============================================================================

def create_full_agent_with_di(config: AppConfig = None):
    """Create agent with dependency injection.
    
    Args:
        config: Application configuration with dependencies
    """
    from langgraph.graph import StateGraph
    from demo.graph.state import GraphState
    
    config = config or AppConfig()
    
    agent_builder = StateGraph(GraphState)
    
    # Create nodes with injected dependencies
    draft_node = create_draft_node_factory(
        llm=config.llm,
        prompt_loader=config.prompt_loader
    )
    
    agent_builder.add_node("create_draft", draft_node)
    
    # ... add more nodes
    
    return agent_builder


# ============================================================================
# Example 5: Testing with MockPromptLoader
# ============================================================================

def test_draft_creation():
    """Test draft creation with mocked prompts."""
    from unittest.mock import Mock
    
    # Create mock LLM
    mock_llm = Mock()
    mock_llm.invoke.return_value = "Generated draft"
    
    # Create mock prompt loader
    mock_prompts = MockPromptLoader(prompts={
        "n_draft": "Create a draft from: {manager_input}"
    })
    
    # Create node with mocked dependencies
    draft_node = create_draft_node_factory(
        llm=mock_llm,
        prompt_loader=mock_prompts
    )
    
    # Test it
    state = {
        "input": {"rating": "exceeds"},
        "structure": {"sections": []}
    }
    
    result = draft_node(state)
    
    # Verify
    assert result["draft"] == "Generated draft"
    mock_llm.invoke.assert_called_once()


# ============================================================================
# Example 6: Environment-Specific Prompts
# ============================================================================

class EnvironmentPromptLoader(PromptLoader):
    """Prompt loader that supports environment-specific overrides.
    
    Example:
        src/prompts/n_draft.json          # Default
        src/prompts/dev/n_draft.json      # Dev override
        src/prompts/prod/n_draft.json     # Prod override
    """
    
    def __init__(
        self,
        prompts_dir: Path = Path("src/prompts"),
        environment: str = "default",
        **kwargs
    ):
        super().__init__(prompts_dir=prompts_dir, **kwargs)
        self.environment = environment
        self.override_dir = prompts_dir / environment
    
    def load(self, prompt_name: str, allow_missing: bool = False):
        """Load with environment-specific override support."""
        # Try environment-specific version first
        if self.override_dir.exists():
            override_path = self.override_dir / f"{prompt_name}.json"
            if override_path.exists():
                self.prompts_dir = self.override_dir
                result = super().load(prompt_name, allow_missing=True)
                self.prompts_dir = self.prompts_dir.parent
                if result:
                    return result
        
        # Fall back to default
        return super().load(prompt_name, allow_missing)


# ============================================================================
# Example 7: Prompt Validation CLI
# ============================================================================

def validate_all_prompts():
    """CLI command to validate all prompts."""
    loader = PromptLoader(prompts_dir=Path("src/prompts"))
    results = loader.validate_all()
    
    errors = {name: err for name, err in results.items() if err}
    
    if errors:
        print("❌ Validation errors found:")
        for name, error in errors.items():
            print(f"  - {name}: {error}")
        return False
    else:
        print(f"✅ All {len(results)} prompts are valid!")
        return True


# ============================================================================
# Example 8: Warm Cache on Startup
# ============================================================================

def warm_prompt_cache():
    """Pre-load all prompts into cache on application startup."""
    loader = PromptLoader(
        prompts_dir=Path("src/prompts"),
        enable_cache=True
    )
    
    # Load all prompts to warm cache
    prompts = loader.load_all()
    print(f"Cached {len(prompts)} prompts")
    
    return loader


if __name__ == "__main__":
    # Run examples
    print("=== Example 1: Basic Usage ===")
    example_basic_usage()
    
    print("\n=== Example 7: Validate Prompts ===")
    validate_all_prompts()
    
    print("\n=== Example 5: Test Draft Creation ===")
    test_draft_creation()
    print("✅ Test passed!")
