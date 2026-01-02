"""run with uv: uv run python src/demo/graph/test_fact_checker.py --input_file ..."""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv

from demo.graph.consts import (
    KEY_DRAFT,
    KEY_FACT_CHECKER_CLAIMS_EXTRACTED,
    KEY_FACT_CHECKER_CLAIMS_VERIFIED,
    KEY_INPUT,
)
from demo.graph.fact_check_subgraph import create_fact_check_subgraph
from demo.utils.loader import load_fact_checker
from demo.utils.save_json import save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

agent = create_fact_check_subgraph()


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/input_fact_checker.json",
        help="Path to the input file (default: data/input.json)",
    )
    args = parser.parse_args()

    # Load data
    data = load_fact_checker(fact_checker_path=Path(args.input_file))
    # print(f"Manager Input (from {args.input_file}):")
    # pprint(data["input"])

    config = {
        KEY_INPUT: data["input"],
        KEY_DRAFT: data["draft"],
    }

    response = agent.invoke(config)

    # # Check if we have a draft (success path) or just check result (failure path)
    if response.get(KEY_FACT_CHECKER_CLAIMS_VERIFIED):
        print("Success! Draft created.")
        pprint(response[KEY_FACT_CHECKER_CLAIMS_VERIFIED])
        final_output = response[KEY_FACT_CHECKER_CLAIMS_VERIFIED]
    else:
        print("Validation failed or incomplete.")
        pprint(response.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED))
        final_output = response.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED)

    print("Final State Keys:")
    pprint(list(response.keys()))

    timedate = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_json(response, f"data/output_fact_checker_{timedate}.json")
