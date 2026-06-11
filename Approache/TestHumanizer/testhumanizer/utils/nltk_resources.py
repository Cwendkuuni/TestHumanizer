from __future__ import annotations

import os
from pathlib import Path

import nltk
from rich.console import Console


console = Console()


NLTK_RESOURCES = {
    "punkt": "tokenizers/punkt",
    "wordnet": "corpora/wordnet",
    "omw-1.4": "corpora/omw-1.4",
}


def configure_nltk_data_dir(nltk_data_dir: str | Path | None = None) -> Path:
    """
    Configure a stable NLTK data directory for TestHumanizer.

    Priority:
    1. user-provided path
    2. NLTK_DATA environment variable
    3. ~/.cache/testhumanizer/nltk_data
    """
    if nltk_data_dir:
        data_dir = Path(nltk_data_dir).expanduser().resolve()
    elif os.getenv("NLTK_DATA"):
        data_dir = Path(os.getenv("NLTK_DATA", "")).expanduser().resolve()
    else:
        data_dir = Path.home() / ".cache" / "testhumanizer" / "nltk_data"

    data_dir.mkdir(parents=True, exist_ok=True)

    if str(data_dir) not in nltk.data.path:
        nltk.data.path.append(str(data_dir))

    return data_dir


def ensure_nltk_resources(
    nltk_data_dir: str | Path | None = None,
    download_if_missing: bool = True,
) -> Path:
    data_dir = configure_nltk_data_dir(nltk_data_dir)

    for package_name, resource_path in NLTK_RESOURCES.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            if not download_if_missing:
                raise RuntimeError(
                    f"Missing NLTK resource: {package_name}. "
                    f"Run nltk.download('{package_name}') or enable download_if_missing."
                )

            console.print(
                f"[yellow]Downloading NLTK resource[/yellow] "
                f"{package_name} -> {data_dir}"
            )

            nltk.download(package_name, download_dir=str(data_dir), quiet=True)

    return data_dir
