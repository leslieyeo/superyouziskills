"""TTL JSON 文件缓存。结构: <root>/<kind>/<key>.json"""
from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any, Optional

class Cache:
    def __init__(self, root: Optional[Path] = None) -> None:
        env = os.environ.get("SUPERYOUZI_CACHE")
        self.root = Path(root) if root else (Path(env) if env else Path.home() / "Library" / "Caches" / "superyouzi")

    def _path(self, kind: str, key: str) -> Path:
        for label, value in (("kind", kind), ("key", key)):
            value = str(value)
            if not value or value in (".", "..") or any(
                ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
                for ch in value
            ):
                raise ValueError(f"非法缓存 {label}")
        d = self.root / kind
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{key}.json"
        if self.root.resolve() not in path.resolve().parents:
            raise ValueError("缓存路径越界")
        return path

    def get(self, kind: str, key: str, ttl: int) -> Optional[Any]:
        p = self._path(kind, key)
        if not p.exists():
            return None
        if time.time() - p.stat().st_mtime > ttl:
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, kind: str, key: str, value: Any) -> None:
        path = self._path(kind, key)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)
