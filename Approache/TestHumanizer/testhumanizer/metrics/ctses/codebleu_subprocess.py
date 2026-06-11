from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable


# def _resolve_path(path: str | Path, base_dir: str | Path | None = None) -> Path:
#     p = Path(path).expanduser()
#     if not p.is_absolute() and base_dir is not None:
#         p = Path(base_dir).expanduser().resolve() / p
#     return p.resolve()

def _resolve_path(path: str | Path, base_dir: str | Path | None = None) -> Path:
    p = Path(path).expanduser()

    if not p.is_absolute() and base_dir is not None:
        p = Path(base_dir).expanduser().absolute() / p

    # Important:
    # Do NOT call resolve() here.
    # For virtualenv executables, .venv-codebleu/bin/python can be a symlink
    # to /usr/bin/python3.10. If we resolve it, we lose the virtualenv context,
    # and site-packages from .venv-codebleu are no longer visible.
    return p.absolute()


def _weights_to_string(weights: Iterable[float]) -> str:
    return ",".join(str(float(w)) for w in weights)


def calculate_codebleu_subprocess(
    reference: str,
    prediction: str,
    *,
    codebleu_python: str | Path,
    lang: str = "java",
    weights: Iterable[float] = (0.25, 0.25, 0.25, 0.25),
    project_root: str | Path | None = None,
    timeout_seconds: int = 120,
) -> Dict[str, float | str]:
    """
    Compute CodeBLEU in an isolated Python environment.

    This prevents codebleu/tree-sitter dependency constraints from affecting the
    main TestHumanizer environment.
    """
    codebleu_python_path = _resolve_path(codebleu_python, base_dir=project_root)

    if not codebleu_python_path.exists():
        raise FileNotFoundError(
            f"CodeBLEU Python executable not found: {codebleu_python_path}"
        )

    worker_path = (
        Path(__file__).resolve().parent
        / "workers"
        / "codebleu_worker.py"
    )

    if not worker_path.exists():
        raise FileNotFoundError(f"CodeBLEU worker not found: {worker_path}")

    with tempfile.TemporaryDirectory(prefix="testhumanizer_codebleu_") as tmpdir:
        tmp = Path(tmpdir)
        input_path = tmp / "input.json"
        output_path = tmp / "output.json"

        with input_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "reference": reference,
                    "prediction": prediction,
                },
                f,
                ensure_ascii=False,
            )

        cmd = [
            str(codebleu_python_path),
            str(worker_path),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--lang",
            lang,
            "--weights",
            _weights_to_string(weights),
        ]

        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )

        if not output_path.exists():
            return {
                "codebleu": 0.0,
                "ngram_match_score": 0.0,
                "weighted_ngram_match_score": 0.0,
                "syntax_match_score": 0.0,
                "dataflow_match_score": 0.0,
                "status": "error",
                "error": (
                    "CodeBLEU worker did not produce output. "
                    f"returncode={completed.returncode}; "
                    f"stdout={completed.stdout}; stderr={completed.stderr}"
                ),
            }

        with output_path.open("r", encoding="utf-8") as f:
            result = json.load(f)

        if completed.returncode != 0 and result.get("status") != "error":
            result["status"] = "error"
            result["error"] = (
                f"CodeBLEU worker failed with returncode={completed.returncode}; "
                f"stdout={completed.stdout}; stderr={completed.stderr}"
            )

        return result
