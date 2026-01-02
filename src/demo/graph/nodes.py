
from langchain_core.messages import SystemMessage
from demo.graph.state import GraphState
from demo.graph.nodes.n_input import input_check

from demo.graph.model import llm

# 3. Define a model node
def call_model(state: GraphState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# # Node for InputCheck (N1)
# def input_check(state: GraphState):
#     # Logic to check input can be added here
#     # For now, it just passes through as per the diagram N1 -> END
#     return state
