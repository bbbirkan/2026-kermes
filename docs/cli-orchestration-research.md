# CLI Orkestrasyon Araştırması — 2026-05-19

> Bu belge, Kermes'in gelecekteki "CLI Router" katmanı için yapılan
> araştırma ve deneylerin özetidir. Sıfır API maliyetiyle çalışan
> subscription-tabanlı orkestrasyon mümkün — aşağıda kanıtı var.

---

## Vizyon: API Yerine CLI Subscription Katmanı

Kermes şu an OpenRouter API'si üzerinden modellere gidiyor (her token para).
Araştırılan alternatif: **CLI araçları subscription modlarıyla headless kullanmak.**

```
Mevcut Kermes:
  Kullanıcı → Classifier → OpenRouter API → Model → Yanıt
                            (token başına ücret)

Potansiyel Kermes v2:
  Kullanıcı → Classifier → CLI Router → claude / gemini / opencode → Yanıt
                            (flat-rate subscription, token ücret yok)
```

---

## Mevcut CLI Araçları ve Durumları

### 1. Claude Code CLI (`claude`)
- **Subscription:** Anthropic Pro / Max
- **Headless komutu:** `claude -p "prompt" --dangerously-skip-permissions --output-format text`
- **Pipe:** ✅ Doğrudan çalışır
- **Auth:** OAuth / keychain (API key gerektirmez)
- **Asyncio:** ✅ `asyncio.create_subprocess_exec` ile sorunsuz

```bash
claude -p "görev" --dangerously-skip-permissions --output-format text
```

### 2. Google Gemini CLI (`gemini`)
- **Subscription:** Google One / Gemini Advanced + ücretsiz tier
- **Headless komutu:** `gemini --prompt "görev" --yolo`
- **Pipe:** ✅ Doğrudan çalışır
- **Auth:** `GOOGLE_API_KEY` veya OAuth
- **Asyncio:** ✅ `asyncio.create_subprocess_exec` ile sorunsuz
- **Model:** Gemini 2.5 Flash/Pro

```bash
gemini --prompt "görev" --yolo
```

### 3. OpenCode CLI (`opencode`)
- **Subscription:** OpenCode Zen / OpenCode Go üyeliği
- **Headless komutu:** `opencode run --dangerously-skip-permissions "prompt"`
- **Pipe:** ❌ TTY gerektiriyor — pipe'da boş çıktı!
- **Çözüm:** `script -q -c "opencode run ..." /dev/null`
- **Auth:** OpenCode Zen → DeepSeek v4 Pro
- **Asyncio:** ✅ script wrapper ile sorunsuz

```bash
script -q -c "opencode run --dangerously-skip-permissions 'görev'" /dev/null
```

**Kritik not:** OpenCode TTY olmadan sessiz kalıyor. Bu bir bug değil, tasarım — TUI tabanlı bir araç. `script` ile pseudo-TTY açmak çözüm.

---

## Terminal Orchester v0.1 — Çalışan Demo

**Dosya:** `/root/2026-orchester/terminal_orchester.py`

3 orkestrasyon modu, kanıtlanmış çalışıyor:

### PARALLEL modu (önerilen)
```
Görev → Claude + OpenCode (eş zamanlı) → Gemini sentezi → Final
```
- En hızlı: 2 adım
- Gemini iki perspektifi birleştirir

### CHAIN modu
```
Görev → Claude → OpenCode (Claude'u görür) → Gemini (ikisini görür) → Final
```
- Her ajan bir öncekinin çıktısını okur
- Tartışma/revizyon dinamiği

### SEQUENTIAL modu
```
Görev → Gemini taslak → Claude + OpenCode eleştiri (paralel) → Gemini final
```
- Gemini kendi taslağını eleştirilere göre düzeltir
- En kapsamlı, en fazla adım

---

## Kermes'e Entegrasyon Önerisi

### CLI Tier'ı Ekle

Mevcut `router.py` tier sistemi:
```
FAST  → DeepSeek Flash (OpenRouter API)
MID   → DeepSeek Pro (OpenRouter API)
BEST  → GPT-5.5 (OpenRouter API)
```

Önerilen ek tier:
```
FAST   → DeepSeek Flash (OpenRouter API)      ← maliyet: token başına
MID    → DeepSeek Pro (OpenRouter API)         ← maliyet: token başına
BEST   → GPT-5.5 (OpenRouter API)             ← maliyet: token başına
---
CLI_FAST   → OpenCode (DeepSeek v4 Pro)        ← maliyet: sıfır (subscription)
CLI_MID    → Gemini (Gemini 2.5)               ← maliyet: sıfır (subscription)
CLI_BEST   → Claude (Claude Sonnet/Opus)        ← maliyet: sıfır (subscription)
```

Kullanıcı "subscription mod"u tercih ederse tüm trafik CLI tier'ına gider.

### Örnek `router.py` güncellemesi

```python
from enum import Enum

class Tier(Enum):
    FAST = "fast"
    MID = "mid"
    BEST = "best"
    CLI_FAST = "cli_fast"    # OpenCode — sıfır maliyet
    CLI_MID = "cli_mid"      # Gemini — sıfır maliyet
    CLI_BEST = "cli_best"    # Claude — sıfır maliyet

CLI_BACKENDS = {
    Tier.CLI_FAST: ask_opencode,
    Tier.CLI_MID:  ask_gemini,
    Tier.CLI_BEST: ask_claude,
}
```

### Config eklentisi (`config.example.yaml`)

```yaml
router:
  mode: api          # "api" veya "cli" veya "hybrid"
  cli:
    fast: opencode   # DeepSeek v4 Pro — OpenCode Zen subscription
    mid: gemini      # Gemini 2.5 — Google subscription
    best: claude     # Claude Pro — Anthropic subscription
  api:
    fast: deepseek/deepseek-v4-flash
    mid: deepseek/deepseek-v4-pro
    best: openai/gpt-5.5
```

---

## CLI Subscription vs API Maliyet Karşılaştırması

| Araç | API modu | Subscription modu |
|------|----------|-------------------|
| Claude | $3-15/M token | Claude Pro $20/ay flat |
| Gemini | $0.075-2.5/M token | Google One $10/ay flat |
| OpenCode | — | OpenCode Zen $10/ay flat |
| Toplam | Kullanıma göre değişken | ~$40/ay sabit |

**Break-even:** Aylık ~3-5M token üzerinde subscription daha ucuz.

---

## Teknik Gereksinimler

```
python3 asyncio      — eş zamanlı CLI çağrıları için
shlex                — güvenli argüman quotelama
script (bsd-compat)  — OpenCode için pseudo-TTY
CLAUDE_CODE_BUBBLEWRAP=1  — root ortamda Claude için
```

Herhangi bir pip paketi gerektirmez — sadece stdlib.

---

## Test Edilen Senaryo

**Soru:** "AI otomasyon sistemi kurarken en kritik 3 teknik karar nedir?"

**Sonuç (PARALLEL mod):**
- Claude: 152 kelime analiz ✓
- OpenCode: 169 kelime teknik perspektif ✓
- Gemini: 276 kelime sentez ✓
- Toplam süre: ~45 saniye
- API maliyeti: **0 TL**

---

## Referanslar

- Çalışan kod: `/root/2026-orchester/terminal_orchester.py`
- Test çıktıları: `/root/2026-orchester/debates/`
- Hermes bilgi notu: `~/.hermes/skills/birkan-claude-parallel/terminal-orchester-v01.md`
