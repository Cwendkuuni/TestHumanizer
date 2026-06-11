


###################################################################################################################WITH SYSTEM STATISTIQUES LOC, TOKENS, ETC.
# import os
# import csv
# import json
# import re
# from collections import defaultdict
# from tree_sitter import Language, Parser
# import tree_sitter_java as tsjava  # Utilisation de la nouvelle syntaxe
# import tiktoken  # Pour le comptage des tokens


# # Initialisation correcte de Tree-sitter pour Java
# JAVA_LANGUAGE = Language(tsjava.language())
# parser = Parser(JAVA_LANGUAGE)




import os
import csv
import json
import re
from collections import defaultdict
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava  # Utilisation de la nouvelle syntaxe
import tiktoken  # Pour le comptage des tokens





# Configuration des chemins
BASE_DIR = "/home/e113/Documents/Humanization-Project/HUMANIZATION/MISTRAL-ONLY/Refactoring-output"
OUTPUT_BASE_DIR = "MISTRAL_ITERATIONS-Processed_Tests"

SYNTAX_CSV_FILE = "A_mistral_syntax_statistics.csv"
ERRORS_CSV_FILE = "A_mistral_syntax_errors.csv"
DETAILED_CSV_FILE = "A_mistral_detailed_statistics.csv"
SUMMARY_CSV_FILE = "A_mistral_final_summary_statistics.csv"
DEFECTS4J_JSON = "Defects4J_complet_enriched.json"
SF110_JSON = "SF110_complet_enriched.json"

# Initialisation correcte de Tree-sitter pour Java
JAVA_LANGUAGE = Language(tsjava.language())
parser = Parser(JAVA_LANGUAGE)


# Initialisation de tiktoken
ENCODING = tiktoken.get_encoding("cl100k_base")

# Fonction pour charger les fichiers JSON
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON {file_path}: {e}")
        return []

# Chargement des données JSON
defects4j_data = load_json(DEFECTS4J_JSON)
sf110_data = load_json(SF110_JSON)

# Fonction pour extraire les blocs de code
def extract_code(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Capture les blocs de code entre ```java et ``` ou simplement ``` et ```
        code_blocks = re.findall(r'```(?:java)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if not code_blocks:
            print(f"Aucun bloc de code trouvé dans: {file_path}")
        else:
            print(f"{len(code_blocks)} blocs de code trouvés dans: {file_path}")
        return code_blocks
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return []

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

        methods, loc_count = extract_methods_and_locs(root_node, code_bytes)
        token_count = count_tokens(java_code)
        print(f"  Detected {len(methods)} methods and {loc_count} LOC.")

        return {
            'test_token_count': token_count,
            'test_loc': loc_count,
            'test_method_count': len(methods)
        }
    except Exception as e:
        print(f"[Error] Erreur lors de l'analyse du code Java: {e}")
        return {
            'test_token_count': 0,
            'test_loc': 0,
            'test_method_count': 0
        }

# Fonction pour vérifier la syntaxe Java avec Tree-sitter et extraire les erreurs
def is_syntax_correct(java_code):
    try:
        tree = parser.parse(bytes(java_code, "utf8"))
        root_node = tree.root_node
        if root_node.has_error:
            # Collecter les positions des erreurs
            errors = []
            collect_errors(root_node, errors)
            return False, errors
        return True, []
    except Exception as e:
        print(f"Erreur lors de l'analyse syntaxique: {e}")
        return False, [str(e)]

# Fonction récursive pour collecter les erreurs dans le parse tree
def collect_errors(node, errors):
    if node.has_error:
        errors.append({
            "type": node.type,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "start_point": node.start_point,
            "end_point": node.end_point
        })
    for child in node.children:
        collect_errors(child, errors)

# Fonction pour obtenir les informations depuis les JSON
def get_test_info(dataset, project, bug_id, class_name):
    if dataset == "Defects4J":
        for entry in defects4j_data:
            if (entry.get("project_name") == project and
                entry.get("bug-id") == bug_id and
                entry.get("class") == class_name):
                return entry
    elif dataset == "SF110":
        for entry in sf110_data:
            if (entry.get("project_name") == project and
                entry.get("class") == class_name):
                return entry
    return None

# Fonction pour traiter les fichiers Defects4J
def process_defects4j(scenario, model, dataset, project, class_name, bug_id, testsuite_dir, test_file, csv_writer, error_writer, detailed_writer, stats, detailed_stats):
    # Pattern de nom de fichier pour Defects4J
    # Exemple : 3-Time-2-UnsupportedDurationField-refactoring-output-iter-1.txt
    regex = r'^(\d+)-([\w-]+)-(\d+)-([\w-]+)-refactoring-output-iter-(\d+)\.txt$'
    match = re.match(regex, test_file)
    if not match:
        print(f"Format de fichier inattendu: {test_file}")
        return
    iteration_number = match.group(5)

    # Chemin complet du fichier
    file_path = os.path.join(testsuite_dir, test_file)

    # Extraction des blocs de code
    code_blocks = extract_code(file_path)
    if not code_blocks:
        return

    java_code = "\n".join(code_blocks)

    # Vérification de la syntaxe et collecte des erreurs
    syntax_ok, errors = is_syntax_correct(java_code)
    if syntax_ok:
        metrics = analyze_java_code(java_code)
    else:
        metrics = {
            'test_token_count': 0,
            'test_loc': 0,
            'test_method_count': 0
        }

    stats['total_tests'] += 1
    if syntax_ok:
        stats['syntax_correct'] += 1
    else:
        stats['syntax_incorrect'] += 1

    # Mise à jour des statistiques détaillées par scénario et dataset
    if scenario not in detailed_stats:
        detailed_stats[scenario] = {}
    if dataset not in detailed_stats[scenario]:
        detailed_stats[scenario][dataset] = {'total_tests': 0, 'syntax_correct': 0, 'syntax_incorrect': 0}
    detailed_stats[scenario][dataset]['total_tests'] += 1
    if syntax_ok:
        detailed_stats[scenario][dataset]['syntax_correct'] += 1
    else:
        detailed_stats[scenario][dataset]['syntax_incorrect'] += 1

    # Écriture dans le CSV des statistiques syntaxiques
    csv_writer.writerow({
        "Scenario": scenario,
        "Model": model,
        "Dataset": dataset,
        "Project": project,
        "Class": class_name,
        "Bug-ID": bug_id,
        "Testsuite": os.path.basename(testsuite_dir),
        "Iteration": iteration_number,
        "Syntax Correct": syntax_ok
    })

    # Si syntaxe incorrecte, enregistrer dans syntax_errors.csv avec les détails des erreurs
    if not syntax_ok:
        for error in errors:
            error_writer.writerow({
                "Scenario": scenario,
                "Model": model,
                "Dataset": dataset,
                "Project": project,
                "Class": class_name,
                "Bug-ID": bug_id,
                "Testsuite": os.path.basename(testsuite_dir),
                "Iteration": iteration_number,
                "Test File": test_file,
                "File Path": file_path,
                "Error Type": error["type"],
                "Start Point": error["start_point"],
                "End Point": error["end_point"]
            })

    # Obtenir les informations du JSON pour le scaffolding
    test_info = get_test_info(dataset, project, bug_id, class_name)
    if not test_info:
        print(f"Aucune correspondance trouvée dans le JSON pour: Project='{project}', Class='{class_name}', Bug-ID='{bug_id}'")
        return

    scaffolding_code = test_info.get("test_scaffolding_code", "")

    # Extraire le nom du testsuite (par exemple, 'testsuite_3')
    testsuite_name = os.path.basename(testsuite_dir)

    # Préparation du répertoire de sortie avec testsuite_name
    # Pour Defects4J, inclure bug_id
    class_dir_path = os.path.join(OUTPUT_BASE_DIR, scenario, model, dataset, project, class_name, bug_id, testsuite_name, f"iter-{iteration_number}")
    os.makedirs(class_dir_path, exist_ok=True)

    # Déduction du nom du fichier Java de test refactoré
    # Exemple : '3-Time-2-UnsupportedDurationField-refactoring-output-iter-1.txt' -> 'UnsupportedDurationField_ESTest.java'
    base_name = test_file.split('-refactoring-output')[0]  # '3-Time-2-UnsupportedDurationField'
    parts = base_name.split('-')
    class_part = parts[-1]  # 'UnsupportedDurationField'
    test_java_name = f"{class_part}_ESTest.java"
    test_java_path = os.path.join(class_dir_path, test_java_name)

    # Déduction du nom du fichier Java de scaffolding
    scaffolding_java_name = f"{class_part}_ESTest_scaffolding.java"
    scaffolding_java_path = os.path.join(class_dir_path, scaffolding_java_name)

    # Enregistrement du code Java de test refactoré
    try:
        with open(test_java_path, 'w', encoding='utf-8') as f:
            f.write(java_code)
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {test_java_path}: {e}")

    # Enregistrement du fichier de scaffolding
    try:
        with open(scaffolding_java_path, 'w', encoding='utf-8') as f:
            f.write(scaffolding_code)
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {scaffolding_java_path}: {e}")

# Fonction pour traiter les fichiers SF110
def process_sf110(scenario, model, dataset, project, class_name, testsuite_dir, test_file, csv_writer, error_writer, detailed_writer, stats, detailed_stats):
    # Pattern de nom de fichier pour SF110
    # Exemple : 3-100_jgaap-jgaapGUI-refactoring-output-iter-1.txt
    regex = r'^(\d+)-[\w_-]+-[\w_-]+-refactoring-output-iter-(\d+)\.txt$'
    match = re.match(regex, test_file)
    if not match:
        print(f"Format de fichier inattendu: {test_file}")
        return
    iteration_number = match.group(2)

    # Chemin complet du fichier
    file_path = os.path.join(testsuite_dir, test_file)

    # Extraction des blocs de code
    code_blocks = extract_code(file_path)
    if not code_blocks:
        return

    java_code = "\n".join(code_blocks)

    # Vérification de la syntaxe et collecte des erreurs
    syntax_ok, errors = is_syntax_correct(java_code)
    if syntax_ok:
        metrics = analyze_java_code(java_code)
    else:
        metrics = {
            'test_token_count': 0,
            'test_loc': 0,
            'test_method_count': 0
        }

    stats['total_tests'] += 1
    if syntax_ok:
        stats['syntax_correct'] += 1
    else:
        stats['syntax_incorrect'] += 1

    # Mise à jour des statistiques détaillées par scénario et dataset
    if scenario not in detailed_stats:
        detailed_stats[scenario] = {}
    if dataset not in detailed_stats[scenario]:
        detailed_stats[scenario][dataset] = {'total_tests': 0, 'syntax_correct': 0, 'syntax_incorrect': 0}
    detailed_stats[scenario][dataset]['total_tests'] += 1
    if syntax_ok:
        detailed_stats[scenario][dataset]['syntax_correct'] += 1
    else:
        detailed_stats[scenario][dataset]['syntax_incorrect'] += 1

    # Écriture dans le CSV des statistiques syntaxiques
    csv_writer.writerow({
        "Scenario": scenario,
        "Model": model,
        "Dataset": dataset,
        "Project": project,
        "Class": class_name,
        "Bug-ID": "",  # Pas de bug-id pour SF110
        "Testsuite": os.path.basename(testsuite_dir),
        "Iteration": iteration_number,
        "Syntax Correct": syntax_ok
    })

    # Si syntaxe incorrecte, enregistrer dans syntax_errors.csv avec les détails des erreurs
    if not syntax_ok:
        for error in errors:
            error_writer.writerow({
                "Scenario": scenario,
                "Model": model,
                "Dataset": dataset,
                "Project": project,
                "Class": class_name,
                "Bug-ID": "",  # Pas de bug-id pour SF110
                "Testsuite": os.path.basename(testsuite_dir),
                "Iteration": iteration_number,
                "Test File": test_file,
                "File Path": file_path,
                "Error Type": error["type"],
                "Start Point": error["start_point"],
                "End Point": error["end_point"]
            })

    # Obtenir les informations du JSON pour le scaffolding
    test_info = get_test_info(dataset, project, None, class_name)  # bug_id est None pour SF110
    if not test_info:
        print(f"Aucune correspondance trouvée dans le JSON pour: Project='{project}', Class='{class_name}'")
        return

    scaffolding_code = test_info.get("test_scaffolding_code", "")

    # Extraire le nom du testsuite (par exemple, 'testsuite_3')
    testsuite_name = os.path.basename(testsuite_dir)

    # Préparation du répertoire de sortie avec testsuite_name
    # Pour SF110, omettre bug_id
    class_dir_path = os.path.join(OUTPUT_BASE_DIR, scenario, model, dataset, project, class_name, testsuite_name, f"iter-{iteration_number}")
    os.makedirs(class_dir_path, exist_ok=True)

    # Déduction du nom du fichier Java de test refactoré
    # Exemple : '3-100_jgaap-jgaapGUI-refactoring-output-iter-1.txt' -> 'jgaapGUI_ESTest.java'
    base_name = test_file.split('-refactoring-output')[0]  # '3-100_jgaap-jgaapGUI'
    parts = base_name.split('-')
    class_part = parts[-1]  # 'jgaapGUI'
    test_java_name = f"{class_part}_ESTest.java"
    test_java_path = os.path.join(class_dir_path, test_java_name)

    # Déduction du nom du fichier Java de scaffolding
    scaffolding_java_name = f"{class_part}_ESTest_scaffolding.java"
    scaffolding_java_path = os.path.join(class_dir_path, scaffolding_java_name)

    # Enregistrement du code Java de test refactoré
    try:
        with open(test_java_path, 'w', encoding='utf-8') as f:
            f.write(java_code)
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {test_java_path}: {e}")

    # Enregistrement du fichier de scaffolding
    try:
        with open(scaffolding_java_path, 'w', encoding='utf-8') as f:
            f.write(scaffolding_code)
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {scaffolding_java_path}: {e}")

# Initialisation des statistiques
stats = {
    'total_tests': 0,
    'syntax_correct': 0,
    'syntax_incorrect': 0
}

# Initialisation des statistiques détaillées par scénario et dataset
detailed_stats = {}

# Ouverture des fichiers CSV pour les statistiques
with open(SYNTAX_CSV_FILE, mode='w', newline='', encoding='utf-8') as syntax_csv, \
     open(ERRORS_CSV_FILE, mode='w', newline='', encoding='utf-8') as errors_csv, \
     open(DETAILED_CSV_FILE, mode='w', newline='', encoding='utf-8') as detailed_csv:
    
    # Écriture des en-têtes pour syntax_statistics.csv
    syntax_fieldnames = ["Scenario", "Model", "Dataset", "Project", "Class", "Bug-ID", "Testsuite", "Iteration", "Syntax Correct"]
    syntax_writer = csv.DictWriter(syntax_csv, fieldnames=syntax_fieldnames)
    syntax_writer.writeheader()

    # Écriture des en-têtes pour syntax_errors.csv
    error_fieldnames = ["Scenario", "Model", "Dataset", "Project", "Class", "Bug-ID", "Testsuite", "Iteration", "Test File", "File Path", "Error Type", "Start Point", "End Point"]
    error_writer = csv.DictWriter(errors_csv, fieldnames=error_fieldnames)
    error_writer.writeheader()

    # Écriture des en-têtes pour gpt_mistral_detailed_statistics.csv
    detailed_fieldnames = ["Scenario", "Dataset", "Total Tests", "Syntax Correct", "Syntax Incorrect", "Success Rate (%)"]
    detailed_writer = csv.DictWriter(detailed_csv, fieldnames=detailed_fieldnames)
    detailed_writer.writeheader()

    # Parcours des scénarios
    for scenario in os.listdir(BASE_DIR):
        scenario_path = os.path.join(BASE_DIR, scenario)
        if not os.path.isdir(scenario_path):
            continue
        print(f"Traitement du {scenario}")

        # Parcours des modèles GPT et MISTRAL
        for model in ['GPT', 'MISTRAL']:
            model_path = os.path.join(scenario_path, model)
            if not os.path.isdir(model_path):
                print(f"  Modèle manquant: {model}")
                continue
            print(f"  Traitement du modèle: {model}")

            # Parcours des datasets
            for dataset in ['Defects4J', 'SF110']:
                dataset_path = os.path.join(model_path, dataset)
                if not os.path.isdir(dataset_path):
                    print(f"    Dataset manquant: {dataset}")
                    continue
                print(f"    Traitement du dataset: {dataset}")

                # Parcours des projets
                for project in os.listdir(dataset_path):
                    project_path = os.path.join(dataset_path, project)
                    if not os.path.isdir(project_path):
                        continue
                    print(f"      Traitement du projet: {project}")

                    if dataset == 'Defects4J':
                        # Parcours des classes
                        for class_name in os.listdir(project_path):
                            class_path = os.path.join(project_path, class_name)
                            if not os.path.isdir(class_path):
                                continue
                            print(f"        Traitement de la classe: {class_name}")

                            # Parcours des bug-ids
                            for bug_id in os.listdir(class_path):
                                bug_id_path = os.path.join(class_path, bug_id)
                                if not os.path.isdir(bug_id_path):
                                    continue
                                print(f"          Traitement du bug-id: {bug_id}")

                                # Parcours des testsuites
                                for testsuite in os.listdir(bug_id_path):
                                    testsuite_dir = os.path.join(bug_id_path, testsuite)
                                    if not os.path.isdir(testsuite_dir):
                                        continue
                                    print(f"            Traitement de la testsuite: {testsuite}")

                                    # Parcours des fichiers de tests
                                    for test_file in os.listdir(testsuite_dir):
                                        if not test_file.endswith(".txt"):
                                            continue
                                        print(f"              Traitement du fichier de test: {test_file}")
                                        process_defects4j(
                                            scenario, model, dataset, project, class_name, bug_id,
                                            testsuite_dir, test_file, syntax_writer, error_writer, detailed_writer, stats, detailed_stats
                                        )

                    elif dataset == 'SF110':
                        # Parcours des classes
                        for class_name in os.listdir(project_path):
                            class_path = os.path.join(project_path, class_name)
                            if not os.path.isdir(class_path):
                                continue
                            print(f"        Traitement de la classe: {class_name}")

                            # Parcours des testsuites
                            for testsuite in os.listdir(class_path):
                                testsuite_dir = os.path.join(class_path, testsuite)
                                if not os.path.isdir(testsuite_dir):
                                    continue
                                print(f"          Traitement de la testsuite: {testsuite}")

                                # Parcours des fichiers de tests
                                for test_file in os.listdir(testsuite_dir):
                                    if not test_file.endswith(".txt"):
                                        continue
                                    print(f"              Traitement du fichier de test: {test_file}")
                                    process_sf110(
                                        scenario, model, dataset, project, class_name,
                                        testsuite_dir, test_file, syntax_writer, error_writer, detailed_writer, stats, detailed_stats
                                    )

    # Écriture des statistiques détaillées dans gpt_mistral_detailed_statistics.csv
    for scenario, datasets in detailed_stats.items():
        for dataset, counts in datasets.items():
            total = counts['total_tests']
            correct = counts['syntax_correct']
            incorrect = counts['syntax_incorrect']
            success_rate = (correct / total * 100) if total > 0 else 0.0
            detailed_writer.writerow({
                "Scenario": scenario,
                "Dataset": dataset,
                "Total Tests": total,
                "Syntax Correct": correct,
                "Syntax Incorrect": incorrect,
                "Success Rate (%)": f"{success_rate:.2f}"
            })

# Écriture des statistiques finales dans un fichier CSV
with open(SUMMARY_CSV_FILE, mode='w', newline='', encoding='utf-8') as summary_csv:
    fieldnames = ["Total Tests Analysés", "Syntaxe Correcte", "Syntaxe Incorrecte", "Taux de Réussite (%)"]
    summary_writer = csv.DictWriter(summary_csv, fieldnames=fieldnames)
    summary_writer.writeheader()
    taux_reussite = (stats['syntax_correct'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0.0
    summary_writer.writerow({
        "Total Tests Analysés": stats['total_tests'],
        "Syntaxe Correcte": stats['syntax_correct'],
        "Syntaxe Incorrecte": stats['syntax_incorrect'],
        "Taux de Réussite (%)": f"{taux_reussite:.2f}"
    })

# Affichage des statistiques finales
print("=== Statistiques de Vérification Syntaxique ===")
print(f"Total des tests analysés: {stats['total_tests']}")
print(f"Syntaxe correcte: {stats['syntax_correct']}")
print(f"Syntaxe incorrecte: {stats['syntax_incorrect']}")
print(f"Taux de Réussite: {taux_reussite:.2f}%")
print(f"Statistiques détaillées enregistrées dans {SYNTAX_CSV_FILE}, {ERRORS_CSV_FILE}, {DETAILED_CSV_FILE} et {SUMMARY_CSV_FILE}")