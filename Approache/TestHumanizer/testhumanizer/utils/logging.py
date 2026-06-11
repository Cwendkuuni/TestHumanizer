from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.panel import Panel


@dataclass
class LoggingConfig:
    level: str = "normal"
    show_phase_headers: bool = True
    show_per_item_details: bool = False
    show_metric_details: bool = False
    show_warnings: bool = True

    @property
    def quiet(self) -> bool:
        return self.level == "quiet"

    @property
    def normal(self) -> bool:
        return self.level in {"normal", "verbose"}

    @property
    def verbose(self) -> bool:
        return self.level == "verbose"


class THLogger:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.console = Console()
        logging_config = (config or {}).get("logging", {})

        self.config = LoggingConfig(
            level=str(logging_config.get("level", "normal")).lower(),
            show_phase_headers=bool(logging_config.get("show_phase_headers", True)),
            show_per_item_details=bool(logging_config.get("show_per_item_details", False)),
            show_metric_details=bool(logging_config.get("show_metric_details", False)),
            show_warnings=bool(logging_config.get("show_warnings", True)),
        )

    def phase(self, number: str, title: str) -> None:
        if self.config.quiet or not self.config.show_phase_headers:
            return

        self.console.print(
            Panel.fit(
                f"[bold cyan]Phase {number}[/bold cyan]\n{title}",
                border_style="cyan",
            )
        )

    def success(self, message: str) -> None:
        if not self.config.quiet:
            self.console.print(f"[bold green]✓[/bold green] {message}")

    def info(self, message: str) -> None:
        if self.config.normal:
            self.console.print(f"[cyan]•[/cyan] {message}")

    def detail(self, message: str) -> None:
        if self.config.verbose or self.config.show_per_item_details:
            self.console.print(f"[dim]  - {message}[/dim]")

    def metric(self, message: str) -> None:
        if self.config.verbose or self.config.show_metric_details:
            self.console.print(f"[magenta]  metric[/magenta] {message}")

    def warning(self, message: str) -> None:
        if self.config.show_warnings:
            self.console.print(f"[yellow]⚠ {message}[/yellow]")

    def error(self, message: str) -> None:
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def final_success(self, message: str) -> None:
        self.console.print(
            Panel.fit(
                f"[bold green]{message}[/bold green]",
                border_style="green",
            )
        )
