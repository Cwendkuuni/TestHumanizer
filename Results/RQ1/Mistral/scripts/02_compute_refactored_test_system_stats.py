import os
import csv
from collections import defaultdict
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava  # Assurez-vous que tree_sitter_java est correctement installé
import tiktoken  # Pour le comptage des tokens


# Configuration des chemins
OUTPUT_BASE_DIR = "MISTRAL_ITERATIONS-Processed_Tests"  # Répertoire parent contenant GPT et MISTRAL
SYSTEM_STATS_CSV_FILE = "A_mistral_system_statistics.csv"
SYSTEM_SUMMARY_CSV_FILE = "A_mistral_system_summary_statistics.csv"
DETAILED_STATISTICS_CSV_FILE = "AA_mistral_detailed_statistics.csv"  # Nouveau fichier pour les statistiques détaillées

# Initialisation correcte de Tree-sitter pour Java
JAVA_LANGUAGE = Language(tsjava.language())
parser = Parser(JAVA_LANGUAGE)


# Initialisation de tiktoken
ENCODING = tiktoken.get_encoding("cl100k_base")

# Fonction pour compter les tokens
def count_tokens(code):
    tokens = ENCODING.encode(code)
    return len(tokens)

# Fonction pour extraire les méthodes et calculer les LOC
def extract_methods_and_locs(node, code_bytes):
    methods = []
    loc_count = 0
    if node.type == 'method_declaration':
        method_code = code_bytes[node.start_byte:node.end_byte].decode('utf8')
        methods.append(method_code)
        loc_count += len(method_code.splitlines())
        # Ajouter un message de débogage pour la méthode détectée
        print(f"  Méthode détectée: {method_code.splitlines()[0]}... ({len(method_code.splitlines())} LOC)")
    for child in node.children:
        child_methods, child_loc = extract_methods_and_locs(child, code_bytes)
        methods.extend(child_methods)
        loc_count += child_loc
    return methods, loc_count

# Fonction pour analyser un code Java et extraire les métriques
def analyze_java_code(java_code):
    try:
        code_bytes = java_code.encode('utf8')
        tree = parser.parse(code_bytes)
        root_node = tree.root_node

        # Vérifier la syntaxe
        syntax_ok = not root_node.has_error

        methods, loc_count = extract_methods_and_locs(root_node, code_bytes)
        token_count = count_tokens(java_code)
        print(f"  Detected {len(methods)} methods and {loc_count} LOC. Syntax OK: {syntax_ok}")

        return {
            'test_token_count': token_count,
            'test_loc': loc_count,
            'test_method_count': len(methods),
            'syntax_ok': syntax_ok
        }
    except Exception as e:
        print(f"[Error] Erreur lors de l'analyse du code Java: {e}")
        return {
            'test_token_count': 0,
            'test_loc': 0,
            'test_method_count': 0,
            'syntax_ok': False
        }

# Fonction pour générer les statistiques système
def generate_system_statistics(output_dir, system_csv_file, summary_csv_file, detailed_statistics_csv_file):
    summary_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'tokens': [],
        'loc': [],
        'methods': []
    })))

    # Nouvelle structure pour les statistiques détaillées (3 niveaux)
    detailed_summary_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'total_tests': 0,
        'syntax_correct': 0,
        'syntax_incorrect': 0
    })))

    with open(system_csv_file, mode='w', newline='', encoding='utf-8') as system_csv:
        # Écriture des en-têtes pour gpt_mistral_system_statistics.csv
        system_fieldnames = ["Model", "Scenario", "Dataset", "Project", "Bug-ID", "Testsuite", "Iteration", "Class", "Tokens", "LOC", "Methods"]
        system_writer = csv.DictWriter(system_csv, fieldnames=system_fieldnames)
        system_writer.writeheader()

        # Parcourir tous les fichiers Java dans OUTPUT_BASE_DIR
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if not file.endswith(".java"):
                    continue
                if '_scaffolding' in file:
                    continue  # Exclure les fichiers de scaffolding

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, output_dir)
                path_parts = relative_path.split(os.sep)

                try:
                    # Structure attendue pour Defects4J :
                    # Scenario/model/dataset/project/class/bug_id/testsuite_X/iter-Y/Class_ESTest.java
                    # Structure attendue pour SF110 avec testsuite_X :
                    # Scenario/model/dataset/project/class/testsuite_X/iter-Y/Class_ESTest.java
                    # Structure attendue pour SF110 sans testsuite_X :
                    # Scenario/model/dataset/project/class/iter-Y/Class_ESTest.java

                    if len(path_parts) == 9:
                        # Defects4J
                        scenario, model, dataset, project, class_name, bug_id, testsuite, iter_dir, test_java_name = path_parts
                        iteration_number = iter_dir.split('-')[-1]
                        testsuite_name = testsuite
                    elif len(path_parts) == 8:
                        # SF110 avec testsuite_X
                        scenario, model, dataset, project, class_name, testsuite, iter_dir, test_java_name = path_parts
                        bug_id = ""  # Pas de Bug-ID pour SF110
                        iteration_number = iter_dir.split('-')[-1]
                        testsuite_name = testsuite
                    elif len(path_parts) == 7 and path_parts[2] == 'SF110':
                        # SF110 sans testsuite_X
                        scenario, model, dataset, project, class_name, iter_dir, test_java_name = path_parts
                        bug_id = ""  # Pas de Bug-ID pour SF110
                        iteration_number = iter_dir.split('-')[-1]
                        testsuite_name = "unknown_testsuite"  # Nom par défaut
                        print(f"  Attention: testsuite_X manquant pour le fichier: {file_path}. Assignation de 'unknown_testsuite'.")
                    else:
                        print(f"Structure de chemin inattendue pour le fichier: {file_path}")
                        continue

                    # Lire le contenu du fichier Java
                    with open(file_path, 'r', encoding='utf-8') as f:
                        java_code = f.read()

                    # Analyser le code Java pour extraire les métriques
                    metrics = analyze_java_code(java_code)

                    # Mise à jour des statistiques détaillées
                    detailed_summary_stats[model][scenario][dataset]['total_tests'] += 1
                    if metrics['syntax_ok']:
                        detailed_summary_stats[model][scenario][dataset]['syntax_correct'] += 1
                    else:
                        detailed_summary_stats[model][scenario][dataset]['syntax_incorrect'] += 1

                    # Écriture dans le CSV des statistiques système
                    system_writer.writerow({
                        "Model": model,
                        "Scenario": scenario,
                        "Dataset": dataset,
                        "Project": project,
                        "Bug-ID": bug_id,
                        "Testsuite": testsuite_name,
                        "Iteration": iteration_number,
                        "Class": class_name,
                        "Tokens": metrics['test_token_count'],
                        "LOC": metrics['test_loc'],
                        "Methods": metrics['test_method_count']
                    })

                    # Mise à jour des statistiques pour le résumé
                    summary_stats[model][scenario][dataset]['tokens'].append(metrics['test_token_count'])
                    summary_stats[model][scenario][dataset]['loc'].append(metrics['test_loc'])
                    summary_stats[model][scenario][dataset]['methods'].append(metrics['test_method_count'])

                except Exception as e:
                    print(f"Erreur lors de l'extraction des informations pour le fichier {file_path}: {e}")

    # Générer les statistiques système synthétiques
    with open(summary_csv_file, mode='w', newline='', encoding='utf-8') as summary_csv:
        # Écriture des en-têtes pour gpt_mistral_system_summary_statistics.csv
        summary_fieldnames = ["Model", "Scenario", "Dataset", "Max Tokens", "Min Tokens", "Avg Tokens",
                              "Max LOC", "Min LOC", "Avg LOC", "Total LOC",
                              "Avg Methods per Class"]
        summary_writer = csv.DictWriter(summary_csv, fieldnames=summary_fieldnames)
        summary_writer.writeheader()

        for model, scenarios in summary_stats.items():
            for scenario, datasets in scenarios.items():
                for dataset, counts in datasets.items():
                    tokens_list = counts['tokens']
                    loc_list = counts['loc']
                    methods_list = counts['methods']

                    if tokens_list:
                        max_tokens = max(tokens_list)
                        min_tokens = min(tokens_list)
                        avg_tokens = sum(tokens_list) / len(tokens_list)
                    else:
                        max_tokens = min_tokens = avg_tokens = 0

                    if loc_list:
                        max_loc = max(loc_list)
                        min_loc = min(loc_list)
                        avg_loc = sum(loc_list) / len(loc_list)
                        total_loc = sum(loc_list)
                    else:
                        max_loc = min_loc = avg_loc = total_loc = 0

                    if methods_list:
                        avg_methods = sum(methods_list) / len(methods_list)
                    else:
                        avg_methods = 0

                    summary_writer.writerow({
                        "Model": model,
                        "Scenario": scenario,
                        "Dataset": dataset,
                        "Max Tokens": max_tokens,
                        "Min Tokens": min_tokens,
                        "Avg Tokens": f"{avg_tokens:.2f}",
                        "Max LOC": max_loc,
                        "Min LOC": min_loc,
                        "Avg LOC": f"{avg_loc:.2f}",
                        "Total LOC": total_loc,
                        "Avg Methods per Class": f"{avg_methods:.2f}"
                    })

    # Générer le fichier de statistiques détaillées
    with open(detailed_statistics_csv_file, mode='w', newline='', encoding='utf-8') as detailed_csv:
        # Écriture des en-têtes pour gpt_mistral_1_detailed_statistics.csv
        detailed_fieldnames = ["Model", "Scenario", "Dataset", "Total Tests", "Syntax Correct", "Syntax Incorrect", "Success Rate (%)"]
        detailed_writer = csv.DictWriter(detailed_csv, fieldnames=detailed_fieldnames)
        detailed_writer.writeheader()

        for model, scenarios in detailed_summary_stats.items():
            for scenario, datasets in scenarios.items():
                for dataset, counts in datasets.items():
                    total_tests = counts['total_tests']
                    syntax_correct = counts['syntax_correct']
                    syntax_incorrect = counts['syntax_incorrect']
                    success_rate = (syntax_correct / total_tests * 100) if total_tests > 0 else 0.0

                    detailed_writer.writerow({
                        "Model": model,
                        "Scenario": scenario,
                        "Dataset": dataset,
                        "Total Tests": total_tests,
                        "Syntax Correct": syntax_correct,
                        "Syntax Incorrect": syntax_incorrect,
                        "Success Rate (%)": f"{success_rate:.2f}"
                    })

    print(f"Statistiques système générées dans {system_csv_file}, {summary_csv_file}, et {detailed_statistics_csv_file}")

# Générer les statistiques système
generate_system_statistics(OUTPUT_BASE_DIR, SYSTEM_STATS_CSV_FILE, SYSTEM_SUMMARY_CSV_FILE, DETAILED_STATISTICS_CSV_FILE)
