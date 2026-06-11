from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from testhumanizer.core.artifacts import TargetClass


REQUIRED_COLUMNS = {
    "dataset",
    "project",
    "class_name",
    "source_path",
}


def _clean_optional(value: str | None) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    return value


def load_targets(targets_file: str | Path) -> List[TargetClass]:
    path = Path(targets_file).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Targets file not found: {path}")

    targets: List[TargetClass] = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError(f"Targets file has no header: {path}")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required target columns in {path}: {sorted(missing)}")

        for row_id, row in enumerate(reader, start=1):
            source_path = Path(row["source_path"]).expanduser()

            target = TargetClass(
                dataset=row["dataset"].strip(),
                project=row["project"].strip(),
                class_name=row["class_name"].strip(),
                bug_id=_clean_optional(row.get("bug_id")),
                source_path=source_path,
                classpath=_clean_optional(row.get("classpath")),
                test_class_fqdn=_clean_optional(row.get("test_class_fqdn")),
                class_files_dir=_clean_optional(row.get("class_files_dir")),
                source_files_dir=_clean_optional(row.get("source_files_dir")),
            )

            targets.append(target)

    return targets
