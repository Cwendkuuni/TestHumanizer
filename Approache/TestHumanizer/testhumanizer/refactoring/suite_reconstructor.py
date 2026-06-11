from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional


def ensure_package_dir(base_dir: str | Path, fqdn_path: str | None) -> Path:
    base = Path(base_dir).expanduser().resolve()

    if fqdn_path:
        target_dir = base / fqdn_path
    else:
        target_dir = base

    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def write_refactored_suite_files(
    *,
    refactored_test_code: str,
    test_file_name: str,
    original_scaffolding_file: str | Path | None,
    output_base_dir: str | Path,
    fqdn_path: str | None,
) -> tuple[Path, Optional[Path]]:
    package_dir = ensure_package_dir(output_base_dir, fqdn_path)

    test_output_path = package_dir / test_file_name
    test_output_path.write_text(refactored_test_code, encoding="utf-8")

    scaffolding_output_path: Optional[Path] = None

    if original_scaffolding_file:
        original_scaffolding_path = Path(original_scaffolding_file).expanduser().resolve()

        if original_scaffolding_path.exists():
            scaffolding_output_path = package_dir / original_scaffolding_path.name
            shutil.copy2(original_scaffolding_path, scaffolding_output_path)

    return test_output_path, scaffolding_output_path
