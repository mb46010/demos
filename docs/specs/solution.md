#  Bias amplification 

Issue: Could the model systematically write stronger reviews for certain groups?

## Approach
1. Verify Batch Bias Detector: 
- sentiment analysis of reviews for each manager and employee groups.
- compare choice of words (e.g. "excellent" vs "good") vs claims in input.
- compare tone used vs employee groups.

2. Flag inconsistent reviews: 
- e.g. flag poor rating with high praise for successes.

3. Don't feed AI PII, like names, gender, etc. Fill them in after the manager approved the review.

4. Check for inconsistencies in the manager input (across direct reports at a point in time, and for the same employee over time).

5. Check for inconsistencies in the employee history (across past managers and current manager for the same role).



# Fabrication
Issue: The model might add details not in the input (the '87%' wasn't in the bullets)

## Approach
- Both in `AI`and `Guardrail System` add instructions to enforce that only claims in the input are used.
- Add a `Reviewer` node that can verifies independently each claim in the the draft review and reject it if it contains unsupported claims.


# Tone inconsistency 
Issue: Different managers get different quality outputs

## Approach: 
- Enforce templats for required sections of review (same structure for all managers, flow can be personalized for better communication). 
- Enforce dictionary of performance level ratings (same wording for adjective and qualifiers for all managers).
Ask manager to prepend performance keyword to each claim.
- Add AI instructions to `AI` and `Guardrail System` to enforce tone of voice.

### Example Review Template

``` markdown
# Year Goals

# Successes

# Challenges

# Performance rating and discussion

# Strengths

# Development Areas

# Feedback
```

### Example Ratings

``` json
{
    "performance_rating_qualifier": {"Exceeds expectations": "excellent", "Meets expectations": "good", "Does not meet expectations": "poor"},
    "strenth_area_qualifier": {"Exceeds expectations": "excellent", "Meets expectations": "good", "Does not meet expectations": "poor"},
}

```


# Audit trail 
Goal: If an employee disputes their review, can we show what the AI did vs. the manager?

## Architecture Diagram

``` mermaid
flowchart LR

M[Manager]  -->|Input Bullets| AI[AI Generation]
AI -->|Draft Review incl. data requests| UI{Manager UI}
AI --> R{AI Reviewer}
R -->|Approved| AI
R -->|Reject with reason| AI
UI -->|Revised Instructions| AI
UI -->|Edit and Accept| G[Guardrail System]
G -->|Approved: Change Detected| P[Performance Review System]
G -->|Reject: No Human Input| UI
```

## High level details

1. Guardrail System: checks for:
    - Manager rubberstamping AI output (no changes)
    - Tone inconsistency
    - Unsupported claims (requires justification, claim, etc)
    - Break of policy (e.g. discriminatory language)
    Incidents are logged for HR review. 

2. Log Manager Input and changes (review instructions and manual edits) in immutable audit trail.
3. Add `Accept`button and record timestamp, and SSO Auth details of manager in immutable audit trail.


# Deeper dive into key components

## Reviewer to prevent Fabrication 

Add a `Fact Check` node that fact checks the draft review against the manager input.

Prompt: You are a performance review reviewer. Your task is to review the `draft review` provided by the AI system and fact check it against the `manager input`.
You have access to a dictionry of performance level ratings and a dictionary of performance keywords and you must ensure that the appropriate rating and keywords are used.

Your output should be a JSON object with the following structure:


``` json
{
    "verified_claims": [
        {
            "claim_text": "Claim 1",
            "manager_input": "Justification for claim 1",
        }
    ],
    "unjusted_claims": [
        {
            "claim_text": "Claim 1",
            "manager_input": "Justification for claim 1",
            "reason_for_rejection": "missing justification, claim not in manager input, wrong rating, wrong keyword, fabricated details, low semantic similarity",
            "corrections": [
                {"before": "Claim 1", "after": "Claim 1"}
            ]
        }
    ]
}
```

### Steps:
1. Extract all claims from the `draft review` and `manager input`. We'll use Google's langextract to extract claims from both draft review and manager input.
1.1. Identify all claims in the `draft review`
1.2. For each claim, identify the corresponding claim in the `manager input`.
3. Analyze each review_claim/input_claim pair, check if it is supported.
4. If the claim is supported, add it to the `verified_claims` list.
5. If the claim is not supported, add it to the `unjusted_claims` list, including the reason for rejection and a proposal for correction.
6. Always compute semantic similarity between the claim and the manager input. If this is lower than 0.8, add it to the `unjusted_claims` list and propose a correction.
7. Return the JSON object.

#### Comparing a review claim with the manager input

1. Compute semantic similarity between the claim and the manager input. If this is lower than 0.8, add it to the `unjusted_claims` list and propose a correction.
2. Compute metrics such as number of words, number of adjectives and verbs (use spacy).
3. Identify words missing from the manager input. Are they general (fillers, better flow) or specific (potentially fabricated details)?
4. Identify numbers, percentages, dates, etc. in the claim and check if they are supported (potentially in different format) by the manager input.
5. Identify acronyms, abbreviations, etc. in the claim and check if they are supported by the manager input.
6. Identify proper nouns, etc. in the claim and check if they are supported by the manager input.
7. Always report any detail in the review that lacks support from the manager input.


### Logging:
- Log all traces
- Flag traces that highlight factual inconsistencies for A/B testing of better prompts.

### Performance evaluation and red teaming
- Test the reviewer system with adversarial AI, prompted to add subtle fabrications or tone mismatch to the draft review or manager input.



## Audit trail model
The system should store an immutable audit trail of all interactions between the manager and the AI system.

### Data schema
```json
{
    "employee_name": "...",
    "manager_name": "...",
    "performance_cycle": "...",
    "manager_input": "...",
    "manager_input": "...",
    "manager_input_timestamp": "...",
    "manager_input_sso_auth": "...",
    "AI_first_draft": "...",
    "AI_first_draft_timestamp": "...",
    "AI_first_draft_sso_auth": "...",
    "AI_manager_interactions": [
        {
            "manager_input": "...",
            "manager_input_timestamp": "...",
            "manager_input_sso_auth": "...",
            "AI_output": "...",
            "AI_output_timestamp": "...",
        }
    ],
    "AI_final_draft": "...",
    "AI_final_draft_timestamp": "...",
    "AI_final_draft_sso_auth": "...",
    "manager_edits": [
        {
            "before": "...",
            "after": "...",
            "timestamp": "...",
            "manager_input_sso_auth": "...",
        }
    ],    
    "AI_guardrail_interactions": [
        ...
        ],
    "manager_final_draft": "...",
    "manager_final_draft_timestamp": "...",
    "manager_final_draft_sso_auth": "...",
    "
}


```

### Data storage
- Storage in immutable datalake with audit trail of changes. Store for 7+ years.
- Use as source of truth for HR and Legal to audit reviews (e.g. to check for bias, fabrication, tone inconsistency, etc).


