from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional


def normalize_path(path: str | Path, base_dir: str | Path | None = None) -> str:
    p = Path(path).expanduser()

    if not p.is_absolute():
        if base_dir is None:
            p = Path.cwd() / p
        else:
            p = Path(base_dir).expanduser().resolve() / p

    # Preserve wildcard classpaths such as lib/*
    if str(p).endswith("*"):
        parent = p.parent.resolve()
        return str(parent / "*")

    return str(p.resolve())


def normalize_classpath_entry(entry: str, base_dir: str | Path | None = None) -> str:
    return normalize_path(entry, base_dir=base_dir)


def normalize_classpath(classpath: Optional[str], base_dir: str | Path | None = None) -> str:
    if not classpath:
        return ""

    parts = [p for p in classpath.split(os.pathsep) if p.strip()]
    return os.pathsep.join(normalize_classpath_entry(p, base_dir=base_dir) for p in parts)


def build_classpath(
    entries: Iterable[str | Path | None],
    base_dir: str | Path | None = None,
) -> str:
    normalized: List[str] = []

    for entry in entries:
        if entry is None:
            continue

        entry_str = str(entry).strip()
        if not entry_str:
            continue

        # If the entry itself is a classpath with ":" entries, normalize each part.
        if os.pathsep in entry_str:
            cp = normalize_classpath(entry_str, base_dir=base_dir)
            if cp:
                normalized.extend(cp.split(os.pathsep))
        else:
            normalized.append(normalize_classpath_entry(entry_str, base_dir=base_dir))

    # Deduplicate while preserving order.
    seen = set()
    result = []
    for item in normalized:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return os.pathsep.join(result)
