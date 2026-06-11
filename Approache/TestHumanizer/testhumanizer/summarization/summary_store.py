from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _normalise_bug_id(value: Any) -> str:
    return str(value or "").strip()


def summary_key(
    *,
    dataset: str,
    project: str,
    class_name: str,
    bug_id: str | None = "",
) -> tuple[str, str, str, str]:
    return (
        str(dataset or "").strip(),
        str(project or "").strip(),
        str(class_name or "").strip(),
        _normalise_bug_id(bug_id),
    )


class SummaryStore:
    def __init__(self, summaries_jsonl: str | Path) -> None:
        self.summaries_jsonl = Path(summaries_jsonl).expanduser().resolve()
        self.by_key: Dict[tuple[str, str, str, str], Dict[str, Any]] = {}

        self._load()

    def _load(self) -> None:
        if not self.summaries_jsonl.exists():
            return

        with self.summaries_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                row = json.loads(line)

                key = summary_key(
                    dataset=row.get("dataset", ""),
                    project=row.get("project", ""),
                    class_name=row.get("class_name", ""),
                    bug_id=row.get("bug_id", ""),
                )

                if row.get("selected", True):
                    self.by_key[key] = row

    def get_summary_for(
        self,
        *,
        dataset: str,
        project: str,
        class_name: str,
        bug_id: str | None = "",
    ) -> Optional[Dict[str, Any]]:
        key = summary_key(
            dataset=dataset,
            project=project,
            class_name=class_name,
            bug_id=bug_id,
        )

        return self.by_key.get(key)

    def get_summary_text_for(
        self,
        *,
        dataset: str,
        project: str,
        class_name: str,
        bug_id: str | None = "",
    ) -> str:
        row = self.get_summary_for(
            dataset=dataset,
            project=project,
            class_name=class_name,
            bug_id=bug_id,
        )

        if not row:
            return ""

        return str(row.get("summary_text", "") or "").strip()
