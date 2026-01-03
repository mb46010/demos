"""run with uv: uv run python src/demo/graph/graph.py ."""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.pregel import RetryPolicy

from demo.graph.consts import NODE_CREATE_DRAFT, NODE_INPUT_CHECK
from demo.graph.fact_check_subgraph import create_fact_check_subgraph
from demo.graph.nodes.n_draft import create_draft
from demo.graph.nodes.n_input import check_valid, input_check
from demo.graph.state import GraphState
from demo.utils.loader import get_manager_id, load_data
from demo.utils.save_json import save_json

load_dotenv()
DEFAULT_MAX_ATTEMPTS = 3


def create_full_agent(max_attempts: int = DEFAULT_MAX_ATTEMPTS):
    """Create the full agent with draft and fact check."""
    agent_builder = StateGraph(GraphState)

    agent_builder.add_node(NODE_INPUT_CHECK, input_check, retry=RetryPolicy(max_attempts=max_attempts))
    agent_builder.add_node(NODE_CREATE_DRAFT, create_draft, retry=RetryPolicy(max_attempts=max_attempts))

    agent_builder.add_edge(START, NODE_INPUT_CHECK)
    agent_builder.add_conditional_edges(NODE_INPUT_CHECK, check_valid, {"True": NODE_CREATE_DRAFT, "False": END})

    # Add the fact check subgraph as a node/subgraph
    fact_check_subgraph = create_fact_check_subgraph()
    agent_builder.add_subgraph("fact_check", fact_check_subgraph)

    # Connect the draft creation to the fact check
    agent_builder.add_edge(NODE_CREATE_DRAFT, "fact_check")
    agent_builder.add_edge("fact_check", END)

    return agent_builder


def create_draft_agent(max_attempts: int = DEFAULT_MAX_ATTEMPTS):
    """Create the agent."""
    agent_builder = StateGraph(GraphState)

    agent_builder.add_node(NODE_INPUT_CHECK, input_check, retry=RetryPolicy(max_attempts=max_attempts))
    agent_builder.add_node(NODE_CREATE_DRAFT, create_draft, retry=RetryPolicy(max_attempts=max_attempts))

    agent_builder.add_edge(START, NODE_INPUT_CHECK)
    agent_builder.add_conditional_edges(NODE_INPUT_CHECK, check_valid, {"True": NODE_CREATE_DRAFT, "False": END})
    agent_builder.add_edge(NODE_CREATE_DRAFT, END)

    return agent_builder
