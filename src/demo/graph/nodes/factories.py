import loggging

from demo.graph.model import get_default_llm
from demo.graph.nodes.n_draft import create_draft
from demo.graph.nodes.n_fact_extractor import fc_extractor
from demo.graph.nodes.n_fact_rewriter import fact_rewriter
from demo.graph.state import GraphState
from demo.utils.loader import PromptLoader

logger = logging.getLogger(__name__)


def make_draft_creator(llm, prompt_loader):
    def create_draft(state: GraphState) -> dict:
        logger.info("Stage: %s started.", NODE_CREATE_DRAFT)

        # Load prompt and join if it's a list
        prompt_template = load_prompt(Path("src/prompts/n_draft.json"))

        # Fill the prompt
        filled_prompt = prompt_template.format(
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
        )

        # Generate draft
        # Invoke LLM with structured output
        response = llm.with_structured_output(DraftResult).invoke([HumanMessage(content=filled_prompt)])

        # Update state
        if response is None:
            raise ValueError("LLM failed to return a valid structured output.")
        try:
            draft_result = response.model_dump()
        except Exception as e:
            logger.exception("Failed to parse LLM response: %s", str(e))
            raise

        # print()
        # print("LLM Draft Result:")
        # pprint(draft_result)

        logger.info("Stage: %s completed.", NODE_CREATE_DRAFT)
        return {KEY_DRAFT: draft_result["draft"]}

    return create_draft


def make_fact_checker(llm, prompt_loader):
    def check_facts(state: GraphState) -> dict:
        # Implementation here
        pass

    return check_facts


# graph.py
def create_agent(llm=None):
    llm = llm or get_default_llm()
    loader = PromptLoader()

    builder = StateGraph(GraphState)
    builder.add_node("draft", make_draft_creator(llm, loader))
    builder.add_node("fact_check", make_fact_checker(llm, loader))

    return builder
