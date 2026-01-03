from langchain_core.messages import SystemMessage

from demo.graph.model import llm
from demo.graph.nodes.n_draft import create_draft
from demo.graph.nodes.n_input import check_valid, input_check
from demo.graph.state import GraphState


# 3. Define a model node
def call_model(state: GraphState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}
