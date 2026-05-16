```
██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗
██║ ██╔╝██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝
█████╔╝ █████╗  ██████╔╝██╔████╔██║█████╗  ███████╗
██╔═██╗ ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║
██║  ██╗███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝
```

<div align="center">

**Token-smart AI agent system.**
Route queries to the right model. Compress context. Cache responses.
Cut your AI costs without losing capability.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-crimson.svg)](https://python.org)
[![Inspired by Hermes](https://img.shields.io/badge/inspired%20by-Hermes%20Agent-gold.svg)](https://github.com/NousResearch/hermes-agent)

</div>

---

## What is Kermes?

**Kermes** is a lightweight wrapper around [Hermes Agent](https://github.com/NousResearch/hermes-agent) that adds an intelligent token optimization layer.

The name comes from the *Kermes vermilio* insect — the source of the crimson dye that colors its logo. Just as kermes dye is extracted and refined from a raw source, Kermes the system extracts and refines the best of Hermes Agent, adding cost intelligence on top.

**Core idea:** Not every query needs GPT-5.5. A quick factual question costs the same tokens whether you send it to a $5/M model or a $0.03/M model. Kermes routes each query to the cheapest model that can handle it — and caches the ones it has seen before.

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                          USER INPUT                               │
│         Telegram · Discord · WhatsApp · CLI · HTTP API            │
└─────────────────────────┬─────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                    KERMES GATEWAY                                  │
│              (Hermes Agent — unchanged core)                      │
│                                                                   │
│   SOUL.md · MEMORY.md · USER.md · skills/                        │
└─────────────────────────┬─────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                   TOKEN OPTIMIZER LAYER                           │
│                                                                   │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐   │
│  │   CACHE     │   │  COMPRESSOR  │   │     CLASSIFIER      │   │
│  │             │   │              │   │                     │   │
│  │ hash lookup │   │ trim context │   │ simple / medium /   │   │
│  │ semantic    │   │ summarize    │   │ complex / creative  │   │
│  │ similarity  │   │ old messages │   │                     │   │
│  └──────┬──────┘   └──────┬───────┘   └──────────┬──────────┘   │
│         │                 │                       │              │
│         └─────────────────┴───────────────────────┘             │
└─────────────────────────┬─────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                      MODEL ROUTER                                 │
│                                                                   │
│   TIER 1 — FAST ($)        TIER 2 — MID ($$)   TIER 3 — BEST ($$$)│
│   ──────────────────       ─────────────────   ──────────────────│
│   DeepSeek V4 Flash        DeepSeek V4 Pro     GPT-5.5           │
│   GLM-4.7                  Gemini 2.5 Flash    Claude Opus 4.7   │
│   Llama 3.3 70B            Mistral Large       Grok 4.20         │
│                                                                   │
│   < 50 tokens              50–500 tokens       > 500 tokens      │
│   factual / simple         code / analysis     reasoning / long  │
│   no tools needed          tools allowed       multi-step plan   │
└─────────────────────────┬─────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                   RESPONSE + STATS                                │
│                                                                   │
│   answer → user    cache write    cost delta    savings log       │
└───────────────────────────────────────────────────────────────────┘
```

---

## Token Savings: How It Works

### 1. Query Classification
Every incoming message is scored on three axes:
- **Length** — token estimate of prompt + expected response
- **Complexity** — presence of code, multi-step reasoning, tool use
- **Novelty** — seen before? cached?

Based on the score, the query is assigned a tier (FAST / MID / BEST).

### 2. Context Compression
Before sending to any model, the conversation history is compressed:
- Messages older than the protection window are summarized
- Duplicate system context is removed
- Default target: compress to 15% of original when over threshold

### 3. Response Cache
Identical (or near-identical) queries return cached responses instantly — zero tokens, zero cost.
TTL is configurable per tier.

### 4. Cost Dashboard
Every session logs token usage and cost per model. You see exactly how much you saved vs. sending everything to the premium tier.

---

## Quick Install

```bash
# One-liner
curl -fsSL https://raw.githubusercontent.com/bbbirkan/2026-kermes/main/install.sh | bash

# Or with pip
pip install kermes-agent

# Or manual
git clone https://github.com/bbbirkan/2026-kermes.git
cd 2026-kermes
pip install -e .
kermes init
```

---

## Configuration

After `kermes init`, edit `~/.kermes/config.yaml`:

```yaml
provider: openrouter          # openrouter | anthropic | openai | novitaai
api_key: sk-or-...

tiers:
  fast:
    model: deepseek/deepseek-v4-flash
    max_cost_per_query: 0.01   # USD
  mid:
    model: deepseek/deepseek-v4-pro
    max_cost_per_query: 0.10
  best:
    model: openai/gpt-5.5
    max_cost_per_query: 1.00

routing:
  simple_threshold: 50         # tokens
  complex_threshold: 500       # tokens
  force_best_keywords:
    - "write a full"
    - "architect"
    - "reason step by step"

compression:
  enabled: true
  threshold: 0.4               # compress when context > 40% of max
  target_ratio: 0.15
  protect_last_n: 12

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 10000

hermes:
  enabled: true                # use Hermes gateway for messaging platforms
  path: /usr/local/lib/hermes-agent
```

---

## CLI Usage

```bash
# Interactive mode
kermes chat

# Single query
kermes ask "what is the capital of France"

# Force a tier
kermes ask --tier fast "summarize this: ..."
kermes ask --tier best "architect a distributed system for..."

# Show savings dashboard
kermes stats

# Run as daemon (with Hermes gateway)
kermes serve
```

---

## With Hermes Agent

Kermes wraps Hermes — it does not replace it. If you already have Hermes running:

```yaml
# in ~/.kermes/config.yaml
hermes:
  enabled: true
  path: /usr/local/lib/hermes-agent
```

All Hermes platforms (Telegram, Discord, WhatsApp, Signal, etc.) work as-is.
Kermes only intercepts the model call and applies routing + compression before it reaches the API.

```
Telegram message
      ↓
Hermes Gateway  (unchanged)
      ↓
Kermes Token Optimizer  ← NEW LAYER
      ↓
Cheapest capable model  ← SAVINGS
```

---

## Logo

The Kermes logo is a merged **K**+**H** letterform.
The body is crimson red — the color of *Kermes vermilio* dye, from which the word "crimson" itself derives.
The bottom strokes (feet/serifs of both letters) are rendered in amber gold.
Read as **K**, but carrying the **H** of Hermes within it.

---

## Credits & Inspiration

Kermes would not exist without **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** by [Nous Research](https://nousresearch.com).

Hermes solved the hard problem: multi-platform messaging, persistent memory, skill systems, and heterogeneous model delegation — all in one cohesive architecture. We are deeply grateful for that work.

Kermes adds exactly one thing on top: **cost intelligence**. Nothing more, nothing less.

> "We did not build a new agent. We built a smarter wallet for the agent you already have."

---

## License

MIT — free to use, modify, and distribute.
If Kermes saves you money, consider starring the repo or contributing back.
