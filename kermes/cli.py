"""Kermes CLI — interactive and single-shot usage."""

from __future__ import annotations
import sys

from . import __version__
from .config import load, init_config
from .router import KermesRouter
from .classifier import Tier


BANNER = r"""
  _  __
 | |/ / ___ _ __ _ __ ___   ___  ___
 | ' / / _ \ '__| '_ ` _ \ / _ \/ __|
 | . \|  __/ |  | | | | | |  __/\__ \
 |_|\_\___|_|  |_| |_| |_|\___||___/

 Token-smart AI agents.
"""


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return 0

    cmd = args[0]

    if cmd == "version":
        print(f"kermes {__version__}")
        return 0

    if cmd == "init":
        init_config()
        return 0

    if cmd == "stats":
        _cmd_stats()
        return 0

    if cmd == "ask":
        return _cmd_ask(args[1:])

    if cmd == "chat":
        return _cmd_chat(args[1:])

    print(f"Unknown command: {cmd}. Run 'kermes --help' for usage.")
    return 1


def _cmd_ask(args: list[str]) -> int:
    force_tier = None
    query_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--tier" and i + 1 < len(args):
            t = args[i + 1].lower()
            force_tier = Tier(t)
            i += 2
        else:
            query_parts.append(args[i])
            i += 1

    query = " ".join(query_parts).strip()
    if not query:
        query = input("Query: ").strip()

    config = load()
    if not config.get("api_key"):
        print("Error: api_key not set. Run 'kermes init' and edit ~/.kermes/config.yaml")
        return 1

    router = KermesRouter(config)

    messages = [{"role": "user", "content": query}]

    if force_tier:
        from .classifier import Classification
        original_classify = __import__("kermes.classifier", fromlist=["classify"]).classify
        def patched_classify(q, cfg=None):
            c = original_classify(q, cfg)
            c.tier = force_tier
            return c
        import kermes.classifier as cls_mod
        cls_mod.classify = patched_classify

    result = router.route(messages)

    print(f"\n[{result.tier.value.upper()} | {result.model} | {'cached' if result.cached else f'{result.tokens_used} tok | ${result.cost_usd:.5f}'}]\n")
    print(result.response)
    return 0


def _cmd_chat(args: list[str]) -> int:
    config = load()
    if not config.get("api_key"):
        print("Error: api_key not set. Run 'kermes init' and edit ~/.kermes/config.yaml")
        return 1

    print(BANNER)
    print(f"  version {__version__} | type 'exit' or Ctrl+C to quit | 'stats' for usage\n")

    router = KermesRouter(config)
    history: list[dict] = []

    try:
        while True:
            try:
                user_input = input("you> ").strip()
            except EOFError:
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                break
            if user_input.lower() == "stats":
                router.print_stats()
                continue

            history.append({"role": "user", "content": user_input})
            result = router.route(history)
            history.append({"role": "assistant", "content": result.response})

            tier_badge = f"[{result.tier.value}]"
            cached_badge = " (cached)" if result.cached else ""
            print(f"\nkermes{cached_badge} {tier_badge}> {result.response}\n")

    except KeyboardInterrupt:
        pass

    router.print_stats()
    return 0


def _cmd_stats() -> None:
    from pathlib import Path
    import json
    cache_path = Path("~/.kermes/cache/response_cache.json").expanduser()
    if cache_path.exists():
        data = json.loads(cache_path.read_text())
        print(f"Cache entries: {len(data)}")
    else:
        print("No cache data found.")


def _print_help() -> None:
    print(f"kermes {__version__} — token-smart AI agent layer\n")
    print("Usage:")
    print("  kermes init               Create config at ~/.kermes/config.yaml")
    print("  kermes ask [--tier TIER] 'your query'")
    print("  kermes chat               Interactive session")
    print("  kermes stats              Show cache stats")
    print("  kermes version\n")
    print("Tiers: fast | mid | best")
    print("Docs:  https://github.com/bbbirkan/2026-kermes")
