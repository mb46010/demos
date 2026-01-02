from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from demo.graph.state import GraphState

# 1. Init an openai model
llm = ChatOpenAI(model="gpt-4o")

# 3. Define a model node
def call_model(state: GraphState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Node for InputCheck (N1)
def input_check(state: GraphState):
    # Logic to check input can be added here
    # For now, it just passes through as per the diagram N1 -> END
    return state
