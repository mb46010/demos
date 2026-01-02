"""run with uv: uv run python src/demo/graph/app.py data/input_invalid.json  ."""

import argparse
import logging
from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv

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
        "input": data["input"],
        "structure": data["structure"],
        "qualifiers": data["qualifiers"],
        "manager_id": get_manager_id(data["input"]),
    }

    response = agent.invoke(config)
    last_stage_name = "check_result"
    last_stage_result = response.get(last_stage_name)

    print("Last stage result:")
    pprint(last_stage_result)

    timedate = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_json(response, f"data/output_{timedate}.json")
