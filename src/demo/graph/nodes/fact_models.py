"""Module defining Pydantic models for claim and fact extraction."""

from typing import List

from pydantic import BaseModel, Field


class Source(BaseModel):
    """Source information for a claim."""

    section: str = Field(..., description="The section name where the claim was found")
    sentence_index: int = Field(..., description="The zero-based index of the sentence within the section")


class Signals(BaseModel):
    """Linguistic and factual signals extracted from text."""

    numbers: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    percentages: List[str] = Field(default_factory=list)
    currency: List[str] = Field(default_factory=list)
    quantities: List[str] = Field(default_factory=list)
    acronyms: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    qualifiers: List[str] = Field(default_factory=list)
    modality: List[str] = Field(default_factory=list)
    intensity: List[str] = Field(default_factory=list)
    causality: List[str] = Field(default_factory=list)


class Claim(BaseModel):
    """An individual claim extracted from the document."""

    claim_id: str = Field(..., description="Unique identifier for the claim (e.g., c1, c2)")
    text: str = Field(..., description="The text of the claim")
    source: Source
    signals: Signals
    sentiment: str = Field(..., description="Sentiment of the claim (e.g., positive, neutral, negative)")
    primary_type: str = Field(..., description="Primary type of the claim (e.g., success, growth, skill)")
    tags: List[str] = Field(default_factory=list)


class Fact(BaseModel):
    """An individual fact extracted for comparison with claims."""

    fact_id: str = Field(..., description="Unique identifier for the fact (e.g., f1, f2)")
    text: str = Field(..., description="The text of the fact")
    rating: str = Field(..., description="Rating associated with the fact")
    signals: Signals
    sentiment: str = Field(..., description="Sentiment of the fact")
    primary_type: str = Field(..., description="Primary type of the fact")
    tags: List[str] = Field(default_factory=list)


class Scores(BaseModel):
    """Similarity scores for claim-fact linking."""

    semantic_similarity: float = Field(..., description="Semantic similarity score between 0 and 1")
    lexical_overlap: float = Field(..., description="Lexical overlap score between 0 and 1")
    number_match: str = Field(..., description="How numbers match (e.g., exact, partial, none)")
    entity_match_ratio: float = Field(..., description="Ratio of matching entities")
    modality_match: str = Field(..., description="How modality matches")


class Link(BaseModel):
    """A link between a claim and supporting/refuting facts."""

    claim_id: str = Field(..., description="ID of the claim")
    fact_ids: List[str] = Field(..., description="List of IDs of the facts that support the claim")
    scores: Scores
    verdict: str = Field(..., description="Verdict: supported, unsupported, or partially supported")
    reasons: List[str] = Field(default_factory=list, description="Reasons for the verdict")


class ClaimFactPairs(BaseModel):
    """Entire document structured into claims and facts."""

    version: str = Field(default="1.0")
    claims: List[Claim] = Field(default_factory=list)
    facts: List[Fact] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)


class FactPairs(BaseModel):
    """Structured output wrapper for the fact extractor node."""

    claim_fact_pairs: ClaimFactPairs = Field(..., description="The claim-fact pairs data structure")
