"""run with uv: uv run python src/demo/graph/graph.py ."""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from demo.graph.consts import NODE_CREATE_DRAFT, NODE_INPUT_CHECK
from demo.graph.nodes.n_draft import create_draft
from demo.graph.nodes.n_input import check_valid, input_check
from demo.graph.state import GraphState
from demo.utils.loader import get_manager_id, load_data
from demo.utils.save_json import save_json

load_dotenv()


def create_agent():
    """Create the agent."""
    agent_builder = StateGraph(GraphState)

    agent_builder.add_node(NODE_INPUT_CHECK, input_check)
    agent_builder.add_node(NODE_CREATE_DRAFT, create_draft)

    agent_builder.add_edge(START, NODE_INPUT_CHECK)
    agent_builder.add_conditional_edges(NODE_INPUT_CHECK, check_valid, {"True": NODE_CREATE_DRAFT, "False": END})
    agent_builder.add_edge(NODE_CREATE_DRAFT, END)

    agent = agent_builder.compile()
    return agent
