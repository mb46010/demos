"""run with uv: uv run python src/demo/graph/app.py --input_file data/input_invalid.json."""

import argparse
import logging
from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv

from demo.graph.consts import (
    KEY_CHECK_RESULT,
    KEY_DRAFT,
    KEY_INPUT,
    KEY_MANAGER_ID,
    KEY_QUALIFIERS,
    KEY_STRUCTURE,
)
from demo.graph.graph import create_agent
from demo.utils.loader import get_manager_id, load_data
from demo.utils.save_json import save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

agent = create_agent()


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/input.json",
        help="Path to the input file (default: data/input.json)",
    )
    args = parser.parse_args()

    # Load data
    data = load_data(input_path=args.input_file)
    print(f"Manager Input (from {args.input_file}):")
    pprint(data["input"])

    config = {
        KEY_INPUT: data["input"],
        KEY_STRUCTURE: data["structure"],
        KEY_QUALIFIERS: data["qualifiers"],
        KEY_MANAGER_ID: get_manager_id(data["input"]),
    }

    response = agent.invoke(config)

    # Check if we have a draft (success path) or just check result (failure path)
    if response.get(KEY_DRAFT):
        print("Success! Draft created.")
        pprint(response[KEY_DRAFT])
        final_output = response[KEY_DRAFT]
    else:
        print("Validation failed or incomplete.")
        pprint(response.get(KEY_CHECK_RESULT))
        final_output = response.get(KEY_CHECK_RESULT)

    print("Final State Keys:")
    pprint(list(response.keys()))

    timedate = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_json(response, f"data/output_{timedate}.json")
