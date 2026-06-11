#!/usr/bin/env python3
import os
import random
import csv
from pathlib import Path

# === PARAMÈTRES À ADAPTER SI BESOIN ===

# Dossier où building_human_sample_eval.py a créé les tâches
TASKS_ROOT = Path(
    "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/HUMAN-EVAL/rq6_selected_tasks"
)

# Fichiers de sortie
SURVEY_TEX = TASKS_ROOT / "rq6_survey.tex"
MAPPING_CSV = TASKS_ROOT / "rq6_survey_mapping.csv"

# Optionnel : fixer la seed pour reproductibilité
RANDOM_SEED = 42


# === UTILITAIRES ===

def find_task_dirs(root: Path):
    """Retourne la liste des sous-dossiers de tâches (triés par nom)."""
    dirs = [p for p in root.iterdir() if p.is_dir()]
    return sorted(dirs, key=lambda p: p.name)


def read_file_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# === MAIN ===

def main():
    random.seed(RANDOM_SEED)

    task_dirs = find_task_dirs(TASKS_ROOT)
    if not task_dirs:
        print(f"No task directories found under {TASKS_ROOT}")
        return

    # Préparation du mapping A/B
    mapping_rows = []
    # Contenu LaTeX
    tex_lines = []

    # Preambule LaTeX
    tex_lines.append(r"\documentclass[11pt]{article}")
    tex_lines.append(r"\usepackage[margin=2cm]{geometry}")
    tex_lines.append(r"\usepackage{booktabs}")
    tex_lines.append(r"\usepackage{array}")
    tex_lines.append(r"\usepackage{tabularx}")
    tex_lines.append(r"\usepackage{xcolor}")
    tex_lines.append(r"\usepackage{minted}")  # pour le code Java coloré
    tex_lines.append(r"")
    tex_lines.append(r"\setlength{\parindent}{0pt}")
    tex_lines.append(r"\setlength{\parskip}{0.5em}")
    tex_lines.append(r"")
    tex_lines.append(r"\begin{document}")
    tex_lines.append(r"")
    tex_lines.append(r"\section*{Test Suite Readability and Understandability Survey}")
    tex_lines.append(
        r"""Hello, and thank you for participating in this study.

In each task, you will see:
\begin{itemize}
  \item a short summary (and possibly the source code) of a Java class under test;
  \item two alternative JUnit test suites (\textbf{Test Suite A} and \textbf{Test Suite B}).
\end{itemize}

Your goal is to rate each test suite in terms of:
\begin{enumerate}
  \item readability and clarity of intent,
  \item confidence in its correctness / faithfulness to the described behaviour,
  \item willingness to adopt it in a real project.
\end{enumerate}

Please base your judgement only on the code you see, not on style preferences
unrelated to understandability.

\newpage
"""
    )

    # Parcours des tâches
    for idx, task_dir in enumerate(task_dirs, start=1):
        # On essaie d'extraire dataset / project / class du nom de dossier
        # Par ex. : SF110_100_jgaap_jgaapGUI_small
        # Si ton naming est différent, adapte ce split.
        parts = task_dir.name.split("__")
        # Fallback si on ne trouve pas cette structure
        dataset = "UnknownDataset"
        project = "UnknownProject"
        class_name = "UnknownClass"
        size_bin = "UnknownSize"

        # Ex : "SF110_100_jgaap_jgaapGUI_small"
        # -> ["SF110", "100_jgaap", "jgaapGUI", "small"]
        if len(parts) >= 4:
            dataset = parts[0]
            project = parts[1]
            class_name = parts[2]
            size_bin = parts[3]

        # Lecture des fichiers
        summary_txt = read_file_if_exists(task_dir / "summary.txt").strip()
        source_code = read_file_if_exists(task_dir / "source.java")
        evo_code = read_file_if_exists(task_dir / "evo.java")
        th_code = read_file_if_exists(task_dir / "testhumanizer.java")

        if not evo_code or not th_code:
            print(f"[WARN] Missing evo/testhumanizer code in {task_dir}")
            continue

        # Randomisation A/B
        # 0 => A=EvoSuite, B=TestHumanizer
        # 1 => A=TestHumanizer, B=EvoSuite
        condition = random.randint(0, 1)
        if condition == 0:
            suite_a_label = "EvoSuite"
            suite_b_label = "TestHumanizer"
            suite_a_code = evo_code
            suite_b_code = th_code
        else:
            suite_a_label = "TestHumanizer"
            suite_b_label = "EvoSuite"
            suite_a_code = th_code
            suite_b_code = evo_code

        # Ajout au mapping CSV
        mapping_rows.append(
            {
                "task_id": f"Task_{idx:02d}",
                "task_dir": task_dir.name,
                "dataset": dataset,
                "project": project,
                "class_name": class_name,
                "size_bin": size_bin,
                "suiteA_type": suite_a_label,
                "suiteB_type": suite_b_label,
            }
        )

        # === BLOC LaTeX POUR CETTE TÂCHE ===
        tex_lines.append(r"\section*{Task %d -- %s / %s}" % (idx, dataset, class_name))
        tex_lines.append(
            r"\textbf{Project:} %s \hfill \textbf{Size bin:} %s" % (project, size_bin)
        )
        tex_lines.append("")
        # Résumé de la classe
        if summary_txt:
            tex_lines.append(r"\subsection*{Class Summary}")
            tex_lines.append(r"\small")
            # On échappe juste les backslashes potentiels dans le résumé
            safe_summary = summary_txt.replace("\\", r"\textbackslash{}")
            tex_lines.append(safe_summary)
            tex_lines.append(r"\normalsize")
            tex_lines.append("")

        # Classe de production (optionnel, mais utile)
        if source_code:
            tex_lines.append(r"\subsection*{Class under test}")
            tex_lines.append(r"\begin{minted}[fontsize=\scriptsize,linenos]{java}")
            tex_lines.append(source_code.rstrip())
            tex_lines.append(r"\end{minted}")
            tex_lines.append("")

        # Test Suite A
        tex_lines.append(r"\subsection*{Test Suite A}")
        tex_lines.append(r"\begin{minted}[fontsize=\scriptsize,linenos]{java}")
        tex_lines.append(suite_a_code.rstrip())
        tex_lines.append(r"\end{minted}")
        tex_lines.append("")

        # Test Suite B
        tex_lines.append(r"\subsection*{Test Suite B}")
        tex_lines.append(r"\begin{minted}[fontsize=\scriptsize,linenos]{java}")
        tex_lines.append(suite_b_code.rstrip())
        tex_lines.append(r"\end{minted}")
        tex_lines.append("")

        # Grille Likert
        tex_lines.append(r"\subsection*{Ratings}")
        tex_lines.append(
            r"""Please rate each test suite on the following 5-point Likert scales (1 = very low, 5 = very high)."""
        )
        tex_lines.append("")
        tex_lines.append(r"\begin{tabular}{p{0.45\linewidth}ccccc}")
        tex_lines.append(r"& 1 & 2 & 3 & 4 & 5 \\")
        tex_lines.append(r"\midrule")
        tex_lines.append(r"\multicolumn{6}{l}{\textbf{Test Suite A}} \\")
        tex_lines.append(
            r"Readability and clarity of intent & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(
            r"Confidence in correctness / faithfulness & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(
            r"Willingness to adopt in a real project & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(r"\midrule")
        tex_lines.append(r"\multicolumn{6}{l}{\textbf{Test Suite B}} \\")
        tex_lines.append(
            r"Readability and clarity of intent & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(
            r"Confidence in correctness / faithfulness & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(
            r"Willingness to adopt in a real project & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\"
        )
        tex_lines.append(r"\end{tabular}")
        tex_lines.append("")
        tex_lines.append(r"\vspace{0.5em}")
        tex_lines.append(r"\noindent\textbf{Optional comments:}\\[0.2em]")
        tex_lines.append(r"\fbox{\parbox{\linewidth}{\vspace{4em}}}")
        tex_lines.append("")
        tex_lines.append(r"\newpage")
        tex_lines.append("")

    tex_lines.append(r"\end{document}")

    # Écriture du LaTeX
    SURVEY_TEX.write_text("\n".join(tex_lines), encoding="utf-8")
    print(f"LaTeX survey written to: {SURVEY_TEX}")

    # Écriture du mapping CSV
    with MAPPING_CSV.open("w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(
            f_csv,
            fieldnames=[
                "task_id",
                "task_dir",
                "dataset",
                "project",
                "class_name",
                "size_bin",
                "suiteA_type",
                "suiteB_type",
            ],
        )
        writer.writeheader()
        for row in mapping_rows:
            writer.writerow(row)

    print(f"Mapping CSV written to: {MAPPING_CSV}")


if __name__ == "__main__":
    main()
