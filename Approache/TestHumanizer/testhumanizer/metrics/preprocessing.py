from __future__ import annotations

import re


def preprocess_java_code(code: str, *, remove_comments: bool = False) -> str:
    """
    Preprocess Java code before metric computation.

    Default behavior follows the CTSES script:
    - keep imports
    - remove empty lines
    - trim leading/trailing spaces

    Optionally remove comments for embedding-based metrics later.
    """
    if not code:
        return ""

    processed = code

    if remove_comments:
        processed = re.sub(r"//.*", "", processed)
        processed = re.sub(r"/\*.*?\*/", "", processed, flags=re.DOTALL)

    processed = "\n".join(
        line.strip()
        for line in processed.splitlines()
        if line.strip()
    )

    return processed.strip()
