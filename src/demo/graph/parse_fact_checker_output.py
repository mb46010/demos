"""run with uv: uv run python src/demo/graph/parse_fact_checker_output.py --input_file ..."""

import argparse
import logging
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv

from demo.utils.loader import load_fact_checker_output
from demo.utils.parse_facts import parse_fact_extractor_output

data = load_fact_checker_output(Path("data/output/output_fact_checker_20260102_175002.json"))

feedback = parse_fact_extractor_output(data.get("claims_extracted", {}))

pprint(feedback)
