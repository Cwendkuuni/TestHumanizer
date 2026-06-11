from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

from testhumanizer.config.loader import load_config
from testhumanizer.config.overrides import apply_cli_overrides
from testhumanizer.core.pipeline import TestHumanizerPipeline


console = Console()


ALL_SCENARIOS = "tests-only,code-centric,summary-based"


def _set_nested(config: Dict[str, Any], path: list[str], value: Any) -> None:
    current = config

    for key in path[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    current[path[-1]] = value


def _apply_preset_defaults(
    *,
    config: Dict[str, Any],
    preset: str | None,
    models: str | None,
    scenarios: str | None,
    iterations: int | None,
) -> tuple[str | None, str | None, int | None]:
    """
    Presets are intentionally conservative.

    They only fill missing CLI values. Explicit CLI arguments always win.
    """

    if not preset:
        return models, scenarios, iterations

    preset = preset.lower().strip()

    if preset == "ready":
        # Use the YAML as the source of truth.
        return models, scenarios, iterations

    if preset == "fast":
        # Quick sanity run.
        if scenarios is None:
            scenarios = ALL_SCENARIOS
        if iterations is None:
            iterations = 1
        return models, scenarios, iterations

    if preset == "full":
        # Paper-like complete run with 3 attempts/candidates.
        if scenarios is None:
            scenarios = ALL_SCENARIOS
        if iterations is None:
            iterations = 3
        return models, scenarios, iterations

    raise ValueError(
        f"Unsupported preset: {preset}. "
        "Expected one of: ready, fast, full."
    )


def _apply_logging_cli_overrides(
    *,
    config: Dict[str, Any],
    log_level: str | None,
    quiet: bool,
    verbose: bool,
    show_details: bool,
    show_metrics: bool,
) -> Dict[str, Any]:
    config = deepcopy(config)

    if quiet:
        log_level = "quiet"
    elif verbose:
        log_level = "verbose"

    if log_level is not None:
        _set_nested(config, ["logging", "level"], log_level)

    if show_details:
        _set_nested(config, ["logging", "show_per_item_details"], True)

    if show_metrics:
        _set_nested(config, ["logging", "show_metric_details"], True)

    return config


def main() -> None:
    parser = argparse.ArgumentParser(prog="testhumanizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Run the TestHumanizer pipeline.",
    )
    run_parser.add_argument("--config", required=True)

    run_parser.add_argument(
        "--preset",
        choices=["ready", "fast", "full"],
        default=None,
        help=(
            "Optional preset. "
            "ready = YAML only, fast = all scenarios with 1 iteration, "
            "full = all scenarios with 3 iterations. "
            "Explicit CLI options override presets."
        ),
    )
    run_parser.add_argument(
        "--models",
        default=None,
        help="Comma-separated refactoring model aliases to run, e.g. gpt4o or gpt4o,mistral.",
    )
    run_parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Override temperature for selected refactoring models.",
    )
    run_parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Override number of LLM refactoring iterations.",
    )
    run_parser.add_argument(
        "--scenarios",
        default=None,
        help=(
            "Comma-separated scenarios: tests-only,code-centric,summary-based. "
            "Use 'all' to run all scenarios."
        ),
    )
    run_parser.add_argument(
        "--output-dir",
        default=None,
        help="Override experiment.output_dir.",
    )
    run_parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM refactoring execution.",
    )
    run_parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable JaCoCo coverage.",
    )

    run_parser.add_argument(
        "--log-level",
        choices=["quiet", "normal", "verbose"],
        default=None,
        help="Override logging.level from the YAML config.",
    )
    run_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Shortcut for --log-level quiet.",
    )
    run_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Shortcut for --log-level verbose.",
    )
    run_parser.add_argument(
        "--show-details",
        action="store_true",
        help="Show per-item details even if logging.level is normal.",
    )
    run_parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Show detailed metric logs even if logging.level is normal.",
    )

    inspect_parser = subparsers.add_parser(
        "inspect-config",
        help="Load and display a TestHumanizer YAML configuration.",
    )
    inspect_parser.add_argument("--config", required=True)

    args = parser.parse_args()

    if args.command == "inspect-config":
        config = load_config(args.config)
        console.print("[bold green]Config loaded successfully[/bold green]")
        console.print(config)
        return

    if args.command == "run":
        config_path = Path(args.config)
        config = load_config(config_path)

        scenarios = args.scenarios
        if scenarios == "all":
            scenarios = ALL_SCENARIOS

        models, scenarios, iterations = _apply_preset_defaults(
            config=config,
            preset=args.preset,
            models=args.models,
            scenarios=scenarios,
            iterations=args.iterations,
        )

        config = apply_cli_overrides(
            config,
            models=models,
            temperature=args.temperature,
            iterations=iterations,
            scenarios=scenarios,
            no_llm=args.no_llm,
            no_coverage=args.no_coverage,
            output_dir=args.output_dir,
        )

        config = _apply_logging_cli_overrides(
            config=config,
            log_level=args.log_level,
            quiet=args.quiet,
            verbose=args.verbose,
            show_details=args.show_details,
            show_metrics=args.show_metrics,
        )

        pipeline = TestHumanizerPipeline(config=config, config_path=config_path)
        pipeline.run()
        return


if __name__ == "__main__":
    main()


############V1
# from __future__ import annotations

# import argparse
# from pathlib import Path

# from rich.console import Console

# from testhumanizer.config.loader import load_config
# from testhumanizer.config.overrides import apply_cli_overrides
# from testhumanizer.core.pipeline import TestHumanizerPipeline


# console = Console()


# def main() -> None:
#     parser = argparse.ArgumentParser(prog="testhumanizer")
#     subparsers = parser.add_subparsers(dest="command", required=True)

#     run_parser = subparsers.add_parser("run")
#     run_parser.add_argument("--config", required=True)

#     run_parser.add_argument(
#         "--models",
#         default=None,
#         help="Comma-separated refactoring model aliases to run, e.g. gpt4o or gpt4o,mistral.",
#     )
#     run_parser.add_argument(
#         "--temperature",
#         type=float,
#         default=None,
#         help="Override temperature for selected refactoring models.",
#     )
#     run_parser.add_argument(
#         "--iterations",
#         type=int,
#         default=None,
#         help="Override number of LLM refactoring iterations.",
#     )
#     run_parser.add_argument(
#         "--scenarios",
#         default=None,
#         help="Comma-separated scenarios: tests-only,code-centric,summary-based.",
#     )
#     run_parser.add_argument(
#         "--output-dir",
#         default=None,
#         help="Override experiment.output_dir.",
#     )
#     run_parser.add_argument(
#         "--no-llm",
#         action="store_true",
#         help="Disable LLM refactoring execution.",
#     )
#     run_parser.add_argument(
#         "--no-coverage",
#         action="store_true",
#         help="Disable JaCoCo coverage.",
#     )

#     inspect_parser = subparsers.add_parser("inspect-config")
#     inspect_parser.add_argument("--config", required=True)

#     args = parser.parse_args()

#     if args.command == "inspect-config":
#         config = load_config(args.config)
#         console.print("[bold green]Config loaded successfully[/bold green]")
#         console.print(config)

#     elif args.command == "run":
#         config_path = Path(args.config)
#         config = load_config(config_path)

#         config = apply_cli_overrides(
#             config,
#             models=args.models,
#             temperature=args.temperature,
#             iterations=args.iterations,
#             scenarios=args.scenarios,
#             no_llm=args.no_llm,
#             no_coverage=args.no_coverage,
#             output_dir=args.output_dir,
#         )

#         pipeline = TestHumanizerPipeline(config=config, config_path=config_path)
#         pipeline.run()


# if __name__ == "__main__":
#     main()
