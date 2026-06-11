import os
import csv

# Définir le répertoire de base
BASE_DIR = "/home/e113/Documents/Humanization-Project/HUMANIZATION/MISTRAL-ONLY/Refactoring-output"

# Définir les noms de scénarios, modèles et datasets
SCENARIOS = ["Scenario-1", "Scenario-2", "Scenario-3"]
MODELS = ["GPT", "MISTRAL"]
DATASETS = ["Defects4J", "SF110"]

# Définir les itérations attendues
EXPECTED_ITERATIONS = ["iter-1.txt", "iter-2.txt", "iter-3.txt"]

# Fonction pour vérifier les itérations
def check_iterations(files):
    present = set()
    for file in files:
        for iter_num in range(1, 4):
            iter_suffix = f"iter-{iter_num}.txt"
            if iter_suffix in file:
                present.add(iter_num)
    return present

# Préparer le fichier CSV de sortie
output_file = "refactoring_statistics.csv"
with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        "Scenario",
        "Model",
        "Dataset",
        "Project",
        "Class",
        "Bug-ID",
        "Testsuite",
        "Iterations Present",
        "Iterations Missing"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Parcourir chaque scénario
    for scenario in SCENARIOS:
        scenario_path = os.path.join(BASE_DIR, scenario)
        if not os.path.isdir(scenario_path):
            print(f"Scénario manquant: {scenario_path}")
            continue

        # Parcourir chaque modèle
        for model in MODELS:
            model_path = os.path.join(scenario_path, model)
            if not os.path.isdir(model_path):
                print(f"Modèle manquant: {model_path}")
                continue

            # Parcourir chaque dataset
            for dataset in DATASETS:
                dataset_path = os.path.join(model_path, dataset)
                if not os.path.isdir(dataset_path):
                    print(f"Dataset manquant: {dataset_path}")
                    continue

                # Parcourir chaque projet
                for project in os.listdir(dataset_path):
                    project_path = os.path.join(dataset_path, project)
                    if not os.path.isdir(project_path):
                        continue

                    # Définir si le dataset est Defects4J ou SF110
                    if dataset == "Defects4J":
                        # Parcourir chaque classe
                        for class_name in os.listdir(project_path):
                            class_path = os.path.join(project_path, class_name)
                            if not os.path.isdir(class_path):
                                continue

                            # Parcourir chaque bug-id
                            for bug_id in os.listdir(class_path):
                                bug_path = os.path.join(class_path, bug_id)
                                if not os.path.isdir(bug_path):
                                    continue

                                # Parcourir chaque testsuite_x
                                for testsuite in os.listdir(bug_path):
                                    testsuite_path = os.path.join(bug_path, testsuite)
                                    if not os.path.isdir(testsuite_path):
                                        continue

                                    # Lister les fichiers dans la suite de tests
                                    files = os.listdir(testsuite_path)
                                    iterations_present = check_iterations(files)
                                    iterations_missing = set(range(1,4)) - iterations_present

                                    # Écrire dans le CSV
                                    writer.writerow({
                                        "Scenario": scenario,
                                        "Model": model,
                                        "Dataset": dataset,
                                        "Project": project,
                                        "Class": class_name,
                                        "Bug-ID": bug_id,
                                        "Testsuite": testsuite,
                                        "Iterations Present": sorted(list(iterations_present)),
                                        "Iterations Missing": sorted(list(iterations_missing))
                                    })

                    elif dataset == "SF110":
                        # Parcourir chaque classe
                        for class_name in os.listdir(project_path):
                            class_path = os.path.join(project_path, class_name)
                            if not os.path.isdir(class_path):
                                continue

                            # Parcourir chaque testsuite_x
                            for testsuite in os.listdir(class_path):
                                testsuite_path = os.path.join(class_path, testsuite)
                                if not os.path.isdir(testsuite_path):
                                    continue

                                # Lister les fichiers dans la suite de tests
                                files = os.listdir(testsuite_path)
                                iterations_present = check_iterations(files)
                                iterations_missing = set(range(1,4)) - iterations_present

                                # Écrire dans le CSV
                                writer.writerow({
                                    "Scenario": scenario,
                                    "Model": model,
                                    "Dataset": dataset,
                                    "Project": project,
                                    "Class": class_name,
                                    "Bug-ID": "",  # Pas de Bug-ID pour SF110
                                    "Testsuite": testsuite,
                                    "Iterations Present": sorted(list(iterations_present)),
                                    "Iterations Missing": sorted(list(iterations_missing))
                                })

print(f"Statistiques générées dans le fichier {output_file}")
