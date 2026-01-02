"""run with uv: uv run python src/demo/graph/fact_check_subgraph.py ."""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from demo.graph.consts import NODE_FACT_CHECKER_CLAIM_EXTRACTOR, NODE_FACT_CHECKER_CLAIM_VERIFIER
from demo.graph.nodes.n_fact_extractor import check_fc_result, fc_extractor
from demo.graph.nodes.n_fact_verifier import fc_verifier
from demo.graph.state import GraphState
from demo.utils.loader import load_fact_checker
from demo.utils.save_json import save_json

load_dotenv()


def create_fact_check_subgraph():
    """Create the agent."""
    subgraph_builder = StateGraph(GraphState)

    subgraph_builder.add_node(NODE_FACT_CHECKER_CLAIM_EXTRACTOR, fc_extractor)
    subgraph_builder.add_node(NODE_FACT_CHECKER_CLAIM_VERIFIER, fc_verifier)

    subgraph_builder.add_edge(START, NODE_FACT_CHECKER_CLAIM_EXTRACTOR)
    subgraph_builder.add_conditional_edges(
        NODE_FACT_CHECKER_CLAIM_EXTRACTOR, check_fc_result, {"True": NODE_FACT_CHECKER_CLAIM_VERIFIER, "False": END}
    )
    subgraph_builder.add_edge(NODE_FACT_CHECKER_CLAIM_VERIFIER, END)

    subgraph = subgraph_builder.compile()
    return subgraph
