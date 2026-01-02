from typing import Any, Dict


def parse_fact_extractor_output(claims_extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Parse fact extractor output."""
    links = claims_extracted.get("links", [])
    claims = claims_extracted.get("claims", [])
    facts = claims_extracted.get("facts", [])

    rejected_claims = [x for x in links if x.get("verdict") != "supported"]

    feedback = []

    for claim in rejected_claims:
        item = {
            "verdict": claim.get("verdict"),
            "reason": claim.get("reasons"),
        }
        claim_id = claim.get("claim_id")
        if claim_id:
            claim_text = [x.get("text") for x in claims if x.get("claim_id") == claim_id]
        else:
            claim_text = []
        fact_ids = claim.get("fact_ids") or []
        fact_texts = [x.get("text") for x in facts if x and x.get("fact_id") in fact_ids]

        item["claim_text"] = claim_text
        item["fact_texts"] = fact_texts
        feedback.append(item)

    return feedback
