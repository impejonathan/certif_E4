
# Projet de Transfert INSEE vers Data Lake

## Description
Ce projet permet d'automatiser le téléchargement des données NAF (Nomenclature d'Activités Française) depuis le site de l'[INSEE](https://www.insee.fr) et leur stockage dans Azure Data Lake. Le script récupère un fichier XLS contenant les codes NAF et le transfère automatiquement vers un container Azure Data Lake spécifié.

## Prérequis
- Python 3.x
- Compte Azure avec un Data Lake Storage configuré
- Accès aux données INSEE

## Installation
1. Cloner le repository
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration
1. Créer un fichier `.env` à la racine du projet avec les informations suivantes :
```env
# Storage Configuration
STORAGE_ACCOUNT_NAME=VOTRE_STORAGE_ACCOUNT
STORAGE_ACCOUNT_KEY=VOTRE_STORAGE_KEY
CONTAINER_NAME=VOTRE_CONTAINER

# INSEE Configuration
INSEE_URL=https://www.insee.fr/fr/statistiques/fichier/2120875/int_courts_naf_rev_2.xls
```

## Structure du Projet
```
fichier_plat_to_DL -- Source 3/
├── NAF_to_DL.py
├── .env
├── requirements.txt
└── data/
    └── (fichiers téléchargés temporairement)
```

## Fonctionnalités
- Téléchargement automatique du fichier NAF depuis l'INSEE
- Validation des variables d'environnement
- Gestion des logs (fichier et console)
- Upload automatique vers Azure Data Lake
- Gestion des erreurs et exceptions
- Nommage des fichiers avec horodatage

## Utilisation
Pour exécuter le script :
```bash
python NAF_to_DL.py
```

## Logs
Les logs sont générés dans :
- Console (sortie standard)
- Fichier `insee_to_datalake.log`

## Architecture du Code
- `InseeToDataLake` : Classe principale gérant les opérations
  - `__init__` : Initialisation et validation des configurations
  - `download_insee_file` : Téléchargement du fichier INSEE
  - `upload_to_datalake` : Transfert vers Azure Data Lake
  - `_validate_env_variables` : Validation des variables d'environnement
  - `_initialize_datalake_client` : Initialisation du client Azure

## Stockage dans Azure Data Lake
Les fichiers sont stockés dans le chemin :
```
data_NAF/naf_rev2_YYYYMMDD.xls
```

## Gestion des Erreurs
- Validation des variables d'environnement
- Gestion des erreurs de téléchargement
- Gestion des erreurs d'upload
- Logging complet des opérations et erreurs

## Support
Pour toute question ou problème, veuillez créer une issue dans le repository.

## Notes
- Les fichiers sont automatiquement horodatés
- Les fichiers existants dans le Data Lake sont écrasés (mode overwrite)

