"""run with uv: uv run python src/demo/graph/graph.py ."""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from demo.graph.nodes.n_draft import create_draft
from demo.graph.nodes.n_input import check_valid, input_check
from demo.graph.state import GraphState
from demo.utils.loader import get_manager_id, load_data
from demo.utils.save_json import save_json

load_dotenv()


def create_agent():
    """Create the agent."""
    agent_builder = StateGraph(GraphState)

    agent_builder.add_node("InputCheck", input_check)
    agent_builder.add_node("CreateDraft", create_draft)

    agent_builder.add_edge(START, "InputCheck")
    agent_builder.add_conditional_edges("InputCheck", check_valid, {"True": "CreateDraft", "False": END})
    agent_builder.add_edge("CreateDraft", END)

    agent = agent_builder.compile()
    return agent
