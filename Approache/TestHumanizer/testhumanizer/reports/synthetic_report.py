from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rich.console import Console


console = Console()


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as e:
        console.print(f"[yellow]Could not read CSV:[/yellow] {path} ({e})")
        return pd.DataFrame()


def _safe_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _safe_bool_series(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "1": True,
                "yes": True,
                "ok": True,
                "false": False,
                "0": False,
                "no": False,
                "fail": False,
            }
        )
    )


def _first_existing_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class SyntheticReportGenerator:
    def __init__(
        self,
        *,
        output_dir: str | Path,
        config: Dict[str, Any],
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config

        report_config = config.get("reports", {}).get("synthetic", {})
        self.enabled = bool(report_config.get("enabled", True))

        self.reports_dir = self.output_dir / report_config.get(
            "output_dir",
            "07_reports",
        )
        self.figures_dir = self.reports_dir / "figures"

        self.export_png = bool(report_config.get("export_png", True))
        self.export_html = bool(report_config.get("export_html", True))
        self.png_scale = int(report_config.get("png_scale", 3))

    def run(self) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        data = self._load_data()
        summary = self._build_summary(data)

        figures = self._build_figures(data)

        self._save_figures(figures)

        markdown = self._build_markdown_report(summary, data, figures)
        html = self._build_html_report(summary, data, figures)

        _write_text(self.reports_dir / "synthetic_report.md", markdown)
        _write_text(self.reports_dir / "synthetic_report.html", html)
        _write_json(self.reports_dir / "report_summary.json", summary)

        console.print(
            "[bold green]Synthetic report generated.[/bold green] "
            f"{self.reports_dir}"
        )

    def _load_data(self) -> Dict[str, pd.DataFrame]:
        return {
            "targets": _safe_read_csv(
                self.output_dir / "01_targets" / "targets_resolved.csv"
            ),
            "original_validation": self._read_first_existing(
                [
                    self.output_dir
                    / "05_validation"
                    / "original"
                    / "original_validation_metadata.csv",
                    self.output_dir
                    / "05_validation"
                    / "original_validation_metadata.csv",
                    self.output_dir
                    / "05_validation"
                    / "original_suites_validation_metadata.csv",
                ]
            ),
            "summaries": _safe_read_csv(
                self.output_dir
                / "03_summaries"
                / "source_summaries_metadata.csv"
            ),
            "summary_attempts": self._read_jsonl_as_df(
                self.output_dir / "03_summaries" / "summary_attempts.jsonl"
            ),
            "prompts": _safe_read_csv(
                self.output_dir
                / "04_refactorings"
                / "prompts"
                / "refactoring_prompts_metadata.csv"
            ),
            "refactored_validation": self._read_all_csvs(
                self.output_dir / "05_validation" / "refactored"
            ),
            "ctses": self._read_all_csvs(
                self.output_dir / "06_metrics" / "ctses"
            ),
            "embeddings": _safe_read_csv(
                self.output_dir
                / "06_metrics"
                / "embeddings"
                / "embedding_similarity_results.csv"
            ),
            "readability": self._read_all_csvs(
                self.output_dir / "06_metrics" / "readability"
            ),
            "complexity": self._read_all_csvs(
                self.output_dir / "06_metrics" / "complexity"
            ),
            "selection_all": _safe_read_csv(
                self.output_dir
                / "06_metrics"
                / "selection"
                / "candidate_selection_all.csv"
            ),
            "selected_candidates": _safe_read_csv(
                self.output_dir
                / "06_metrics"
                / "selection"
                / "selected_candidates.csv"
            ),
        }

    def _read_first_existing(self, paths: List[Path]) -> pd.DataFrame:
        for path in paths:
            if path.exists():
                return _safe_read_csv(path)
        return pd.DataFrame()

    def _read_all_csvs(self, root: Path) -> pd.DataFrame:
        if not root.exists():
            return pd.DataFrame()

        frames = []
        for path in sorted(root.rglob("*.csv")):
            df = _safe_read_csv(path)
            if not df.empty:
                df["source_csv"] = str(path.relative_to(self.output_dir))
                frames.append(df)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True, sort=False)

    def _read_jsonl_as_df(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()

        rows = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))

        return pd.DataFrame(rows)

    def _build_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        targets = data["targets"]
        prompts = data["prompts"]
        summaries = data["summaries"]
        selected = data["selected_candidates"]
        selection_all = data["selection_all"]

        summary: Dict[str, Any] = {
            "output_dir": str(self.output_dir),
            "num_targets": int(len(targets)) if not targets.empty else 0,
            "num_prompt_rows": int(len(prompts)) if not prompts.empty else 0,
            "num_summary_rows": int(len(summaries)) if not summaries.empty else 0,
            "num_candidate_rows": int(len(selection_all)) if not selection_all.empty else 0,
            "num_selected_candidates": int(len(selected)) if not selected.empty else 0,
        }

        if not prompts.empty:
            if "scenario_id" in prompts.columns:
                summary["scenarios"] = sorted(prompts["scenario_id"].dropna().unique().tolist())
            elif "scenario" in prompts.columns:
                summary["scenarios"] = sorted(prompts["scenario"].dropna().unique().tolist())

            if "model_alias" in prompts.columns:
                summary["models"] = sorted(prompts["model_alias"].dropna().unique().tolist())

            if "prompt_token_count" in prompts.columns:
                tokens = _safe_float_series(prompts["prompt_token_count"])
                summary["prompt_tokens_total"] = float(tokens.sum())
                summary["prompt_tokens_mean"] = float(tokens.mean())
                summary["prompt_tokens_max"] = float(tokens.max())

        if not selected.empty:
            if "passes_all_thresholds" in selected.columns:
                pass_series = _safe_bool_series(selected["passes_all_thresholds"])
                summary["selected_candidates_threshold_pass"] = int(pass_series.sum())
                summary["selected_candidates_threshold_total"] = int(len(selected))
                summary["selected_candidates_threshold_pass_rate"] = (
                    float(pass_series.sum() / len(selected)) if len(selected) else 0.0
                )

            if "selection_cosine_score" in selected.columns:
                cosine = _safe_float_series(selected["selection_cosine_score"])
                summary["selected_cosine_mean"] = float(cosine.mean())
                summary["selected_cosine_min"] = float(cosine.min())
                summary["selected_cosine_max"] = float(cosine.max())

            if "selection_ctses_score" in selected.columns:
                ctses = _safe_float_series(selected["selection_ctses_score"])
                summary["selected_ctses_mean"] = float(ctses.mean())
                summary["selected_ctses_min"] = float(ctses.min())
                summary["selected_ctses_max"] = float(ctses.max())

        if not summaries.empty:
            if "llm_side_score" in summaries.columns:
                llm_side = _safe_float_series(summaries["llm_side_score"])
                summary["llm_side_mean"] = float(llm_side.mean())
                summary["llm_side_min"] = float(llm_side.min())
                summary["llm_side_max"] = float(llm_side.max())

            if "official_side_score" in summaries.columns:
                official_side = _safe_float_series(summaries["official_side_score"])
                if official_side.notna().any():
                    summary["official_side_mean"] = float(official_side.mean())
                    summary["official_side_min"] = float(official_side.min())
                    summary["official_side_max"] = float(official_side.max())

        return summary

    def _build_figures(self, data: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
        figures: Dict[str, go.Figure] = {}

        selected = data["selected_candidates"]
        prompts = data["prompts"]
        summaries = data["summaries"]
        embeddings = data["embeddings"]
        ctses = data["ctses"]
        complexity = data["complexity"]

        if not selected.empty:
            figures["candidate_selection_scatter"] = self._fig_candidate_selection_scatter(selected)
            figures["selected_cosine_by_scenario"] = self._fig_metric_bar(
                selected,
                value_col="selection_cosine_score",
                title="Selected candidates - OpenAI cosine similarity",
                y_title="OpenAI cosine similarity",
            )
            figures["selected_ctses_by_scenario"] = self._fig_metric_bar(
                selected,
                value_col="selection_ctses_score",
                title="Selected candidates - CTSES score",
                y_title="CTSES score",
            )
            figures["threshold_pass_by_scenario"] = self._fig_threshold_pass(selected)

        if not prompts.empty and "prompt_token_count" in prompts.columns:
            figures["prompt_tokens_by_scenario_model"] = self._fig_prompt_tokens(prompts)

        if not summaries.empty:
            if "llm_side_score" in summaries.columns:
                figures["llm_side_by_class"] = self._fig_summary_side(
                    summaries,
                    value_col="llm_side_score",
                    title="LLM-SIDE score by class",
                )
            if "official_side_score" in summaries.columns:
                official = _safe_float_series(summaries["official_side_score"])
                if official.notna().any():
                    figures["official_side_by_class"] = self._fig_summary_side(
                        summaries,
                        value_col="official_side_score",
                        title="Official SIDE score by class",
                    )

        if not embeddings.empty and "cosine_similarity" in embeddings.columns:
            figures["embedding_similarity_by_model"] = self._fig_embeddings(embeddings)

        if not ctses.empty:
            ctses_value_col = _first_existing_column(
                ctses,
                ["ctses_score", "codebleu_score", "codebleu", "CodeBLEU"],
            )
            if ctses_value_col:
                figures["ctses_all_candidates"] = self._fig_metric_bar(
                    ctses,
                    value_col=ctses_value_col,
                    title="CTSES / CodeBLEU across all candidates",
                    y_title=ctses_value_col,
                )

        if not complexity.empty:
            mi_col = _first_existing_column(
                complexity,
                ["maintainability_index", "mi", "maintainability"],
            )
            if mi_col:
                figures["maintainability_index"] = self._fig_metric_bar(
                    complexity,
                    value_col=mi_col,
                    title="Maintainability index across candidates",
                    y_title="Maintainability index",
                )

        return figures

    def _fig_candidate_selection_scatter(self, df: pd.DataFrame) -> go.Figure:
        plot_df = df.copy()
        plot_df["selection_cosine_score"] = _safe_float_series(
            plot_df["selection_cosine_score"]
        )
        plot_df["selection_ctses_score"] = _safe_float_series(
            plot_df["selection_ctses_score"]
        )

        fig = px.scatter(
            plot_df,
            x="selection_cosine_score",
            y="selection_ctses_score",
            color="scenario" if "scenario" in plot_df.columns else None,
            symbol="model_alias" if "model_alias" in plot_df.columns else None,
            hover_data=[
                col
                for col in [
                    "class_name",
                    "testsuite_id",
                    "scenario",
                    "model_alias",
                    "iteration",
                    "passes_all_thresholds",
                    "selection_reason",
                ]
                if col in plot_df.columns
            ],
            title="Selected candidates: cosine similarity vs CTSES",
        )

        fig.add_vline(x=0.80, line_dash="dash")
        fig.add_hline(y=0.50, line_dash="dash")
        fig.update_layout(
            xaxis_title="OpenAI cosine similarity",
            yaxis_title="CTSES score",
            template="plotly_white",
        )
        return fig

    def _fig_metric_bar(
        self,
        df: pd.DataFrame,
        *,
        value_col: str,
        title: str,
        y_title: str,
    ) -> go.Figure:
        plot_df = df.copy()
        plot_df[value_col] = _safe_float_series(plot_df[value_col])

        x_col = "scenario" if "scenario" in plot_df.columns else "scenario_id"
        color_col = "model_alias" if "model_alias" in plot_df.columns else None

        if x_col not in plot_df.columns:
            plot_df["group"] = "all"
            x_col = "group"

        fig = px.bar(
            plot_df,
            x=x_col,
            y=value_col,
            color=color_col,
            barmode="group",
            facet_col="class_name" if "class_name" in plot_df.columns else None,
            hover_data=[
                col
                for col in ["class_name", "testsuite_id", "iteration", "selection_reason"]
                if col in plot_df.columns
            ],
            title=title,
        )
        fig.update_layout(yaxis_title=y_title, template="plotly_white")
        return fig

    def _fig_threshold_pass(self, df: pd.DataFrame) -> go.Figure:
        plot_df = df.copy()
        plot_df["passes_all_thresholds_bool"] = _safe_bool_series(
            plot_df["passes_all_thresholds"]
        )

        group_cols = [col for col in ["scenario", "model_alias"] if col in plot_df.columns]

        if group_cols:
            grouped = (
                plot_df.groupby(group_cols)["passes_all_thresholds_bool"]
                .mean()
                .reset_index()
            )
            grouped["pass_rate_percent"] = grouped["passes_all_thresholds_bool"] * 100
        else:
            grouped = pd.DataFrame(
                {
                    "group": ["all"],
                    "pass_rate_percent": [plot_df["passes_all_thresholds_bool"].mean() * 100],
                }
            )
            group_cols = ["group"]

        fig = px.bar(
            grouped,
            x=group_cols[0],
            y="pass_rate_percent",
            color=group_cols[1] if len(group_cols) > 1 else None,
            barmode="group",
            title="Threshold pass rate by scenario/model",
        )
        fig.update_layout(
            yaxis_title="Pass rate (%)",
            template="plotly_white",
        )
        return fig

    def _fig_prompt_tokens(self, df: pd.DataFrame) -> go.Figure:
        plot_df = df.copy()
        plot_df["prompt_token_count"] = _safe_float_series(plot_df["prompt_token_count"])

        fig = px.bar(
            plot_df,
            x="scenario_id" if "scenario_id" in plot_df.columns else "scenario",
            y="prompt_token_count",
            color="model_alias" if "model_alias" in plot_df.columns else None,
            facet_col="class_name" if "class_name" in plot_df.columns else None,
            barmode="group",
            title="Prompt token count by scenario/model/class",
            hover_data=[
                col
                for col in ["class_name", "testsuite_id", "summary_used", "summary_source"]
                if col in plot_df.columns
            ],
        )
        fig.update_layout(
            yaxis_title="Prompt tokens",
            template="plotly_white",
        )
        return fig

    def _fig_summary_side(
        self,
        df: pd.DataFrame,
        *,
        value_col: str,
        title: str,
    ) -> go.Figure:
        plot_df = df.copy()
        plot_df[value_col] = _safe_float_series(plot_df[value_col])

        fig = px.bar(
            plot_df,
            x="class_name" if "class_name" in plot_df.columns else "id",
            y=value_col,
            hover_data=[
                col
                for col in [
                    "summary_status",
                    "summary_chars",
                    "llm_side_faithfulness",
                    "llm_side_coverage",
                    "llm_side_hallucination_risk",
                ]
                if col in plot_df.columns
            ],
            title=title,
        )
        fig.update_layout(yaxis_title=value_col, template="plotly_white")
        return fig

    def _fig_embeddings(self, df: pd.DataFrame) -> go.Figure:
        plot_df = df.copy()
        plot_df["cosine_similarity"] = _safe_float_series(plot_df["cosine_similarity"])

        fig = px.bar(
            plot_df,
            x="scenario_id" if "scenario_id" in plot_df.columns else "scenario",
            y="cosine_similarity",
            color="embedding_model_alias" if "embedding_model_alias" in plot_df.columns else None,
            facet_col="class_name" if "class_name" in plot_df.columns else None,
            barmode="group",
            hover_data=[
                col
                for col in ["model_alias", "llm_model_alias", "iteration", "status"]
                if col in plot_df.columns
            ],
            title="Embedding cosine similarity by embedding model",
        )
        fig.update_layout(yaxis_title="Cosine similarity", template="plotly_white")
        return fig

    def _save_figures(self, figures: Dict[str, go.Figure]) -> None:
        for name, fig in figures.items():
            if self.export_html:
                fig.write_html(
                    self.figures_dir / f"{name}.html",
                    include_plotlyjs="cdn",
                    full_html=True,
                )

            if self.export_png:
                try:
                    fig.write_image(
                        self.figures_dir / f"{name}.png",
                        scale=self.png_scale,
                        width=1600,
                        height=900,
                    )
                except Exception as e:
                    console.print(
                        f"[yellow]PNG export skipped for {name}:[/yellow] {e}"
                    )

    def _build_markdown_report(
        self,
        summary: Dict[str, Any],
        data: Dict[str, pd.DataFrame],
        figures: Dict[str, go.Figure],
    ) -> str:
        lines: List[str] = []

        lines.append("# TestHumanizer Synthetic Report")
        lines.append("")
        lines.append("## 1. Experiment overview")
        lines.append("")
        lines.append(f"- Output directory: `{summary.get('output_dir', '')}`")
        lines.append(f"- Number of targets: **{summary.get('num_targets', 0)}**")
        lines.append(f"- Number of prompts: **{summary.get('num_prompt_rows', 0)}**")
        lines.append(f"- Number of generated summaries: **{summary.get('num_summary_rows', 0)}**")
        lines.append(f"- Number of evaluated candidates: **{summary.get('num_candidate_rows', 0)}**")
        lines.append(f"- Number of selected candidates: **{summary.get('num_selected_candidates', 0)}**")
        lines.append("")

        scenarios = summary.get("scenarios", [])
        models = summary.get("models", [])

        if scenarios:
            lines.append(f"- Scenarios: `{', '.join(map(str, scenarios))}`")
        if models:
            lines.append(f"- Models: `{', '.join(map(str, models))}`")

        lines.append("")
        lines.append("## 2. Prompt and token usage")
        lines.append("")

        if "prompt_tokens_total" in summary:
            lines.append(f"- Total prompt tokens: **{summary['prompt_tokens_total']:.0f}**")
            lines.append(f"- Mean prompt tokens: **{summary['prompt_tokens_mean']:.2f}**")
            lines.append(f"- Max prompt tokens: **{summary['prompt_tokens_max']:.0f}**")
        else:
            lines.append("- Prompt token information not available.")

        lines.append("")
        lines.append("## 3. Summarization and SIDE diagnostics")
        lines.append("")

        if "llm_side_mean" in summary:
            lines.append(f"- LLM-SIDE mean: **{summary['llm_side_mean']:.4f}**")
            lines.append(f"- LLM-SIDE min: **{summary['llm_side_min']:.4f}**")
            lines.append(f"- LLM-SIDE max: **{summary['llm_side_max']:.4f}**")
        else:
            lines.append("- LLM-SIDE information not available.")

        if "official_side_mean" in summary:
            lines.append(f"- Official SIDE mean: **{summary['official_side_mean']:.4f}**")
            lines.append(f"- Official SIDE min: **{summary['official_side_min']:.4f}**")
            lines.append(f"- Official SIDE max: **{summary['official_side_max']:.4f}**")

        lines.append("")
        lines.append("## 4. Candidate selection")
        lines.append("")

        if "selected_candidates_threshold_pass_rate" in summary:
            total = summary.get("selected_candidates_threshold_total", 0)
            passed = summary.get("selected_candidates_threshold_pass", 0)
            rate = summary.get("selected_candidates_threshold_pass_rate", 0.0) * 100
            lines.append(f"- Threshold pass: **{passed}/{total}** ({rate:.2f}%)")
        else:
            lines.append("- Candidate selection information not available.")

        if "selected_cosine_mean" in summary:
            lines.append(f"- Selected OpenAI cosine mean: **{summary['selected_cosine_mean']:.4f}**")
            lines.append(f"- Selected OpenAI cosine min: **{summary['selected_cosine_min']:.4f}**")
            lines.append(f"- Selected OpenAI cosine max: **{summary['selected_cosine_max']:.4f}**")

        if "selected_ctses_mean" in summary:
            lines.append(f"- Selected CTSES mean: **{summary['selected_ctses_mean']:.4f}**")
            lines.append(f"- Selected CTSES min: **{summary['selected_ctses_min']:.4f}**")
            lines.append(f"- Selected CTSES max: **{summary['selected_ctses_max']:.4f}**")

        lines.append("")
        lines.append("## 5. Generated figures")
        lines.append("")

        if figures:
            for name in figures:
                lines.append(f"- `{name}`: `figures/{name}.html`")
        else:
            lines.append("- No figures were generated.")

        lines.append("")
        lines.append("## 6. Selected candidates table")
        lines.append("")

        selected = data["selected_candidates"]
        if selected.empty:
            lines.append("Selected candidates table not available.")
        else:
            cols = [
                col
                for col in [
                    "class_name",
                    "testsuite_id",
                    "scenario",
                    "model_alias",
                    "iteration",
                    "selection_cosine_score",
                    "selection_ctses_score",
                    "passes_all_thresholds",
                    "selection_reason",
                ]
                if col in selected.columns
            ]

            if cols:
                lines.append(selected[cols].to_markdown(index=False))
            else:
                lines.append("Selected candidate columns not available.")

        lines.append("")
        return "\n".join(lines)

    def _build_html_report(
        self,
        summary: Dict[str, Any],
        data: Dict[str, pd.DataFrame],
        figures: Dict[str, go.Figure],
    ) -> str:
        figure_html = []

        for name, fig in figures.items():
            figure_html.append(f"<h2>{name}</h2>")
            figure_html.append(
                fig.to_html(
                    include_plotlyjs="cdn",
                    full_html=False,
                )
            )

        selected_html = ""
        selected = data["selected_candidates"]
        if not selected.empty:
            cols = [
                col
                for col in [
                    "class_name",
                    "testsuite_id",
                    "scenario",
                    "model_alias",
                    "iteration",
                    "selection_cosine_score",
                    "selection_ctses_score",
                    "passes_all_thresholds",
                    "selection_reason",
                ]
                if col in selected.columns
            ]
            if cols:
                selected_html = selected[cols].to_html(index=False)

        summary_items = "".join(
            f"<li><strong>{key}</strong>: {value}</li>"
            for key, value in summary.items()
        )

        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TestHumanizer Synthetic Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
      color: #222;
    }}
    h1, h2 {{
      color: #111;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 16px;
      margin-bottom: 32px;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }}
    th {{
      background: #f5f5f5;
    }}
    .summary {{
      background: #fafafa;
      border: 1px solid #eee;
      padding: 16px;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
  <h1>TestHumanizer Synthetic Report</h1>

  <div class="summary">
    <h2>Experiment summary</h2>
    <ul>
      {summary_items}
    </ul>
  </div>

  <h2>Selected candidates</h2>
  {selected_html}

  {"".join(figure_html)}
</body>
</html>
"""
