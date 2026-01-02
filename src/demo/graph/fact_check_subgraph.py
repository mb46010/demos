"""run with uv: uv run python src/demo/graph/fact_check_subgraph.py ."""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from demo.graph.consts import NODE_FACT_CHECKER_CLAIM_EXTRACTOR, NODE_REWRITER
from demo.graph.nodes.n_fact_extractor import fc_extractor, needs_rewrite
from demo.graph.nodes.n_fact_rewriter import fc_rewriter
from demo.graph.state import GraphState
from demo.utils.loader import load_fact_checker
from demo.utils.save_json import save_json

load_dotenv()


def create_fact_check_subgraph(add_loader_node: bool = True):
    """Create the agent."""
    subgraph_builder = StateGraph(GraphState)

    # get feedback
    subgraph_builder.add_node(NODE_FACT_CHECKER_CLAIM_EXTRACTOR, fc_extractor)

    # rewriter
    subgraph_builder.add_node(NODE_REWRITER, fc_rewriter)

    subgraph_builder.add_edge(START, NODE_FACT_CHECKER_CLAIM_EXTRACTOR)

    # rewrite if needed
    subgraph_builder.add_conditional_edges(
        NODE_FACT_CHECKER_CLAIM_EXTRACTOR, needs_rewrite, {"True": NODE_REWRITER, "False": END}
    )
    subgraph_builder.add_edge(NODE_REWRITER, NODE_FACT_CHECKER_CLAIM_EXTRACTOR)

    subgraph = subgraph_builder.compile()
    return subgraph
