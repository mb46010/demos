"""Refactoring Example: From Hardcoded to Config-Driven

This file shows how to refactor your existing code to use the new config system.
"""

# ============================================================================
# BEFORE: Hardcoded Dependencies
# ============================================================================

# OLD: src/demo/graph/model.py
# ❌ This file has hardcoded LLM configuration
"""
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",  # Wrong model name!
    temperature=0,
    max_tokens=10000,
).with_retry(
    retry_if_exception_type=(Exception,),
    wait_exponential_jitter=True,
    stop_after_attempt=3,
)
"""

# OLD: src/demo/graph/nodes/n_draft.py
# ❌ Directly imports hardcoded LLM
"""
from demo.graph.model import llm  # Hardcoded!
from demo.utils.loader import load_prompt

def create_draft(state: GraphState):
    prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw
    
    filled_prompt = prompt_template.format(
        manager_input=json.dumps(state[KEY_INPUT], indent=2),
        review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
    )
    
    response = llm.invoke([HumanMessage(content=filled_prompt)])  # Hardcoded llm
    # ...
"""

# OLD: src/demo/graph/graph.py
# ❌ Imports node with hardcoded dependencies
"""
from demo.graph.nodes.n_draft import create_draft

def create_full_agent():
    agent_builder = StateGraph(GraphState)
    agent_builder.add_node(NODE_CREATE_DRAFT, create_draft)
    # ...
"""

# OLD: src/demo/graph/app.py
# ❌ No configuration at all
"""
if __name__ == "__main__":
    data = load_data(input_path=args.input_file)
    
    config = {
        KEY_INPUT: data["input"],
        # ...
    }
    
    agent_builder = create_full_agent()  # No config!
    agent = agent_builder.compile()
    response = agent.invoke(config)
"""


# ============================================================================
# AFTER: Config-Driven with Dependency Injection
# ============================================================================

# NEW: src/demo/config.py (Already created)
"""
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o"
    temperature: float = 0.0
    # ...
    
    def create_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            # ...
        )
"""

# NEW: src/demo/graph/nodes/n_draft.py
# ✅ Factory pattern with injected dependencies
"""
from demo.utils.prompt_loader import PromptLoader

def create_draft_node(llm, prompt_loader: PromptLoader):
    '''Factory function that creates a draft node with injected dependencies.'''
    
    def create_draft(state: GraphState):
        # Use injected prompt_loader
        filled_prompt = prompt_loader.get_formatted(
            "n_draft",
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
        )
        
        # Use injected llm
        response = llm.with_structured_output(DraftResult).invoke(
            [HumanMessage(content=filled_prompt)]
        )
        
        return {KEY_DRAFT: response.model_dump()["draft"]}
    
    return create_draft
"""

# NEW: src/demo/graph/graph.py
# ✅ Graph builder accepts config
"""
from demo.config import AppConfig
from demo.graph.nodes.n_draft import create_draft_node

def create_full_agent(config: AppConfig):
    '''Create agent with dependency injection.'''
    agent_builder = StateGraph(GraphState)
    
    # Create LLM and prompt loader from config
    llm = config.create_llm()
    prompt_loader = config.create_prompt_loader()
    
    # Create nodes with injected dependencies
    draft_node = create_draft_node(llm, prompt_loader)
    
    agent_builder.add_node(NODE_CREATE_DRAFT, draft_node)
    # ...
    
    return agent_builder
"""

# NEW: src/demo/graph/app.py
# ✅ Loads config from environment
"""
from demo.config import get_config

if __name__ == "__main__":
    # Load configuration from environment
    app_config = get_config()
    
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
"""


# ============================================================================
# STEP-BY-STEP REFACTORING PLAN
# ============================================================================

"""
PHASE 1: Setup (1 hour)
-----------------------
1. Create config.py
   cp config.py src/demo/config.py

2. Create .env file
   cp .env.example .env
   # Edit .env with your API key

3. Update requirements.txt
   echo "pydantic-settings>=2.0.0" >> requirements.txt
   pip install pydantic-settings

4. Test config
   python -c "from demo.config import get_config; print(get_config())"


PHASE 2: Refactor Nodes (2-3 hours)
------------------------------------
For each node file:

1. Change signature to factory pattern:
   # Before
   def create_draft(state):
       pass
   
   # After
   def create_draft_node(llm, prompt_loader):
       def create_draft(state):
           pass
       return create_draft

2. Replace hardcoded imports:
   # Before
   from demo.graph.model import llm
   from demo.utils.loader import load_prompt
   
   # After
   # (these are now injected parameters)

3. Update prompt loading:
   # Before
   prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
   if isinstance(prompt_raw, list):
       prompt_template = "\n".join(prompt_raw)
   
   # After
   prompt_template = prompt_loader.get_formatted("n_draft", ...)

Order of refactoring:
- [ ] n_draft.py
- [ ] n_input.py
- [ ] n_rewriter.py
- [ ] n_fact_extractor.py


PHASE 3: Update Graph Builders (1 hour)
----------------------------------------
1. Update graph.py:
   # Before
   from demo.graph.nodes.n_draft import create_draft
   
   def create_full_agent():
       agent_builder.add_node("draft", create_draft)
   
   # After
   from demo.graph.nodes.n_draft import create_draft_node
   
   def create_full_agent(config: AppConfig):
       llm = config.create_llm()
       loader = config.create_prompt_loader()
       
       draft_node = create_draft_node(llm, loader)
       agent_builder.add_node("draft", draft_node)

2. Update subgraph builders similarly


PHASE 4: Update Entry Points (30 minutes)
------------------------------------------
1. Update app.py:
   from demo.config import get_config
   
   app_config = get_config()
   agent = create_full_agent(config=app_config)

2. Update test scripts:
   from demo.config import create_test_config
   
   config = create_test_config(model_name="gpt-4o-mini")


PHASE 5: Update Tests (2 hours)
--------------------------------
1. Update test files to use config:
   from demo.config import create_test_config
   from demo.utils.prompt_loader import MockPromptLoader
   
   def test_draft_creation():
       config = create_test_config()
       mock_llm = Mock()
       mock_loader = MockPromptLoader(prompts={...})
       
       node = create_draft_node(mock_llm, mock_loader)
       result = node(test_state)

2. Add config-specific tests:
   def test_config_validation():
       with pytest.raises(ValueError):
           AppConfig(temperature=3.0)  # Out of range


PHASE 6: Cleanup (30 minutes)
------------------------------
1. Delete old files:
   rm src/demo/graph/model.py

2. Update imports in __init__.py files

3. Remove old loader functions:
   # From src/demo/utils/loader.py, remove:
   - load_prompt()
   - load_prompts()

4. Update documentation


PHASE 7: Verification (1 hour)
-------------------------------
1. Run all tests:
   pytest tests/ -v

2. Test end-to-end:
   python src/demo/graph/app.py --input_file data/input.json

3. Verify environment switching:
   ENVIRONMENT=production python src/demo/graph/app.py

4. Check logging:
   LOG_LEVEL=DEBUG python src/demo/graph/app.py


Total Time: ~8-10 hours
"""


# ============================================================================
# TESTING THE REFACTORED CODE
# ============================================================================

def test_example():
    """Example test showing new pattern."""
    from unittest.mock import Mock
    from demo.config import create_test_config
    from demo.utils.prompt_loader import MockPromptLoader
    from demo.graph.nodes.n_draft import create_draft_node
    
    # Create test config
    config = create_test_config()
    
    # Create mocks
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.model_dump.return_value = {"draft": "Test draft"}
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
    
    mock_loader = MockPromptLoader(prompts={
        "n_draft": "Create draft: {manager_input}"
    })
    
    # Create node with dependency injection
    draft_node = create_draft_node(mock_llm, mock_loader)
    
    # Test
    state = {
        "input": {"rating": "exceeds"},
        "structure": {"sections": []}
    }
    
    result = draft_node(state)
    
    # Verify
    assert result["draft"] == "Test draft"
    print("✅ Test passed!")


# ============================================================================
# ROLLBACK PLAN
# ============================================================================

"""
If something goes wrong during migration:

1. Keep old code in nodes/deprecated/ folder:
   mkdir src/demo/graph/nodes/deprecated
   cp src/demo/graph/nodes/n_draft.py src/demo/graph/nodes/deprecated/

2. Create feature flag:
   USE_NEW_CONFIG = os.getenv("USE_NEW_CONFIG", "false").lower() == "true"
   
   if USE_NEW_CONFIG:
       config = get_config()
       agent = create_full_agent(config)
   else:
       agent = create_full_agent_old()

3. Test both paths in parallel

4. After 1 week of stable operation:
   rm -rf src/demo/graph/nodes/deprecated/
"""


# ============================================================================
# BENEFITS AFTER REFACTORING
# ============================================================================

"""
BEFORE:
- ❌ Hardcoded LLM (can't change model without code change)
- ❌ Hardcoded paths (breaks on different machines)
- ❌ Difficult to test (can't mock LLM easily)
- ❌ No validation (crashes at runtime)
- ❌ Secrets in code (security risk)

AFTER:
- ✅ Configurable LLM (change via .env)
- ✅ Portable paths (works on any machine)
- ✅ Easy to test (dependency injection)
- ✅ Validated config (catches errors early)
- ✅ Secure secrets (from environment/secret manager)
- ✅ Environment-specific settings (dev/staging/prod)
- ✅ Type safety (IDE autocomplete)
- ✅ Documentation (via Field descriptions)
"""


if __name__ == "__main__":
    print("=" * 60)
    print("Refactoring Example")
    print("=" * 60)
    
    print("\n✅ Running test example...")
    test_example()
    
    print("\n📋 Next steps:")
    print("1. Create config.py and .env")
    print("2. Refactor nodes one by one")
    print("3. Update graph builders")
    print("4. Update entry points")
    print("5. Update tests")
    print("6. Clean up old code")
    print("7. Verify everything works")
