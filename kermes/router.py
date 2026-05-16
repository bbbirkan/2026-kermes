"""Model router: sends each query to the cheapest model that can handle it."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from .classifier import Tier, classify
from .compressor import compress
from .cache import ResponseCache


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = {
    Tier.FAST: "deepseek/deepseek-v4-flash",
    Tier.MID: "deepseek/deepseek-v4-pro",
    Tier.BEST: "openai/gpt-5.5",
}


@dataclass
class RouteResult:
    response: str
    tier: Tier
    model: str
    cached: bool
    tokens_used: int
    cost_usd: float
    latency_ms: int


@dataclass
class SessionStats:
    total_queries: int = 0
    cache_hits: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0
    savings_usd: float = 0.0
    tier_counts: dict[str, int] = field(default_factory=lambda: {"fast": 0, "mid": 0, "best": 0})


# Approximate cost per 1M tokens (input+output blended), USD
COST_PER_M = {
    "deepseek/deepseek-v4-flash": 0.14,
    "deepseek/deepseek-v4-pro": 2.61,
    "openai/gpt-5.5": 17.50,
    "z-ai/glm-4.7": 1.19,
    "meta-llama/llama-3.3-70b-instruct": 0.59,
    "mistralai/mistral-large": 3.00,
    "google/gemini-2.5-flash": 0.60,
    "x-ai/grok-4.20": 4.00,
    "anthropic/claude-opus-4-7": 15.00,
}


class KermesRouter:
    def __init__(self, config: dict[str, Any]):
        self.api_key = config["api_key"]
        self.provider_url = config.get("provider_url", OPENROUTER_URL)

        tier_cfg = config.get("tiers", {})
        self.models = {
            Tier.FAST: tier_cfg.get("fast", {}).get("model", DEFAULT_MODELS[Tier.FAST]),
            Tier.MID: tier_cfg.get("mid", {}).get("model", DEFAULT_MODELS[Tier.MID]),
            Tier.BEST: tier_cfg.get("best", {}).get("model", DEFAULT_MODELS[Tier.BEST]),
        }

        cache_cfg = config.get("cache", {})
        self.cache = ResponseCache(
            cache_dir=config.get("cache_dir", "~/.kermes/cache"),
            ttl=cache_cfg.get("ttl_seconds", 3600),
            max_entries=cache_cfg.get("max_entries", 10000),
        ) if cache_cfg.get("enabled", True) else None

        self.routing_cfg = config.get("routing", {})
        self.compression_cfg = config.get("compression", {})
        self.stats = SessionStats()

    def route(self, messages: list[dict], system: str | None = None) -> RouteResult:
        query = _last_user_message(messages)

        classification = classify(query, self.routing_cfg)
        tier = classification.tier
        model = self.models[tier]

        # Cache check
        if self.cache:
            cached = self.cache.get(query, model)
            if cached:
                self.stats.cache_hits += 1
                self.stats.total_queries += 1
                return RouteResult(
                    response=cached, tier=tier, model=model,
                    cached=True, tokens_used=0, cost_usd=0.0, latency_ms=0,
                )

        # Compress context
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        if self.compression_cfg.get("enabled", True):
            all_messages = compress(
                all_messages,
                threshold=self.compression_cfg.get("threshold", 0.4),
                target_ratio=self.compression_cfg.get("target_ratio", 0.15),
                protect_last_n=self.compression_cfg.get("protect_last_n", 12),
            )

        # Call model
        t0 = time.time()
        response_text, tokens = self._call(model, all_messages)
        latency_ms = int((time.time() - t0) * 1000)

        cost = _estimate_cost(model, tokens)
        best_cost = _estimate_cost(self.models[Tier.BEST], tokens)
        savings = max(0.0, best_cost - cost)

        self.stats.total_queries += 1
        self.stats.tokens_used += tokens
        self.stats.cost_usd += cost
        self.stats.savings_usd += savings
        self.stats.tier_counts[tier.value] += 1

        if self.cache:
            self.cache.set(query, model, response_text)

        return RouteResult(
            response=response_text, tier=tier, model=model,
            cached=False, tokens_used=tokens, cost_usd=cost, latency_ms=latency_ms,
        )

    def _call(self, model: str, messages: list[dict]) -> tuple[str, int]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/bbbirkan/2026-kermes",
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 8192,
        }
        with httpx.Client(timeout=120) as client:
            resp = client.post(self.provider_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", len(choice) // 4)
        return choice, tokens

    def print_stats(self) -> None:
        s = self.stats
        print(f"\n{'─'*50}")
        print(f"  KERMES SESSION STATS")
        print(f"{'─'*50}")
        print(f"  Queries      : {s.total_queries}")
        print(f"  Cache hits   : {s.cache_hits}")
        print(f"  Tokens used  : {s.tokens_used:,}")
        print(f"  Cost         : ${s.cost_usd:.4f}")
        print(f"  Saved vs best: ${s.savings_usd:.4f}")
        print(f"  Tier split   : fast={s.tier_counts['fast']} mid={s.tier_counts['mid']} best={s.tier_counts['best']}")
        print(f"{'─'*50}\n")


def _last_user_message(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            content = m.get("content", "")
            return content if isinstance(content, str) else str(content)
    return ""


def _estimate_cost(model: str, tokens: int) -> float:
    rate = COST_PER_M.get(model, 5.0)
    return (tokens / 1_000_000) * rate
