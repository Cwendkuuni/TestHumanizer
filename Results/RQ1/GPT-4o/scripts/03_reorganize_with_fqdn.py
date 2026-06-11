import os
import shutil
import re
import subprocess
from collections import defaultdict
import csv


import os
import shutil
import re
import subprocess
from collections import defaultdict
import csv
from multiprocessing import Pool
from functools import partial

# # Configuration des chemins de base
# BASE_DIR = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/GPT-MISTRAL-1_ITERATION-Processed_Tests-NEW"
# OUTPUT_DIR = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/REORGANIZED-TESTS-NEW"
# SOURCES_DIR_DEFECTS4J = "/home/wendkuuni/EVOSUITE/LLMS-PROJECT/COMPILABILITY-CODECOVERAGE/DEFECTS4J/SOURCES"
# SOURCES_DIR_SF110 = "/home/wendkuuni/EVOSUITE/LLMS-PROJECT/COMPILABILITY-CODECOVERAGE/SF-110/SOURCES"

# # Chemins vers les dépendances
# JUNIT_PATH = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/JUNIT-HAMCREST/junit4.jar"
# HAMCREST_PATH = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/JUNIT-HAMCREST/hamcrest-core.jar"
# EVOSUITE_PATH = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/evosuite-master-1.2.1-SNAPSHOT.jar"
# SLF4J_PATH = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/slf4j-api-1.6.4.jar"
# DEPENDENCY_DIR = "/media/wendkuuni/b5c80e57-7e05-43fe-90db-5c088623d224/FROM-EVOSUITE-LLMS-PROJECT/HUMANIZATION-PROJECT/LLM-REFACTORED-TEST/JARS/dependencies"



# Configuration des chemins de base
BASE_DIR = "/home/e113/Documents/Humanization-Project/HUMANIZATION/MISTRAL-ONLY/MISTRAL_ITERATIONS-Processed_Tests"
OUTPUT_DIR = "/home/e113/Documents/Humanization-Project/HUMANIZATION/MISTRAL-ONLY/REORGANIZED-TESTS-NEW"
SOURCES_DIR_DEFECTS4J = "/home/e113/Documents/Humanization-Project/HUMANIZATION/DEFECTS4J/SOURCES"
SOURCES_DIR_SF110 = "/home/e113/Documents/Humanization-Project/HUMANIZATION/SF-110/SOURCES"

# Chemins vers les dépendances
JUNIT_PATH = "/home/e113/Documents/Humanization-Project/HUMANIZATION/LLM-REFACTORED-TEST/GPT-ONLY-FOR-ICPC/JUNIT-HAMCREST/junit4.jar"
HAMCREST_PATH = "/home/e113/Documents/Humanization-Project/HUMANIZATION/LLM-REFACTORED-TEST/GPT-ONLY-FOR-ICPC/JUNIT-HAMCREST/hamcrest-core.jar"
EVOSUITE_PATH = "/home/e113/Documents/Humanization-Project/HUMANIZATION/LLM-REFACTORED-TEST/GPT-ONLY-FOR-ICPC/evosuite-master-1.2.1-SNAPSHOT.jar"
SLF4J_PATH = "slf4j-api-1.6.4.jar"
DEPENDENCY_DIR = "/home/e113/Documents/Humanization-Project/HUMANIZATION/LLM-REFACTORED-TEST/GPT-ONLY-FOR-ICPC/JARS/dependencies"


# Fichiers de sortie pour les statistiques
DETAILED_STATS_FILE = "Acompilation_stats_detailed.csv"
SUMMARY_STATS_FILE = "Acompilation_stats_summary.csv"
ERROR_TYPES_FILE = "Acompilation_error_types_summary.csv"

# Liste des itérations à traiter
ITERATIONS = ["iter-1", "iter-2", "iter-3"]

# Fonction pour analyser le chemin de package à partir d'un fichier Java
def parse_package_path(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'\s*package\s+([\w\.]+);', line)
                if match:
                    return match.group(1).replace('.', os.sep)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
    return None

# Fonction pour réorganiser les fichiers en maintenant la hiérarchie des scénarios
def reorganize_files():
    for scenario in os.listdir(BASE_DIR):
        scenario_path = os.path.join(BASE_DIR, scenario)
        if not os.path.isdir(scenario_path):
            continue

        for model in os.listdir(scenario_path):
            model_path = os.path.join(scenario_path, model)
            if not os.path.isdir(model_path):
                continue

            for dataset in os.listdir(model_path):
                dataset_path = os.path.join(model_path, dataset)
                if not os.path.isdir(dataset_path):
                    continue

                for project in os.listdir(dataset_path):
                    project_path = os.path.join(dataset_path, project)
                    if not os.path.isdir(project_path):
                        continue

                    for clazz in os.listdir(project_path):
                        clazz_path = os.path.join(project_path, clazz)
                        if not os.path.isdir(clazz_path):
                            continue

                        if dataset == "Defects4J":
                            for bug_id in os.listdir(clazz_path):
                                bug_id_path = os.path.join(clazz_path, bug_id)
                                if not os.path.isdir(bug_id_path):
                                    continue

                                for testsuite in os.listdir(bug_id_path):
                                    testsuite_path = os.path.join(bug_id_path, testsuite)
                                    if not os.path.isdir(testsuite_path):
                                        continue

                                    for iter_dir in ITERATIONS:
                                        iter_path = os.path.join(testsuite_path, iter_dir)
                                        if not os.path.isdir(iter_path):
                                            continue

                                        # Identifier le fichier de test principal pour extraire le chemin du package
                                        main_test_file = None
                                        for java_file in os.listdir(iter_path):
                                            if java_file.endswith("_ESTest.java"):
                                                main_test_file = java_file
                                                break

                                        if main_test_file:
                                            main_test_file_path = os.path.join(iter_path, main_test_file)
                                            package_path = parse_package_path(main_test_file_path)

                                            # Déterminer le répertoire cible
                                            if package_path:
                                                target_dir = os.path.join(
                                                    OUTPUT_DIR, scenario, model, dataset, project, clazz, bug_id, testsuite, iter_dir, package_path
                                                )
                                            else:
                                                target_dir = os.path.join(
                                                    OUTPUT_DIR, scenario, model, dataset, project, clazz, bug_id, testsuite, iter_dir
                                                )

                                            # Créer le répertoire cible s'il n'existe pas
                                            os.makedirs(target_dir, exist_ok=True)

                                            # Copier les fichiers Java
                                            for java_file in os.listdir(iter_path):
                                                if java_file.endswith(".java"):
                                                    src_file = os.path.join(iter_path, java_file)
                                                    try:
                                                        shutil.copy2(src_file, target_dir)
                                                        print(f"Copié {src_file} vers {target_dir}")
                                                    except Exception as e:
                                                        print(f"Erreur lors de la copie de {src_file} vers {target_dir}: {e}")

                        elif dataset == "SF110":
                            for testsuite in os.listdir(clazz_path):
                                testsuite_path = os.path.join(clazz_path, testsuite)
                                if not os.path.isdir(testsuite_path):
                                    continue

                                for iter_dir in ITERATIONS:
                                    iter_path = os.path.join(testsuite_path, iter_dir)
                                    if not os.path.isdir(iter_path):
                                        continue

                                    # Identifier le fichier de test principal pour extraire le chemin du package
                                    main_test_file = None
                                    for java_file in os.listdir(iter_path):
                                        if java_file.endswith("_ESTest.java"):
                                            main_test_file = java_file
                                            break

                                    if main_test_file:
                                        main_test_file_path = os.path.join(iter_path, main_test_file)
                                        package_path = parse_package_path(main_test_file_path)

                                        # Déterminer le répertoire cible
                                        if package_path:
                                            target_dir = os.path.join(
                                                OUTPUT_DIR, scenario, model, dataset, project, clazz, testsuite, iter_dir, package_path
                                            )
                                        else:
                                            target_dir = os.path.join(
                                                OUTPUT_DIR, scenario, model, dataset, project, clazz, testsuite, iter_dir
                                            )

                                        # Créer le répertoire cible s'il n'existe pas
                                        os.makedirs(target_dir, exist_ok=True)

                                        # Copier les fichiers Java
                                        for java_file in os.listdir(iter_path):
                                            if java_file.endswith(".java"):
                                                src_file = os.path.join(iter_path, java_file)
                                                try:
                                                    shutil.copy2(src_file, target_dir)
                                                    print(f"Copié {src_file} vers {target_dir}")
                                                except Exception as e:
                                                    print(f"Erreur lors de la copie de {src_file} vers {target_dir}: {e}")

# Fonction pour compiler un ensemble de fichiers Java et collecter les statistiques
def compile_task(task, sources_dir_defects4j, sources_dir_sf110, junit_path, hamcrest_path, evosuite_path, slf4j_path, dependency_dir):
    dataset, scenario, model, path, java_files, iter_dir = task

    # Déterminer les parties du chemin relatives à OUTPUT_DIR
    rel_path = os.path.relpath(path, OUTPUT_DIR)
    path_parts = rel_path.split(os.sep)

    # Déterminer le Dataset à partir du paramètre, ne pas réassigner
    if dataset == "Defects4J":
        # Structure : Scenario/Model/Defects4J/Project/Class/Bug-ID/testsuite_y/iter-x/package-path
        if len(path_parts) < 8:
            print(f"Chemin inattendu pour Defects4J : {path}")
            return (dataset, scenario, model, path, iter_dir, "Failed", "Chemin inattendu")
        # Unpack path_parts
        # Indices : 0=Scenario, 1=Model, 2=Defects4J, 3=Project, 4=Class, 5=Bug-ID, 6=testsuite_y, 7=iter-x
        project = path_parts[3]
        clazz = path_parts[4]
        bug_id = path_parts[5]
        testsuite = path_parts[6]
        iter_dir = path_parts[7]
        # Source directory pour Defects4J
        source_dir = os.path.join(sources_dir_defects4j, project, clazz)
    elif dataset == "SF110":
        # Structure : Scenario/Model/SF110/Project/Class/testsuite_y/iter-x/package-path
        if len(path_parts) < 7:
            print(f"Chemin inattendu pour SF110 : {path}")
            return (dataset, scenario, model, path, iter_dir, "Failed", "Chemin inattendu")
        # Unpack path_parts
        # Indices : 0=Scenario, 1=Model, 2=SF110, 3=Project, 4=Class, 5=testsuite_y, 6=iter-x
        project = path_parts[3]
        clazz = path_parts[4]
        testsuite = path_parts[5]
        iter_dir = path_parts[6]
        bug_id = "N/A"  # Pas de bug-id pour SF110
        # Source directory pour SF110
        source_dir = os.path.join(sources_dir_sf110, project)
    else:
        return (dataset, scenario, model, path, iter_dir, "Failed", "Dataset non reconnu")

    # Construction du classpath
    classpath = f".:{source_dir}:{junit_path}:{hamcrest_path}:{evosuite_path}:{slf4j_path}:{dependency_dir}/*"

    # Commande de compilation
    compile_command = [
        "javac",
        "-cp",
        classpath,
        *java_files
    ]

    try:
        result = subprocess.run(
            compile_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Compilation réussie
        return (dataset, scenario, model, path, iter_dir, "Success", "None")
    except subprocess.CalledProcessError as e:
        # Compilation échouée
        error_message = e.stderr.decode("utf-8")
        error_lines = error_message.splitlines()
        error_infos = []
        for line in error_lines:
            # Utiliser une expression régulière pour capturer les erreurs, même avec des espaces
            if re.match(r'\s*error:', line, re.IGNORECASE):
                error_infos.append(line.strip())
        if error_infos:
            # Il y a des erreurs réelles
            error_info_str = "; ".join(error_infos)
        else:
            # Aucun message d'erreur réel, probablement des "Note:" ou autres messages
            # Inclure le message d'erreur complet pour diagnostic
            error_info_str = error_message.strip().replace("\n", " ")
        return (dataset, scenario, model, path, iter_dir, "Failed", error_info_str)

# Fonction pour compiler les fichiers Java et collecter les statistiques en parallèle
def compile_files():
    tasks = []
    # Parcourir les répertoires réorganisés et créer des tâches de compilation
    for root, _, files in os.walk(OUTPUT_DIR):
        java_files = [os.path.join(root, f) for f in files if f.endswith(".java")]
        if not java_files:
            continue

        rel_path = os.path.relpath(root, OUTPUT_DIR)
        path_parts = rel_path.split(os.sep)

        # Déterminer le Dataset
        if "Defects4J" in root:
            dataset = "Defects4J"
            if len(path_parts) < 8:
                print(f"Chemin inattendu pour Defects4J : {root}")
                continue
            scenario, model, dataset_check, project, clazz, bug_id, testsuite, iter_dir = path_parts[:8]
            # Vérifier que dataset_check correspond
            if dataset_check != "Defects4J":
                print(f"Incohérence dans le Dataset pour le chemin : {root}")
                continue
        elif "SF110" in root:
            dataset = "SF110"
            if len(path_parts) < 7:
                print(f"Chemin inattendu pour SF110 : {root}")
                continue
            scenario, model, dataset_check, project, clazz, testsuite, iter_dir = path_parts[:7]
            # Vérifier que dataset_check correspond
            if dataset_check != "SF110":
                print(f"Incohérence dans le Dataset pour le chemin : {root}")
                continue
        else:
            continue  # Dataset non reconnu

        # Ajouter la tâche avec l'itération
        tasks.append((dataset, scenario, model, root, java_files, iter_dir))

    if not tasks:
        print("Aucune tâche de compilation trouvée.")
        return

    # Définir une fonction partielle avec les arguments fixes
    compile_func = partial(
        compile_task,
        sources_dir_defects4j=SOURCES_DIR_DEFECTS4J,
        sources_dir_sf110=SOURCES_DIR_SF110,
        junit_path=JUNIT_PATH,
        hamcrest_path=HAMCREST_PATH,
        evosuite_path=EVOSUITE_PATH,
        slf4j_path=SLF4J_PATH,
        dependency_dir=DEPENDENCY_DIR
    )

    # Utiliser un Pool de processus pour paralléliser les compilations
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(compile_func, tasks)

    # Structures pour les statistiques finales
    detailed_stats = []
    summary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"total": 0, "success": 0, "failure": 0})))
    error_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    # Traiter les résultats
    for result in results:
        dataset, scenario, model, path, iter_dir, status, error_info = result
        detailed_stats.append([dataset, scenario, model, path, iter_dir, status, error_info])
        summary[dataset][scenario][model]["total"] += 1
        if status == "Success":
            summary[dataset][scenario][model]["success"] += 1
        else:
            summary[dataset][scenario][model]["failure"] += 1
            error_summary[dataset][scenario][model][error_info] += 1

    # Écriture des statistiques détaillées
    with open(DETAILED_STATS_FILE, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Dataset", "Scenario", "Model", "Path", "Iteration", "Status", "Error_Info"])
        writer.writerows(detailed_stats)

    # Écriture des statistiques de synthèse
    with open(SUMMARY_STATS_FILE, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Dataset", "Scenario", "Model", "Total_Compiled", "Success_Count", "Failure_Count"])
        for dataset, scenarios in summary.items():
            for scenario, models in scenarios.items():
                for model, counts in models.items():
                    writer.writerow([
                        dataset,
                        scenario,
                        model,
                        counts["total"],
                        counts["success"],
                        counts["failure"]
                    ])

    # Écriture du résumé des types d'erreurs
    with open(ERROR_TYPES_FILE, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Dataset", "Scenario", "Model", "Error_Type", "Count"])
        for dataset, scenarios in error_summary.items():
            for scenario, models in scenarios.items():
                for model, errors in models.items():
                    for error_type, count in errors.items():
                        writer.writerow([
                            dataset,
                            scenario,
                            model,
                            error_type,
                            count
                        ])

# Fonction principale
def main():
    print("Réorganisation des fichiers...")
    reorganize_files()
    print("Réorganisation terminée.\n")
    
    print("Compilation des fichiers Java en parallèle...")
    compile_files()
    print("Compilation terminée.")

if __name__ == "__main__":
    main()