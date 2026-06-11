from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codebleu import calc_codebleu


def read_json(path: str | Path):
    p = Path(path).expanduser().resolve()
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--lang", default="java")
    parser.add_argument(
        "--weights",
        default="0.25,0.25,0.25,0.25",
        help="Comma-separated CodeBLEU weights.",
    )

    args = parser.parse_args()

    payload = read_json(args.input)
    reference = payload.get("reference", "")
    prediction = payload.get("prediction", "")

    weights = tuple(float(x.strip()) for x in args.weights.split(",") if x.strip())
    if len(weights) != 4:
        raise ValueError(f"Expected 4 weights, got: {weights}")

    try:
        if not reference.strip() or not prediction.strip():
            result = {
                "codebleu": 0.0,
                "ngram_match_score": 0.0,
                "weighted_ngram_match_score": 0.0,
                "syntax_match_score": 0.0,
                "dataflow_match_score": 0.0,
                "status": "empty_input",
                "error": "",
            }
        else:
            raw = calc_codebleu(
                [reference],
                [prediction],
                lang=args.lang,
                weights=weights,
                tokenizer=None,
            )

            result = {
                "codebleu": float(raw.get("codebleu", 0.0)),
                "ngram_match_score": float(raw.get("ngram_match_score", 0.0)),
                "weighted_ngram_match_score": float(raw.get("weighted_ngram_match_score", 0.0)),
                "syntax_match_score": float(raw.get("syntax_match_score", 0.0)),
                "dataflow_match_score": float(raw.get("dataflow_match_score", 0.0)),
                "status": "ok",
                "error": "",
            }

        write_json(args.output, result)
        return 0

    except Exception as e:
        result = {
            "codebleu": 0.0,
            "ngram_match_score": 0.0,
            "weighted_ngram_match_score": 0.0,
            "syntax_match_score": 0.0,
            "dataflow_match_score": 0.0,
            "status": "error",
            "error": str(e),
        }
        write_json(args.output, result)
        return 1


if __name__ == "__main__":
    sys.exit(main())
