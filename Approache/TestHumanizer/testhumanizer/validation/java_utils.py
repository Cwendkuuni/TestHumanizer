from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


PACKAGE_RE = re.compile(r"^\s*package\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;", re.MULTILINE)


def read_text(path: str | Path) -> str:
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1")


def extract_package(java_file: str | Path) -> Optional[str]:
    content = read_text(java_file)
    match = PACKAGE_RE.search(content)
    if not match:
        return None
    return match.group(1)


def infer_java_class_name(java_file: str | Path) -> str:
    return Path(java_file).stem


def infer_fqdn(java_file: str | Path) -> str:
    package = extract_package(java_file)
    class_name = infer_java_class_name(java_file)

    if package:
        return f"{package}.{class_name}"

    return class_name
