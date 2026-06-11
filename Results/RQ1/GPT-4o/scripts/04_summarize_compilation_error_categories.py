import pandas as pd
import re
import os

# Chemin vers le fichier d'entrée
INPUT_CSV = "Acompilation_error_types_summary.csv"

# Chemin vers le fichier de sortie
OUTPUT_CSV = "Acompilation_error_summary-GLOBAL-STATS.csv"

import pandas as pd
import re
import os

# Chemin vers le fichier d'entrée
INPUT_CSV = "Acompilation_error_types_summary.csv"

# Chemin vers le fichier de sortie
OUTPUT_CSV = "Acompilation_error_summary-GLOBAL-STATS.csv"

# Fonction pour extraire le message d'erreur à partir de la colonne Error_Type
def extract_error_message(error_type_str):
    """
    Extrait le message d'erreur pertinent à partir de la chaîne d'erreur complète.

    Exemple :
    Input:
    "/path/to/File.java:461: error: method X is already defined in class Y     public void testMethod() {                 ^ 1 error"

    Output:
    "method X is already defined in class Y"
    """
    # Définir une expression régulière pour capturer le message d'erreur après "error:"
    error_pattern = re.compile(r'error:\s*(.*?)(?:\s*\^|\s*\d+\s+error)', re.IGNORECASE)
    match = error_pattern.search(error_type_str)
    if match:
        # Nettoyer le message en supprimant les espaces inutiles
        return match.group(1).strip()
    else:
        # Si aucun message d'erreur pertinent n'est trouvé, retourner la chaîne brute
        return error_type_str.strip()

# # Définir les catégories d'erreurs avec leurs motifs correspondants
# ERROR_CATEGORIES = [
#     (re.compile(r'cannot find symbol', re.IGNORECASE), 'Cannot Find Symbol'),
#     (re.compile(r'package\s+[\w\.]+\s+does\s+not\s+exist', re.IGNORECASE), 'Package Does Not Exist'),
#     (re.compile(r'method\s+\w+\s+is\s+already\s+defined', re.IGNORECASE), 'Method Redefinition'),
#     (re.compile(r'cannot\s+access\s+\w+', re.IGNORECASE), 'Cannot Access'),
#     (re.compile(r'class\s+\w+\s+is\s+public', re.IGNORECASE), 'Public Class Redefinition'),
#     (re.compile(r'syntax error', re.IGNORECASE), 'Syntax Error'),
#     (re.compile(r'unexpected\s+end\s+of\s+file', re.IGNORECASE), 'Unexpected EOF'),
#     # Ajouter d'autres catégories et motifs selon vos besoins
# ]
# Define the updated error categories with patterns for more detailed classification
ERROR_CATEGORIES = [
    (re.compile(r'cannot find symbol', re.IGNORECASE), 'Cannot Find Symbol'),
    (re.compile(r'package\s+[\w\.]+\s+does\s+not\s+exist', re.IGNORECASE), 'Package Does Not Exist'),
    (re.compile(r'method\s+\w+\s+is\s+already\s+defined', re.IGNORECASE), 'Method Redefinition'),
    (re.compile(r'cannot\s+access\s+\w+', re.IGNORECASE), 'Cannot Access'),
    (re.compile(r'class\s+\w+\s+is\s+public', re.IGNORECASE), 'Public Class Redefinition'),
    (re.compile(r'syntax error', re.IGNORECASE), 'Syntax Error'),
    (re.compile(r'unexpected\s+end\s+of\s+file', re.IGNORECASE), 'Unexpected EOF'),
    (re.compile(r'class\s+\w+\s+is\s+already\s+defined', re.IGNORECASE), 'Class Redefinition'),
    (re.compile(r'unclosed character literal', re.IGNORECASE), 'Unclosed Character Literal'),
    (re.compile(r'incompatible types', re.IGNORECASE), 'Incompatible Types'),
    (re.compile(r'void\s+type\s+not\s+allowed', re.IGNORECASE), 'Void Type Not Allowed'),
    (re.compile(r'missing return statement', re.IGNORECASE), 'Missing Return Statement'),
    (re.compile(r'reached end of file while parsing', re.IGNORECASE), 'End of File Parsing Error'),
    (re.compile(r'unclosed string literal', re.IGNORECASE), 'Unclosed String Literal'),
    (re.compile(r';\s+expected', re.IGNORECASE), 'Semicolon Expected'),
]

def classify_error(error_message):
    """
    Classe le message d'erreur dans une catégorie générale basée sur les motifs définis.
    Si aucun motif ne correspond, retourne 'Other'.
    """
    for pattern, category in ERROR_CATEGORIES:
        if pattern.search(error_message):
            return category
    return 'Other'

def main():
    # Vérifier si le fichier d'entrée existe
    if not os.path.isfile(INPUT_CSV):
        print(f"Erreur : Le fichier {INPUT_CSV} n'existe pas.")
        return

    # Lire le fichier CSV d'entrée
    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {INPUT_CSV} : {e}")
        return

    # Vérifier que les colonnes nécessaires existent
    required_columns = ["Dataset", "Scenario", "Model", "Error_Type", "Count"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Erreur : La colonne '{col}' est manquante dans le fichier CSV.")
            return

    # Extraire les messages d'erreur
    df['Error_Message'] = df['Error_Type'].apply(extract_error_message)

    # Classifier les messages d'erreur en catégories
    df['Error_Category'] = df['Error_Message'].apply(classify_error)

    # Afficher quelques exemples pour vérifier l'extraction et la classification
    print("Exemples de messages d'erreur extraits et classifiés :")
    print(df[['Error_Type', 'Error_Message', 'Error_Category']].head())

    # Agréger les données par Dataset, Scenario, Model et Error_Category
    aggregated_df = df.groupby(['Dataset', 'Scenario', 'Model', 'Error_Category']).agg(
        Total_Errors=('Count', 'sum')
    ).reset_index()

    # Trier les données pour une meilleure lisibilité
    aggregated_df = aggregated_df.sort_values(by=['Dataset', 'Scenario', 'Model', 'Total_Errors'], ascending=[True, True, True, False])

    # Afficher quelques exemples des données agrégées
    print("\nExemples de données agrégées par catégorie d'erreur :")
    print(aggregated_df.head())

    # Exporter les données agrégées vers un nouveau fichier CSV
    try:
        aggregated_df.to_csv(OUTPUT_CSV, index=False)
        print(f"\nStatistiques des erreurs agrégées par catégorie exportées avec succès dans {OUTPUT_CSV}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {OUTPUT_CSV} : {e}")

if __name__ == "__main__":
    main()
