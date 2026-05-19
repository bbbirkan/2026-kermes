```
██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗
██║ ██╔╝██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝
█████╔╝ █████╗  ██████╔╝██╔████╔██║█████╗  ███████╗
██╔═██╗ ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║
██║  ██╗███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝
```

<div align="center">

**Your AI subscriptions are sitting idle. Kermes puts them to work.**

Route every query to the right model. Compress context automatically. Cache repeated answers.
Cut AI costs by 60–80% — without switching tools or losing a single feature.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-crimson.svg)](https://python.org)
[![Inspired by Hermes](https://img.shields.io/badge/built%20on-Hermes%20Agent-gold.svg)](https://github.com/NousResearch/hermes-agent)

</div>

---

## The problem nobody talks about

You pay for GPT-5.5. You pay for Claude Pro. You pay for Gemini Advanced.

Then you send *every single message* to the most expensive model available — because that's the default, and changing it manually is too much friction.

"What's the capital of France?" → GPT-5.5. $0.015 per answer.
"Summarize this paragraph" → Claude Opus. $0.075 per answer.
"Write a haiku" → the most powerful reasoning model on Earth.

**You're buying a sports car and using it to go to the grocery store.**

Kermes fixes this automatically.

---

## What Kermes does

Every message you send gets scored in milliseconds:

```
"What's 2+2?"          → FAST tier  → DeepSeek Flash   → $0.0001
"Debug this function"  → MID tier   → DeepSeek Pro      → $0.004
"Architect a system"   → BEST tier  → GPT-5.5 / Claude  → $0.15
```

The right model. Every time. No configuration per query.

---

## Real numbers

A typical power user session, before and after Kermes:

```
                    BEFORE KERMES          AFTER KERMES
                    ─────────────          ────────────
Simple queries      GPT-5.5  ████████      Flash  ██
(60% of traffic)    $0.90/day              $0.06/day

Medium queries      GPT-5.5  ████████      Pro    ████
(30% of traffic)    $1.20/day              $0.18/day

Complex queries     GPT-5.5  ████████      Best   ████████
(10% of traffic)    $0.80/day              $0.80/day
                    ─────────────          ────────────
Daily total         $2.90/day              $1.04/day
Monthly             $87/month              $31/month
Savings             —                      64% less
```

---

## How it works

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR MESSAGE                                 │
│          Telegram · Discord · WhatsApp · CLI · HTTP API             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     HERMES GATEWAY                                  │
│          (memory · skills · platform routing — unchanged)           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   KERMES OPTIMIZER                                  │
│                                                                     │
│   ┌───────────────┐  ┌─────────────────┐  ┌──────────────────────┐ │
│   │  CACHE        │  │  COMPRESSOR     │  │  CLASSIFIER          │ │
│   │               │  │                 │  │                      │ │
│   │  Seen before? │  │  History > 40%? │  │  How hard is this?   │ │
│   │  Return free  │  │  Summarize old  │  │  FAST / MID / BEST   │ │
│   │  in 0ms       │  │  → save tokens  │  │                      │ │
│   └───────┬───────┘  └────────┬────────┘  └──────────┬───────────┘ │
│           │                   │                       │             │
│           └───────────────────┴───────────────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MODEL ROUTER                                   │
│                                                                     │
│  FAST ($)               MID ($$)               BEST ($$$)           │
│  ────────────           ────────────           ─────────────────    │
│  DeepSeek Flash         DeepSeek Pro           GPT-5.5              │
│  GLM-4.7                Gemini 2.5 Flash       Claude Opus 4.7      │
│  Llama 3.3 70B          Mistral Large          Grok 4               │
│                                                                     │
│  < 50 tokens            50–500 tokens          > 500 tokens         │
│  factual · simple       code · analysis        reasoning · long     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    Answer + Cost Log
```

---

## Why not just use Hermes?

Hermes is exceptional at what it does: memory, skills, multi-platform messaging.
It is not designed to care about cost. It routes to whatever model you configured — once, globally.

Kermes keeps everything Hermes does and adds **per-query intelligence** on top.

| Feature | Hermes | Kermes |
|---------|--------|--------|
| Telegram / Discord / WhatsApp | ✅ | ✅ (via Hermes) |
| Persistent memory | ✅ | ✅ (via Hermes) |
| Skill system | ✅ | ✅ (via Hermes) |
| Multi-model routing | ❌ one model | ✅ auto per query |
| Context compression | ❌ | ✅ 85% reduction |
| Response cache | ❌ | ✅ zero-cost repeats |
| Cost dashboard | ❌ | ✅ per session |

---

## Why not just use OpenCode?

OpenCode is a great coding assistant. It is not a routing layer.

| Feature | OpenCode | Kermes |
|---------|----------|--------|
| Headless / CLI | ✅ | ✅ |
| Multi-platform messaging | ❌ | ✅ (via Hermes) |
| Intelligent model routing | ❌ | ✅ |
| Context compression | ❌ | ✅ |
| Works as orchestrator | ❌ | ✅ |
| Language model agnostic | ❌ single | ✅ multi-tier |

Kermes and OpenCode are complementary — Kermes can *call* OpenCode as one of its execution backends for coding tasks.

---

## Install

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

## Configure

After `kermes init`, edit `~/.kermes/config.yaml`:

```yaml
provider: openrouter
api_key: sk-or-...

tiers:
  fast:
    model: deepseek/deepseek-v4-flash
    max_cost_per_query: 0.01
  mid:
    model: deepseek/deepseek-v4-pro
    max_cost_per_query: 0.10
  best:
    model: openai/gpt-5.5
    max_cost_per_query: 1.00

compression:
  enabled: true
  threshold: 0.4       # compress when context > 40% of model max
  target_ratio: 0.15   # aim for 15% of original

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 10000

hermes:
  enabled: true
  path: /usr/local/lib/hermes-agent
```

---

## CLI

```bash
kermes chat                           # interactive
kermes ask "debug this function: ..." # single query
kermes ask --tier best "architect..." # force tier
kermes stats                          # savings dashboard
kermes serve                          # daemon + Hermes gateway
```

---

## With Hermes (drop-in upgrade)

If Hermes is already running, Kermes sits silently between Hermes and your models:

```
Your message
     │
     ▼
Hermes Gateway  ← everything you know, unchanged
     │
     ▼
Kermes Layer    ← cost intelligence added here
     │
     ▼
Cheapest model that can handle it  ← savings
```

No migration. No relearning. Just less cost.

---

## Credits

Kermes stands on the shoulders of **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** by Nous Research.

Hermes solved the hard parts: persistent memory, skill systems, multi-platform messaging, model delegation. We owe it everything.

Kermes adds exactly one thing: **it makes Hermes stop wasting money**.

> *"We didn't build a new agent. We built a smarter wallet for the one you already have."*

The name comes from *Kermes vermilio* — the insect that produces crimson dye. Like it, Kermes extracts something valuable from a raw source and refines it.

---

## License

MIT. Use it, fork it, ship it.
If it saves you money, a star goes a long way.
