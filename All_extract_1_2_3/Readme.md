
# Projet d'Extraction et Stockage Multi-Sources

## Description du Projet
Ce projet constitue une solution complète d'extraction, de transformation et de stockage de données provenant de diverses sources vers Azure Data Lake (avec ses différents containers) et une base de données SQL. Il comprend quatre modules principaux permettant de gérer différents types de données.

## Structure du Projet
```
projet_extraction/
│
├── 1 - scrap_2 paruvendu -- Source 1/
│   └── (Scraping des données automobiles Paruvendu)
│
├── 2 - API_to_DL -- Source 2/
│   └── (Extraction API bornes IRVE)
│
├── 3 - fichier_plat_to_DL -- Source 3/
│   └── (Traitement données INSEE)
│
├── 4 - CSV RECUP carter cash BDD_to_DL/
│   └── (Gestion des données Carter Cash)
│
├── requirements.txt
├── .env
└── README.md
```

## Sources de Données
1. **Paruvendu** : Scraping des fiches techniques automobiles (→ data-gouv)
2. **OpenData Réseaux Énergies** : API des bornes IRVE Hauts-de-France (→ bronze-data)
3. **INSEE** : Fichiers NAF (Nomenclature d'Activités Française) (→ data-gouv)
4. **Carter Cash** : Données produits et caractéristiques (→ gold-data)

## Installation et Configuration

### 1. Création de l'environnement virtuel
```bash
# Création
python -m venv env

# Activation (Windows)
.\env\Scripts\activate

# Désactivation
deactivate
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration du fichier .env unifié
```env
# Azure Storage Configuration
STORAGE_ACCOUNT_NAME=xxx
STORAGE_ACCOUNT_KEY=xxx

# Container Names
CONTAINER_NAME_bronze-data=xxx
CONTAINER_NAME_data-gouv=xxx
CONTAINER_NAME_gold-data=xxx

# Database Configuration
DB_SERVER=xxx
DB_DATABASE=xxx
DB_USERNAME=xxx
DB_PASSWORD=xxx

# API Configuration
INSEE_URL=xxx
```

## Dépendances Principales
```txt
azure-storage-file-datalake==12.x.x
pandas==2.x.x
scrapy==2.x.x
pyodbc==4.x.x
python-dotenv==1.x.x
requests==2.x.x
```

## Architecture de Stockage
### Azure Data Lake

#### Container: bronze-data
```
bornes-irve/
└── ANNÉE/
    └── MOIS/
        └── bornes_irve_hdf_YYYYMMDD.csv
```

#### Container: data-gouv
```
├── scrap_auto/
│   └── ANNÉE/
│       └── MOIS/
│           └── scrap_auto_YYYYMMDD.csv
└── data_NAF/
    └── naf_rev2_YYYYMMDD.xls
```

#### Container: gold-data
```
Data_Carter_cash_BDD_SQL/
├── Produit/
├── Caracteristiques/
└── Dimensions/
    └── ANNÉE/
        └── MOIS/
            └── fichier_YYYYMMDD.csv
```

## Fonctionnalités Principales

### 1. Module Scraping Paruvendu (→ data-gouv)
- Extraction massive de fiches techniques automobiles
- Pipeline ETL complet vers Data Lake et BDD
- Gestion anti-ban et optimisation des performances

### 2. Module API IRVE (→ bronze-data)
- Collecte automatisée des données de bornes de recharge
- Stockage structuré dans le Data Lake
- Mise à jour quotidienne

### 3. Module INSEE (→ data-gouv)
- Téléchargement automatique des données NAF
- Validation et transformation des données
- Organisation chronologique dans le Data Lake

### 4. Module Carter Cash (→ gold-data)
- Système de sauvegarde BDD vers Data Lake
- Conservation historique des données
- Possibilité de restauration complète

## Monitoring et Logs
Chaque module dispose de son propre système de logging :
- Fichiers de logs spécifiques
- Traçabilité des opérations
- Gestion des erreurs

## Sécurité
- Gestion centralisée des credentials via .env
- Validation des variables d'environnement
- Connexions sécurisées aux services Azure

## Maintenance
- Sauvegarde automatique des données
- Vérification d'intégrité
- Scripts de restauration disponibles

## Support
Pour toute question ou problème :
1. Consulter la documentation spécifique de chaque module
2. Vérifier les logs d'erreurs
3. Contacter l'équipe de développement

## Note
Ce projet est conçu pour fonctionner avec Azure Data Lake Storage Gen2 et SQL Server. Les données sont organisées dans trois containers distincts selon leur nature et leur niveau de traitement :
- **bronze-data** : Données brutes des bornes IRVE
- **data-gouv** : Données gouvernementales et de scraping
- **gold-data** : Données nettoyées et structurées
