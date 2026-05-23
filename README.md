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

Route every query to the right model. Compress context. Cache answers.
Cut AI costs 60–80% — without touching a single tool you already use.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-crimson.svg)](https://python.org)
[![Built on Hermes](https://img.shields.io/badge/built%20on-Hermes%20Agent-gold.svg)](https://github.com/NousResearch/hermes-agent)

</div>

---

## The bill that started this

I run AI agents 16 hours a day.

Telegram → Discord → WhatsApp → GitHub → Trello → YouTube — all routed through a single server, all powered by language models. I thought I had it figured out.

I had three subscriptions:

```
Claude Pro      $20/month  ✓ paid
ChatGPT Plus    $20/month  ✓ paid
Gemini Advanced $10/month  ✓ paid
──────────────────────────
Total subs      $50/month  ✓ under control
```

Then I checked my API invoice for the first 10 days of the month.

**$80.**

In ten days. On top of the subscriptions I was already paying.

Extrapolated: **$240/month in API costs alone** — because my agents were sending everything to the most expensive model available, regardless of what the task actually needed. "What time is it in Tokyo?" → GPT-5.5. "Fix this typo" → Claude Opus. "Translate one sentence" → the most powerful reasoning system ever built.

The subscriptions I paid for? Barely touched. The free quota? Ignored. The API meter? Running full speed.

I was paying for a first-class seat and also buying a second ticket to stand in the aisle.

So I built Kermes.

---

## What it does

Every message gets scored before it touches a model:

```
Is it cached?   ──→  return instantly          (zero tokens, zero cost)
     │
     ▼
How complex?
     │
     ├── Simple  ──→  DeepSeek Flash  ($0.03/M)
     ├── Medium  ──→  DeepSeek Pro    ($0.14/M)
     └── Complex ──→  GPT-5.5 / Claude Opus  ($5–15/M)
```

The right model. Every time. Zero configuration per query.

---

## Real numbers

Same usage pattern, before and after:

```
                    BEFORE                  AFTER KERMES
                    ──────                  ────────────
Simple queries      GPT-5.5   ████████      Flash    ██
(60% of traffic)    $0.90/day               $0.06/day

Medium queries      GPT-5.5   ████████      Pro      ████
(30% of traffic)    $1.20/day               $0.18/day

Complex queries     GPT-5.5   ████████      Best     ████████
(10% of traffic)    $0.80/day               $0.80/day
                    ──────────              ────────────────
Daily               $2.90                   $1.04
Monthly             $87                     $31
                                            ↑ 64% less
```

No capability lost. The hard questions still get the best model.
The easy ones stop burning premium tokens.

---

## How it fits into your stack

```
┌───────────────────────────────────────────────────────────┐
│                      YOUR WORLD                           │
│   Telegram · Discord · WhatsApp · Slack · CLI · HTTP      │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────┐
│                   HERMES GATEWAY                          │
│       memory · skills · platform routing (unchanged)      │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────┐
│                  KERMES OPTIMIZER  ← NEW                  │
│                                                           │
│   ┌───────────┐   ┌─────────────┐   ┌─────────────────┐  │
│   │  CACHE    │   │ COMPRESSOR  │   │   CLASSIFIER    │  │
│   │           │   │             │   │                 │  │
│   │ Seen it?  │   │ History 40% │   │ FAST/MID/BEST   │  │
│   │ → free    │   │ → summarize │   │ per query       │  │
│   └───────────┘   └─────────────┘   └─────────────────┘  │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────┐
│                    MODEL ROUTER                           │
│                                                           │
│  FAST ($)            MID ($$)           BEST ($$$)        │
│  ─────────────       ──────────         ──────────────    │
│  DeepSeek Flash      DeepSeek Pro       GPT-5.5           │
│  GLM-4.7             Gemini 2.5 Flash   Claude Opus 4.7   │
│  Llama 3.3 70B       Mistral Large      Grok 4            │
│                                                           │
│  < 50 tokens         50–500 tokens      > 500 tokens      │
│  factual · quick     code · analysis    reasoning · long  │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
                    Answer  +  Cost log
```

---

## Why not just Hermes?

Hermes is brilliant. Memory, skills, Telegram, Discord, WhatsApp, tools — it handles all of it.

It does not handle cost. It routes to whatever model you set globally, forever.

| | Hermes | Kermes |
|---|---|---|
| Multi-platform messaging | ✅ | ✅ (via Hermes) |
| Persistent memory | ✅ | ✅ (via Hermes) |
| Skill system | ✅ | ✅ (via Hermes) |
| Per-query model routing | ❌ | ✅ |
| Context compression | ❌ | ✅ |
| Response cache | ❌ | ✅ |
| Cost dashboard | ❌ | ✅ |

Kermes is not a Hermes replacement. It is Hermes with a cost brain bolted on.

---

## Why not just OpenCode?

OpenCode is a sharp coding tool. It is not a routing layer.

| | OpenCode | Kermes |
|---|---|---|
| Great at coding tasks | ✅ | ✅ (can delegate to OpenCode) |
| Multi-platform messaging | ❌ | ✅ |
| Intelligent model routing | ❌ | ✅ |
| Context compression | ❌ | ✅ |
| Works with any LLM backend | ❌ | ✅ |

They are complementary. Kermes can call OpenCode as a backend for coding tasks
while routing everything else to the appropriate model.

---

## Why not just AGY?

AGY (Antigravity CLI) is Google's subscription-based AI coding assistant. Zero API cost, runs locally, powerful — but single-purpose.

| | AGY | Kermes |
|---|---|---|
| Zero API cost (subscription) | ✅ | ✅ (delegates to AGY) |
| Multi-platform messaging | ❌ | ✅ |
| Intelligent model routing | ❌ | ✅ |
| Context compression | ❌ | ✅ |
| Works with non-Google models | ❌ | ✅ |

Kermes can route **BEST-tier** queries to AGY (subscription, zero marginal cost) instead of paid APIs — the most expensive queries become free.

```yaml
# Use AGY as your zero-cost BEST tier
tiers:
  best:
    provider: agy
    model: subscription
    max_cost_per_query: 0.00   # it's already paid for
```

---

## Install

```bash
# One-liner
curl -fsSL https://raw.githubusercontent.com/bbbirkan/2026-kermes/main/install.sh | bash

# pip
pip install kermes-agent

# manual
git clone https://github.com/bbbirkan/2026-kermes.git
cd 2026-kermes && pip install -e . && kermes init
```

---

## Configure

`~/.kermes/config.yaml` — generated by `kermes init`:

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
  threshold: 0.4       # compress when history > 40% of model max
  target_ratio: 0.15

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 10000

hermes:
  enabled: true
  path: /usr/local/lib/hermes-agent
```

---

## Use it

```bash
kermes chat                     # interactive session
kermes ask "your question"      # single query, auto-routed
kermes ask --tier best "..."    # force the best model
kermes stats                    # see what you saved today
kermes serve                    # daemon mode + Hermes gateway
```

---

## The name

*Kermes vermilio* is the insect that produces crimson dye — the same dye that gave
the color "crimson" its name. For centuries, people refined raw plant material through
kermes to extract something far more valuable.

The logo merges **K** and **H**: Kermes carrying Hermes inside it.
Crimson red body. Amber gold feet.

That's the idea: take what Hermes already does, refine it, make it more valuable.

---

## Credits

None of this works without **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** by [Nous Research](https://nousresearch.com). They built the hard foundation. We added the cost layer.

> *"We didn't build a new agent. We built a smarter wallet for the one you already have."*

---

## License

MIT. Use it, modify it, ship it.
If it saves you money, a ⭐ keeps the project alive.
