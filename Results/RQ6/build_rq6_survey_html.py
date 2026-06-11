#!/usr/bin/env python3
import random
import csv
import html
from pathlib import Path
from collections import defaultdict

# -----------------------------
# Config
# -----------------------------
BASE_DIR = Path("/home/e113/Documents/Humanization-Project/HUMANIZATION")
HUMAN_EVAL_DIR = BASE_DIR / "NEW-EXPERIMENTS-OUTPUTS" / "HUMAN-EVAL"
TASKS_DIR = HUMAN_EVAL_DIR / "rq6_selected_tasks"

OUTPUT_HTML_ALL   = TASKS_DIR / "rq6_survey.html"
OUTPUT_HTML_GRP_A = TASKS_DIR / "rq6_survey_groupA.html"
OUTPUT_HTML_GRP_B = TASKS_DIR / "rq6_survey_groupB.html"

OUTPUT_CSV_ALL    = TASKS_DIR / "rq6_survey_mapping_html.csv"
OUTPUT_CSV_GRP_A  = TASKS_DIR / "rq6_survey_mapping_groupA.csv"
OUTPUT_CSV_GRP_B  = TASKS_DIR / "rq6_survey_mapping_groupB.csv"

# Pour reproductibilité
random.seed(42)


def read_text_if_exists(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def list_task_dirs():
    """Retourne la liste des sous-dossiers de tâches (01_..., 02_..., etc.)."""
    return sorted(
        [p for p in TASKS_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.name
    )


def parse_readme_metadata(readme_text: str):
    """
    Parse les métadonnées de README.txt pour dataset / projet / classe / Size / LOC.
    On suppose le format produit par building_human_sample_eval.py :
      Dataset : ...
      Project : ...
      Class   : ...
      Size    : <bin> (source_loc=XXX)
    """
    meta = {
        "Dataset": "",
        "Project": "",
        "Class": "",
        "Size": "",
        "LOC": "",
    }
    for line in readme_text.splitlines():
        line = line.strip()
        if line.startswith("Dataset"):
            meta["Dataset"] = line.split(":", 1)[1].strip()
        elif line.startswith("Project"):
            meta["Project"] = line.split(":", 1)[1].strip()
        elif line.startswith("Class"):
            meta["Class"] = line.split(":", 1)[1].strip()
        elif line.startswith("Size"):
            after_colon = line.split(":", 1)[1].strip()
            if "(" in after_colon:
                size_part, loc_part = after_colon.split("(", 1)
                meta["Size"] = size_part.strip()
                loc_part = loc_part.rstrip(")")
                if "=" in loc_part:
                    meta["LOC"] = loc_part.split("=", 1)[1].strip()
            else:
                meta["Size"] = after_colon.strip()
    return meta


def extract_summary_body(summary_txt: str) -> str:
    """
    Dans summary.txt, on enlève l'entête et on garde seulement le bloc
    après la ligne contenant 'Class summary:'.
    """
    lines = summary_txt.splitlines()
    summary_only = []
    in_summary = False
    for line in lines:
        if "Class summary:" in line:
            in_summary = True
            continue
        if in_summary:
            summary_only.append(line)
    return "\n".join(summary_only).strip()


def collect_tasks():
    """
    Charge toutes les tâches (dossiers) et renvoie une liste de dicts :
    {
      "task_id": "01",
      "dir": Path(...),
      "dir_name": "...",
      "meta": {...},
      "source_code": str,
      "evo_code": str,
      "ref_code": str,
      "summary": str (corps seulement),
      "order": "EVO_FIRST" ou "REF_FIRST" (randomisé ici),
      "group": "A" / "B" (assigné ensuite),
    }
    """
    task_dirs = list_task_dirs()
    if not task_dirs:
        raise RuntimeError(f"No task dirs found under {TASKS_DIR}")

    tasks = []
    for idx, task_dir in enumerate(task_dirs, start=1):
        readme_text = read_text_if_exists(task_dir / "README.txt")
        meta = parse_readme_metadata(readme_text)

        source_code = read_text_if_exists(task_dir / "source.java")
        evo_code    = read_text_if_exists(task_dir / "evo.java")
        ref_code    = read_text_if_exists(task_dir / "testhumanizer.java")
        summary_txt = read_text_if_exists(task_dir / "summary.txt")
        summary_body = extract_summary_body(summary_txt)

        # Randomisation A/B : fixée une fois pour toutes
        order = random.choice(["EVO_FIRST", "REF_FIRST"])

        tasks.append(
            {
                "task_id": f"{idx:02d}",
                "dir": task_dir,
                "dir_name": task_dir.name,
                "meta": meta,
                "source_code": source_code,
                "evo_code": evo_code,
                "ref_code": ref_code,
                "summary": summary_body,
                "order": order,
                "group": None,  # rempli plus tard
            }
        )
    return tasks


def assign_groups(tasks):
    """
    Assigne chaque tâche à un groupe A ou B, en répartissant
    par (Dataset, Size) de manière équilibrée.
    """
    cells = defaultdict(list)
    for t in tasks:
        ds = t["meta"]["Dataset"]
        size = t["meta"]["Size"]
        cells[(ds, size)].append(t)

    cell_keys = sorted(cells.keys())

    for i, key in enumerate(cell_keys):
        group_tasks = cells[key]
        random.shuffle(group_tasks)
        n = len(group_tasks)
        if n < 2:
            for t in group_tasks:
                t["group"] = "A"
            continue

        if i < len(cell_keys) // 2:
            a_count = (n + 1) // 2
        else:
            a_count = n // 2

        for idx, t in enumerate(group_tasks):
            t["group"] = "A" if idx < a_count else "B"

    count_A = sum(1 for t in tasks if t["group"] == "A")
    count_B = sum(1 for t in tasks if t["group"] == "B")
    print(f"Group A: {count_A} tasks, Group B: {count_B} tasks.")


def render_html(tasks_subset, out_path: Path, title_suffix: str = ""):
    """
    Génère un HTML pour le sous-ensemble de tâches donné.
    tasks_subset : liste de dicts (tels que retournés par collect_tasks + assign_groups)
    """
    tasks_subset = sorted(tasks_subset, key=lambda t: t["task_id"])

    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang='en'>")
    html_parts.append("<head>")
    html_parts.append("<meta charset='UTF-8'/>")

    if title_suffix:
        full_title = f"RQ6 Developer Study – Test Readability and Trust ({title_suffix})"
    else:
        full_title = "RQ6 Developer Study – Test Readability and Trust"

    html_parts.append(f"<title>{html.escape(full_title)}</title>")

    # CSS + highlight.js (coloration syntaxique)
    html_parts.append("""
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>

<style>
body {
    font-family: Arial, sans-serif;
    font-size: 11pt;
    margin: 2cm;
}
h1, h2, h3 {
    font-family: Arial, sans-serif;
}
.code-box {
    border: 1px solid #aaa;
    background: #f8f8f8;
    padding: 8px;
    margin-bottom: 12px;
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 9pt;
    overflow-x: auto;
}
.code-box pre {
    margin: 0;
}
.summary-box {
    border-left: 3px solid #888;
    padding-left: 8px;
    margin: 8px 0 12px 0;
    font-size: 10pt;
    background: #f5f5f5;
}
.task-block {
    page-break-after: always;
    margin-bottom: 2cm;
}
.meta {
    font-size: 9pt;
    color: #555;
}
.likert-table {
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 16px;
    font-size: 9pt;
}
.likert-table th, .likert-table td {
    border: 1px solid #ccc;
    padding: 4px 6px;
    text-align: center;
}
.likert-table th:first-child,
.likert-table td:first-child {
    text-align: left;
    min-width: 160px;
}
.small-note {
    font-size: 8pt;
    color: #777;
}
.comment-box {            /* ### NEW: style pour la zone de commentaires */
    width: 100%;
    box-sizing: border-box;
    font-size: 9pt;
    font-family: Arial, sans-serif;
}
</style>
    """)

    html_parts.append("</head>")
    html_parts.append("<body>")

    # Page d'intro
    html_parts.append(f"<h1>{html.escape(full_title)}</h1>")
    html_parts.append("""
<p>
This questionnaire compares two test suites for the same production class.
For each task:
</p>
<ul>
  <li>Read the <strong>class summary</strong> and the two anonymous test suites (Version&nbsp;A and Version&nbsp;B).</li>
  <li>Assume both suites target the same production class.</li>
  <li>Rate, on a 1–5 scale, how you perceive (i) readability &amp; clarity of intent,
      (ii) trust in correctness, and (iii) willingness to adopt the suite in a real project.</li>
  <li>You may also provide <strong>optional free-text comments</strong> for each task.</li> <!-- ### NEW -->
</ul>

<p>
<em>Scale:</em> 1 = very low, 3 = neutral, 5 = very high.
</p>

<hr/>
    """)

    # Tâches
    for t in tasks_subset:
        meta = t["meta"]
        task_id = t["task_id"]

        source_html = html.escape(t["source_code"])
        evo_html    = html.escape(t["evo_code"])
        ref_html    = html.escape(t["ref_code"])
        summary_html = html.escape(t["summary"])

        # Ordre A/B fixé
        if t["order"] == "EVO_FIRST":
            versionA_label = "EvoSuite"
            versionB_label = "TestHumanizer"
            versionA_code = evo_html
            versionB_code = ref_html
        else:
            versionA_label = "TestHumanizer"
            versionB_label = "EvoSuite"
            versionA_code = ref_html
            versionB_code = evo_html

        html_parts.append("<div class='task-block'>")
        html_parts.append(f"<h2>Task {task_id}</h2>")

        html_parts.append(
            f"<p class='meta'>Dataset: <strong>{html.escape(meta['Dataset'])}</strong> &mdash; "
            f"Project: <strong>{html.escape(meta['Project'])}</strong> &mdash; "
            f"Class: <strong>{html.escape(meta['Class'])}</strong></p>"
        )

        # Résumé
        if summary_html:
            html_parts.append("<h3>Class summary</h3>")
            html_parts.append(f"<div class='summary-box'>{summary_html}</div>")

        # Version A
        html_parts.append("<h3>Version A</h3>")
        html_parts.append(
            "<div class='code-box'><pre><code class=\"language-java\">"
            + versionA_code +
            "</code></pre></div>"
        )

        # Version B
        html_parts.append("<h3>Version B</h3>")
        html_parts.append(
            "<div class='code-box'><pre><code class=\"language-java\">"
            + versionB_code +
            "</code></pre></div>"
        )

        # Table Likert AVEC boutons radio
        def likert_row(aspect_label, name_prefix):
            tds = []
            for val in range(1, 6):
                tds.append(
                    f'<td><input type="radio" name="{name_prefix}" value="{val}"></td>'
                )
            return (
                f"<tr>"
                f"<td>{html.escape(aspect_label)}</td>"
                + "".join(tds) +
                f"</tr>"
            )

        html_parts.append("<table class='likert-table'>")
        html_parts.append(
            "<tr>"
            "<th>Aspect</th>"
            "<th>1</th><th>2</th><th>3</th><th>4</th><th>5</th>"
            "</tr>"
        )

        # Readability A/B
        html_parts.append(
            likert_row(
                "Readability / clarity of intent (Version A)",
                f"t{task_id}_A_readability",
            )
        )
        html_parts.append(
            likert_row(
                "Readability / clarity of intent (Version B)",
                f"t{task_id}_B_readability",
            )
        )

        # Trust A/B
        html_parts.append(
            likert_row(
                "Trust in correctness (Version A)",
                f"t{task_id}_A_trust",
            )
        )
        html_parts.append(
            likert_row(
                "Trust in correctness (Version B)",
                f"t{task_id}_B_trust",
            )
        )

        # Adoption A/B
        html_parts.append(
            likert_row(
                "Willingness to adopt in a real project (Version A)",
                f"t{task_id}_A_adopt",
            )
        )
        html_parts.append(
            likert_row(
                "Willingness to adopt in a real project (Version B)",
                f"t{task_id}_B_adopt",
            )
        )

        html_parts.append("</table>")
        html_parts.append(
            '<p class="small-note">(You may click directly in the boxes when filling the form digitally, '
            'or circle the chosen value if you print it.)</p>'
        )

        # ### NEW: zone de commentaires libres par tâche
        html_parts.append(f"""
<h4>General comments for this task (optional)</h4>
<textarea name="t{task_id}_comments" rows="4" class="comment-box"></textarea>
""")

        html_parts.append("</div>")  # .task-block

    html_parts.append("</body>")
    html_parts.append("</html>")

    out_path.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"HTML survey written to: {out_path}")


def write_mappings_csv(tasks, out_path: Path, subset_group=None):
    """
    Écrit un CSV de mapping.
    subset_group = None -> toutes les tâches
                   "A"   -> seulement groupe A
                   "B"   -> seulement groupe B
    """
    rows = []
    for t in tasks:
        if subset_group is not None and t["group"] != subset_group:
            continue

        meta = t["meta"]

        if t["order"] == "EVO_FIRST":
            versionA_label = "EvoSuite"
            versionB_label = "TestHumanizer"
        else:
            versionA_label = "TestHumanizer"
            versionB_label = "EvoSuite"

        rows.append(
            {
                "task_id": t["task_id"],
                "dir_name": t["dir_name"],
                "group": t["group"],
                "dataset": meta["Dataset"],
                "project": meta["Project"],
                "class": meta["Class"],
                "size_bin": meta["Size"],
                "loc": meta["LOC"],
                "versionA": versionA_label,
                "versionB": versionB_label,
            }
        )

    with out_path.open("w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(
            f_csv,
            fieldnames=[
                "task_id", "dir_name", "group", "dataset", "project", "class",
                "size_bin", "loc", "versionA", "versionB"
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Mapping CSV written to: {out_path}")


def main():
    # 1) Charger les tâches
    tasks = collect_tasks()

    # 2) Assigner groupes A/B (stratifié)
    assign_groups(tasks)

    tasks_all = tasks
    tasks_A = [t for t in tasks if t["group"] == "A"]
    tasks_B = [t for t in tasks if t["group"] == "B"]

    # 3) Générer les trois HTML
    render_html(tasks_all, OUTPUT_HTML_ALL, title_suffix="All tasks")
    render_html(tasks_A,  OUTPUT_HTML_GRP_A, title_suffix="Group A")
    render_html(tasks_B,  OUTPUT_HTML_GRP_B, title_suffix="Group B")

    # 4) Générer les CSV de mapping
    write_mappings_csv(tasks_all, OUTPUT_CSV_ALL, subset_group=None)
    write_mappings_csv(tasks_A,  OUTPUT_CSV_GRP_A, subset_group="A")
    write_mappings_csv(tasks_B,  OUTPUT_CSV_GRP_B, subset_group="B")


if __name__ == "__main__":
    main()
