
# API to Data Lake - Bornes IRVE Hauts-de-France

## Description
Ce projet permet d'automatiser le transfert des données des bornes de recharge pour véhicules électriques (IRVE) de la région Hauts-de-France depuis l'API OpenData Réseaux Énergies vers Azure Data Lake Storage. Le script récupère quotidiennement les données au format CSV et les stocke dans une architecture organisée dans le Data Lake.

## Prérequis
- Python 3.x
- Compte Azure avec un Data Lake Storage Gen2
- Fichier `.env` configuré avec les credentials Azure

## Installation

1. Cloner le repository
```bash
git clone [URL_DU_REPO]
cd API_to_DL
```

2. Installer les dépendances
```bash
pip install -r requirements.txt
```

3. Configurer le fichier `.env`
```env
STORAGE_ACCOUNT_NAME=votre_storage_account
STORAGE_ACCOUNT_KEY=votre_storage_key
CONTAINER_NAME_bronze-data=votre_container
```

## Structure du Projet
```
API_to_DL/
├── API_to_DL.py
├── .env
├── requirements.txt
├── data/
└── README.md
```

## Fonctionnalités
- Téléchargement automatique des données IRVE depuis l'API OpenData
- Stockage local temporaire dans le dossier `data/`
- Upload automatique vers Azure Data Lake avec structure hiérarchique par date
- Système de logging complet pour le suivi des opérations
- Gestion des erreurs et validation des variables d'environnement

## Source des Données
- Portail : [OpenData Réseaux Énergies](https://opendata.reseaux-energies.fr/)
- Dataset : [Bornes IRVE Hauts-de-France](https://odre.opendatasoft.com/explore/dataset/bornes-irve/information/?flg=fr-fr&disjunctive.region&disjunctive.departement)

## Utilisation

1. Exécution du script
```bash
python API_to_DL.py
```

2. Structure des données dans le Data Lake
```
bornes-irve/
└── ANNÉE/
    └── MOIS/
        └── bornes_irve_hdf_YYYYMMDD.csv
```

## Logs
Les logs sont générés dans :
- Console (temps réel)
- Fichier `bornes_irve_to_datalake.log`

