"""Context compressor: shrinks conversation history before sending to the model."""

from __future__ import annotations
from typing import Any


def compress(
    messages: list[dict[str, Any]],
    threshold: float = 0.4,
    target_ratio: float = 0.15,
    protect_last_n: int = 12,
    model_max_tokens: int = 32000,
) -> list[dict[str, Any]]:
    """
    Compress messages if total token estimate exceeds threshold * model_max_tokens.
    Always keeps the system prompt and the last protect_last_n messages intact.
    Summarizes the middle section.
    """
    if not messages:
        return messages

    total_tokens = sum(_token_estimate(m.get("content", "")) for m in messages)
    budget = int(model_max_tokens * threshold)

    if total_tokens <= budget:
        return messages

    system_msgs = [m for m in messages if m.get("role") == "system"]
    non_system = [m for m in messages if m.get("role") != "system"]

    if len(non_system) <= protect_last_n:
        return messages

    to_compress = non_system[:-protect_last_n]
    tail = non_system[-protect_last_n:]

    summary_text = _summarize(to_compress)
    summary_msg = {
        "role": "system",
        "content": f"[Earlier conversation summary]: {summary_text}",
    }

    return system_msgs + [summary_msg] + tail


def _summarize(messages: list[dict[str, Any]]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "?")
        content = m.get("content", "")
        if isinstance(content, str):
            snippet = content[:200].replace("\n", " ")
            parts.append(f"{role}: {snippet}")
    return " | ".join(parts)


def _token_estimate(text: str) -> int:
    if not isinstance(text, str):
        return 10
    return max(1, len(text) // 4)
