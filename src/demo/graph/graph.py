from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from demo.graph.state import GraphState
from demo.graph.nodes import input_check
from demo.utils.loader import load_data, get_manager_id

# Define a small graph
# flowchart LR
#     START((START)) -->|user input| N1{InputCheck}
#     N1 --> END

agent_builder = StateGraph(GraphState)

agent_builder.add_node("InputCheck", input_check)

agent_builder.add_edge(START, "InputCheck")
agent_builder.add_edge("InputCheck", END)

agent = agent_builder.compile()

# def get_initial_state() -> GraphState:
#     """Prepare the initial state with loaded data."""
#     data = load_data()
#     print("Manager Input:")
#     print(data["input"])


#     # Initialize empty messages list as required by MessageState
#     messages = []
#     return {
#         "messages": messages,
#         "input": data["input"],
#         "structure": data["structure"],
#         "qualifiers": data["qualifiers"],
#         "draft": {},
#         "manager_id": get_manager_id(data["input"]),
#     }


from demo.utils.save_json import save_json

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    data = load_data()
    print("Manager Input:")
    print(data["input"])

    config = {
        "input": data["input"],
        "structure": data["structure"],
        "qualifiers": data["qualifiers"],
        "manager_id": get_manager_id(data["input"]),
    }

    response = agent.invoke(config)
    print(response)
    
    save_json(response, "data/output_00.json")
    