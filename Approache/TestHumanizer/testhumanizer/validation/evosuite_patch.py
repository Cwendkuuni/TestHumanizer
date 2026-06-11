from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Optional, Tuple


SEPARATE_CLASSLOADER_RE = re.compile(r"separateClassLoader\s*=\s*true")


def patch_separate_classloader_in_text(java_code: str) -> tuple[str, bool]:
    patched, count = SEPARATE_CLASSLOADER_RE.subn(
        "separateClassLoader = false",
        java_code,
    )
    return patched, count > 0


def create_coverage_friendly_test_copy(
    test_file: str | Path,
    scaffolding_file: str | Path | None,
    output_dir: str | Path,
) -> Tuple[Path, Optional[Path], bool]:
    """
    Copy EvoSuite test files to output_dir while changing:
      separateClassLoader = true
    into:
      separateClassLoader = false

    The original files are never modified.
    """
    test_file = Path(test_file).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    copied_test = output_dir / test_file.name
    original_code = test_file.read_text(encoding="utf-8", errors="replace")
    patched_code, patched = patch_separate_classloader_in_text(original_code)
    copied_test.write_text(patched_code, encoding="utf-8")

    copied_scaffolding: Optional[Path] = None
    if scaffolding_file:
        scaffolding_path = Path(scaffolding_file).expanduser().resolve()
        if scaffolding_path.exists():
            copied_scaffolding = output_dir / scaffolding_path.name
            shutil.copy2(scaffolding_path, copied_scaffolding)

    return copied_test, copied_scaffolding, patched
