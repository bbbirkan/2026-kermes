"""Response cache: avoid paying for the same query twice."""

from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Any


class ResponseCache:
    def __init__(self, cache_dir: str | None = None, ttl: int = 3600, max_entries: int = 10000):
        self.ttl = ttl
        self.max_entries = max_entries
        self._store: dict[str, dict] = {}

        if cache_dir:
            self.path = Path(cache_dir) / "response_cache.json"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._load()

    def get(self, query: str, model: str) -> str | None:
        key = self._key(query, model)
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() - entry["ts"] > self.ttl:
            del self._store[key]
            return None
        return entry["response"]

    def set(self, query: str, model: str, response: str) -> None:
        if len(self._store) >= self.max_entries:
            self._evict()
        key = self._key(query, model)
        self._store[key] = {"response": response, "ts": time.time()}
        self._save()

    def stats(self) -> dict[str, Any]:
        now = time.time()
        live = sum(1 for e in self._store.values() if now - e["ts"] <= self.ttl)
        return {"total_entries": len(self._store), "live_entries": live}

    def _key(self, query: str, model: str) -> str:
        raw = f"{model}||{query.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _evict(self) -> None:
        # Remove oldest 20%
        sorted_keys = sorted(self._store, key=lambda k: self._store[k]["ts"])
        for k in sorted_keys[: len(sorted_keys) // 5]:
            del self._store[k]

    def _load(self) -> None:
        if hasattr(self, "path") and self.path.exists():
            try:
                self._store = json.loads(self.path.read_text())
            except Exception:
                self._store = {}

    def _save(self) -> None:
        if hasattr(self, "path"):
            try:
                self.path.write_text(json.dumps(self._store))
            except Exception:
                pass
