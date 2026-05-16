"""Config loader: reads ~/.kermes/config.yaml with sane defaults."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


DEFAULTS: dict[str, Any] = {
    "provider_url": "https://openrouter.ai/api/v1/chat/completions",
    "tiers": {
        "fast": {"model": "deepseek/deepseek-v4-flash"},
        "mid": {"model": "deepseek/deepseek-v4-pro"},
        "best": {"model": "openai/gpt-5.5"},
    },
    "routing": {
        "simple_threshold": 50,
        "complex_threshold": 500,
    },
    "compression": {
        "enabled": True,
        "threshold": 0.4,
        "target_ratio": 0.15,
        "protect_last_n": 12,
    },
    "cache": {
        "enabled": True,
        "ttl_seconds": 3600,
        "max_entries": 10000,
    },
}


def load(path: str | None = None) -> dict[str, Any]:
    cfg_path = Path(path or os.path.expanduser("~/.kermes/config.yaml"))

    config = dict(DEFAULTS)

    if cfg_path.exists() and yaml:
        with open(cfg_path) as f:
            user_cfg = yaml.safe_load(f) or {}
        config = _deep_merge(config, user_cfg)

    # API key from env fallback
    if "api_key" not in config:
        config["api_key"] = (
            os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("KERMES_API_KEY")
            or os.environ.get("NOVITA_API_KEY")
            or ""
        )

    config["cache_dir"] = os.path.expanduser("~/.kermes/cache")
    return config


def init_config(path: str | None = None) -> None:
    cfg_path = Path(path or os.path.expanduser("~/.kermes/config.yaml"))
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    if cfg_path.exists():
        print(f"Config already exists at {cfg_path}")
        return

    template = Path(__file__).parent.parent / "config.example.yaml"
    if template.exists():
        import shutil
        shutil.copy(template, cfg_path)
    else:
        cfg_path.write_text(_default_config_text())

    print(f"Config created at {cfg_path}")
    print("Edit it to set your API key and model preferences.")


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _default_config_text() -> str:
    return """\
# Kermes Configuration
# Get an OpenRouter key at https://openrouter.ai

provider_url: https://openrouter.ai/api/v1/chat/completions
api_key: sk-or-...

tiers:
  fast:
    model: deepseek/deepseek-v4-flash
  mid:
    model: deepseek/deepseek-v4-pro
  best:
    model: openai/gpt-5.5

routing:
  simple_threshold: 50
  complex_threshold: 500
  force_best_keywords:
    - "architect"
    - "design system"
    - "step by step"
    - "write a full"

compression:
  enabled: true
  threshold: 0.4
  target_ratio: 0.15
  protect_last_n: 12

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 10000

hermes:
  enabled: false
  path: /usr/local/lib/hermes-agent
"""
