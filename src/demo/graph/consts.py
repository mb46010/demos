"""Constants for the graph nodes and keys."""

# Node Names
NODE_INPUT_CHECK = "input_check"
NODE_CREATE_DRAFT = "create_draft"
NODE_FACT_CHECKER_CLAIM_EXTRACTOR = "claim_extractor"
NODE_REWRITER = "rewriter"

# State Keys
KEY_INPUT = "input"
KEY_STRUCTURE = "structure"
KEY_QUALIFIERS = "qualifiers"
KEY_MANAGER_ID = "manager_id"
KEY_DRAFT = "draft"
KEY_CHECK_RESULT = "check_result"

# Fact Checker Keys
KEY_FACT_CHECKER_CLAIMS_EXTRACTED = "claims_extracted"
KEY_REWRITER = KEY_DRAFT  # Same key, so the loop is terminated
