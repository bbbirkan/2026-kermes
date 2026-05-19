# CLI Orchestration Research — 2026-05-19

> Research document for Kermes' future "CLI Router" layer.
> Proof-of-concept complete: subscription-based orchestration with zero API cost works.

---

## Vision: CLI Subscription Layer Instead of API

Kermes currently routes through OpenRouter API (pay per token).
Researched alternative: **using CLI tools headlessly via their subscription modes.**

```
Current Kermes:
  User → Classifier → OpenRouter API → Model → Response
                       (billed per token)

Potential Kermes v2:
  User → Classifier → CLI Router → claude / gemini / opencode → Response
                       (flat-rate subscription, zero per-token cost)
```

---

## Available CLI Tools and Status

### 1. Claude Code CLI (`claude`)
- **Subscription:** Anthropic Pro / Max
- **Headless command:** `claude -p "prompt" --dangerously-skip-permissions --output-format text`
- **Pipe:** ✅ Works directly
- **Auth:** OAuth / keychain (no API key required)
- **Asyncio:** ✅ Works with `asyncio.create_subprocess_exec`

```bash
claude -p "task" --dangerously-skip-permissions --output-format text
```

### 2. Google Gemini CLI (`gemini`)
- **Subscription:** Google One / Gemini Advanced + free tier
- **Headless command:** `gemini --prompt "task" --yolo`
- **Pipe:** ✅ Works directly
- **Auth:** `GOOGLE_API_KEY` or OAuth
- **Asyncio:** ✅ Works with `asyncio.create_subprocess_exec`
- **Model:** Gemini 2.5 Flash / Pro

```bash
gemini --prompt "task" --yolo
```

### 3. OpenCode CLI (`opencode`)
- **Subscription:** OpenCode Zen / OpenCode Go
- **Headless command:** `opencode run --dangerously-skip-permissions "prompt"`
- **Pipe:** ❌ Requires TTY — silent when piped
- **Fix:** `script -q -c "opencode run ..." /dev/null`
- **Auth:** OpenCode Zen → DeepSeek v4 Pro
- **Asyncio:** ✅ Works with script wrapper

```bash
script -q -c "opencode run --dangerously-skip-permissions 'task'" /dev/null
```

**Critical note:** OpenCode goes silent without a TTY. Not a bug — it's TUI-based by design. The `script` wrapper creates a pseudo-TTY and solves this completely.

---

## Terminal Orchester v0.1 — Working Demo

**File:** `/root/2026-orchester/terminal_orchester.py`

Three orchestration modes, all tested and working:

### PARALLEL mode (recommended)
```
Task → Claude + OpenCode (simultaneous) → Gemini synthesis → Final
```
- Fastest: 2 steps
- Gemini merges both perspectives

### CHAIN mode
```
Task → Claude → OpenCode (sees Claude) → Gemini (sees both) → Final
```
- Each agent reads the previous agent's output
- Creates a debate/revision dynamic

### SEQUENTIAL mode
```
Task → Gemini draft → Claude + OpenCode critique (parallel) → Gemini final
```
- Gemini revises its own draft based on critique
- Most thorough, most steps

---

## Integration Proposal for Kermes

### Add a CLI Tier

Current `router.py` tier system:
```
FAST   → DeepSeek Flash (OpenRouter API)   ← billed per token
MID    → DeepSeek Pro (OpenRouter API)     ← billed per token
BEST   → GPT-5.5 (OpenRouter API)         ← billed per token
```

Proposed additional tier:
```
FAST   → DeepSeek Flash (OpenRouter API)   ← billed per token
MID    → DeepSeek Pro (OpenRouter API)     ← billed per token
BEST   → GPT-5.5 (OpenRouter API)         ← billed per token
---
CLI_FAST   → OpenCode (DeepSeek v4 Pro)    ← zero cost (subscription)
CLI_MID    → Gemini (Gemini 2.5)           ← zero cost (subscription)
CLI_BEST   → Claude (Claude Sonnet/Opus)   ← zero cost (subscription)
```

When user enables "subscription mode," all traffic routes to the CLI tier.

### Example `router.py` update

```python
from enum import Enum

class Tier(Enum):
    FAST = "fast"
    MID = "mid"
    BEST = "best"
    CLI_FAST = "cli_fast"    # OpenCode — zero cost
    CLI_MID = "cli_mid"      # Gemini — zero cost
    CLI_BEST = "cli_best"    # Claude — zero cost

CLI_BACKENDS = {
    Tier.CLI_FAST: ask_opencode,
    Tier.CLI_MID:  ask_gemini,
    Tier.CLI_BEST: ask_claude,
}
```

### Config addition (`config.example.yaml`)

```yaml
router:
  mode: api          # "api", "cli", or "hybrid"
  cli:
    fast: opencode   # DeepSeek v4 Pro via OpenCode Zen subscription
    mid: gemini      # Gemini 2.5 via Google subscription
    best: claude     # Claude via Anthropic Pro subscription
  api:
    fast: deepseek/deepseek-v4-flash
    mid: deepseek/deepseek-v4-pro
    best: openai/gpt-5.5
```

---

## Cost Comparison: CLI Subscription vs API

| Tool | API mode | Subscription mode |
|------|----------|-------------------|
| Claude | $3–15/M tokens | Claude Pro $20/mo flat |
| Gemini | $0.075–2.5/M tokens | Google One $10/mo flat |
| OpenCode | — | OpenCode Zen $10/mo flat |
| **Total** | Variable, unbounded | ~$40/mo fixed |

**Break-even:** ~3–5M tokens/month. Above that, subscription wins.

---

## Technical Requirements

```
python3 asyncio      — concurrent CLI calls
shlex                — safe argument quoting
script (bsd-compat)  — pseudo-TTY for OpenCode
CLAUDE_CODE_BUBBLEWRAP=1  — Claude on root servers
```

No pip packages required beyond stdlib.

---

## Tested Scenario

**Question:** "What are the 3 most critical technical decisions when building an AI automation system?"

**Result (PARALLEL mode):**
- Claude: 152 words ✓
- OpenCode: 169 words ✓
- Gemini: 276 word synthesis ✓
- Total time: ~45 seconds
- API cost: **$0.00**

---

## References

- Working code: `/root/2026-orchester/terminal_orchester.py`
- Test outputs: `/root/2026-orchester/debates/`
