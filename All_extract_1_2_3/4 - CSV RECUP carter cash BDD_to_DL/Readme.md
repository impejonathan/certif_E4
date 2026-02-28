
# CSV Récupération et Transfert de Données

## Contexte et Objectif
Ce dossier a été créé dans le cadre d'un projet de test et sauvegarde de  pour :
- Valider le processus de transfert de données depuis une base de données Azure SQL vers un Data Lake
- Mettre en place un système de sauvegarde fiable des données
- Assurer la pérennité des données en cas de suppression accidentelle dans la BDD

## Description
Le projet contient deux scripts principaux pour la gestion des données entre une base de données Azure SQL et un Data Lake :
1. Un script pour l'insertion des données CSV dans la base de données Azure SQL
2. Un script pour la sauvegarde et le transfert des données de la BDD vers Azure Data Lake

## Structure du Projet
```
CSV_recupe/
│
├── BDD_to_DL.py
├── csv_bdd.ipynb
├── .env
├── requirements.txt
└── README.md
```

## Prérequis
- Python 3.x
- Compte Azure avec accès à SQL Database et Data Lake Storage
- Driver ODBC 17 pour SQL Server

## Installation
1. Cloner le repository
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration
Créer un fichier `.env` à la racine du projet avec les informations suivantes :
```env
# Configuration BDD
DB_SERVER=votre_serveur
DB_DATABASE=votre_base
DB_USERNAME=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe

# Configuration Storage
STORAGE_ACCOUNT_NAME=votre_compte_storage
STORAGE_ACCOUNT_KEY=votre_clé_storage
CONTAINER_NAME_gold-data=votre_container
```

## Fonctionnalités

### 1. Insertion des données CSV (csv_bdd.ipynb)
- Lecture des fichiers CSV (produit.csv, carateris.csv, dimen.csv)
- Gestion des types de données
- Insertion dans les tables SQL correspondantes :
  - Produit
  - Caracteristiques
  - Dimensions

### 2. Sauvegarde vers Data Lake (BDD_to_DL.py)
- Export automatique des tables SQL vers CSV
- Structure de stockage organisée dans le Data Lake :
  ```
  Data_Carter_cash_BDD_SQL/
  ├── Produit/
  ├── Caracteristiques/
  └── Dimensions/
      └── ANNÉE/
          └── MOIS/
              └── fichier_YYYYMMDD.csv
  ```
- Logging complet des opérations
- Gestion des erreurs

## Utilisation

### Pour l'insertion des données CSV vers la BDD :
```bash
jupyter notebook csv_bdd.ipynb
```

### Pour la sauvegarde vers Data Lake :
```bash
python BDD_to_DL.py
```

## Système de Sauvegarde
- Sauvegarde automatique quotidienne des données
- Conservation de l'historique complet dans le Data Lake
- Organisation chronologique des fichiers
- Protection contre la perte de données
- Possibilité de restauration complète en cas de besoin

## Logs
Les logs sont enregistrés dans :
- Console (sortie standard)
- Fichier 'sql_to_datalake.log'

## Sécurité
- Utilisation de variables d'environnement pour les informations sensibles
- Gestion sécurisée des connexions
- Nettoyage automatique des ressources après utilisation

## Maintenance et Récupération
En cas de suppression de données dans la BDD :
1. Les données sont automatiquement sauvegardées dans le Data Lake
2. Conservation d'un historique complet des données
3. Possibilité de restauration via les fichiers CSV stockés
4. Vérification de l'intégrité des données lors des transferts

