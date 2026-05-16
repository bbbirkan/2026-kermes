"""Query classifier: assigns a routing tier (fast / mid / best) to each query."""

from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum


class Tier(str, Enum):
    FAST = "fast"
    MID = "mid"
    BEST = "best"


BEST_KEYWORDS = [
    "architect", "design system", "step by step", "reason through",
    "write a full", "implement from scratch", "research and summarize",
    "multi-step", "plan", "strategy", "compare and contrast",
]

CODE_PATTERNS = [
    r"```", r"\bdef \b", r"\bclass \b", r"\bfunction\b", r"\bimport\b",
    r"SELECT\b", r"CREATE TABLE", r"\bnpm\b", r"\bdocker\b",
]

SIMPLE_PATTERNS = [
    r"^(what|who|when|where|is|are|how many|translate)\b",
    r"^(merhaba|selam|naber|nasıl|ne zaman|kim|nerede)\b",
]


@dataclass
class Classification:
    tier: Tier
    token_estimate: int
    reason: str


def classify(query: str, config: dict | None = None) -> Classification:
    cfg = config or {}
    simple_threshold = cfg.get("simple_threshold", 50)
    complex_threshold = cfg.get("complex_threshold", 500)
    force_keywords = cfg.get("force_best_keywords", BEST_KEYWORDS)

    token_estimate = _estimate_tokens(query)

    # Force BEST for known complex patterns
    q_lower = query.lower()
    for kw in force_keywords:
        if kw.lower() in q_lower:
            return Classification(Tier.BEST, token_estimate, f"keyword: '{kw}'")

    # Check for code
    has_code = any(re.search(p, query, re.IGNORECASE) for p in CODE_PATTERNS)
    if has_code and token_estimate > simple_threshold:
        return Classification(Tier.MID, token_estimate, "code detected")

    # Simple factual
    is_simple = any(re.match(p, query.strip(), re.IGNORECASE) for p in SIMPLE_PATTERNS)
    if is_simple and token_estimate < simple_threshold:
        return Classification(Tier.FAST, token_estimate, "simple factual pattern")

    # Token-based fallback
    if token_estimate < simple_threshold:
        return Classification(Tier.FAST, token_estimate, "short query")
    if token_estimate < complex_threshold:
        return Classification(Tier.MID, token_estimate, "medium query")
    return Classification(Tier.BEST, token_estimate, "long/complex query")


def _estimate_tokens(text: str) -> int:
    # ~4 chars per token approximation
    return max(1, len(text) // 4)
