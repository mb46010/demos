from demo.config.config import Config
from demo.graph.graph import create_draft_agent

try:
    config = Config()

    # Skip full agent verification due to environment issues with add_subgraph

    print("Creating draft agent...")
    draft_agent = create_draft_agent(config)
    print("Draft agent created successfully.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()
