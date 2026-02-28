
# Projet Scraping Paruvendu - Pipeline de données automobiles

## Description
Pipeline complet de collecte et traitement de données techniques automobiles depuis Paruvendu.fr, comportant trois phases principales :
1. Scraping des fiches techniques
2. Transfert vers Azure Data Lake
3. ETL vers base de données SQL

## Architecture du projet

### Structure des fichiers
```
scrap_2 paruvendu/
│
├── fiche_technique_auto/
│   └── fiche_technique_auto/
│       └── spiders/
│           └── auto_spider.py
│
├── scrap_to_DL.py
├── ETL_DL_to_BDD.py
└── .env
```

## 1. Phase de Scraping (auto_spider.py)

### Caractéristiques
- Spider Scrapy optimisé pour la collecte massive de données
- Plus de 260 000 fiches techniques collectées
- Durée approximative : 24 heures
- Données collectées : marque, modèle, année, titre, énergie, pneumatiques

### Mécanismes anti-ban implémentés
- Délai entre requêtes (DOWNLOAD_DELAY: 0.5)
- Rotation des requêtes (CONCURRENT_REQUESTS: 32)
- Cache HTTP activé (HTTPCACHE_ENABLED)
- Gestion des timeouts et retries
- Compression HTTP activée
- Désactivation des cookies

### Exécution du scraping
```bash
.\env\Scripts\activate
cd fiche_technique_auto/fiche_technique_auto
scrapy crawl auto_spider
```

## 2. Transfert Data Lake (scrap_to_DL.py)

### Fonctionnalités
- Copie sécurisée des données scrapées vers Azure Data Lake
- Organisation hiérarchique : scrap_auto/année/mois/
- Gestion des logs et erreurs
- Validation des données avant transfert

## 3. ETL vers BDD (ETL_DL_to_BDD.py)

### Transformations
- Nettoyage des finitions véhicules
- Parsing des dimensions pneumatiques
- Standardisation des données
- Chargement optimisé par lots

### Structure finale en BDD
```sql
CREATE TABLE DimensionsParModel (
    Marque VARCHAR(100),
    Modele VARCHAR(100),
    Annee INT,
    Finition VARCHAR(255),
    Largeur INT,
    Hauteur INT,
    Diametre INT
)
```

## Configuration

### Prérequis
- Python 3.8+
- Scrapy
- Azure Data Lake Storage Gen2
- SQL Server

### Variables d'environnement (.env)
```
STORAGE_ACCOUNT_NAME=xxx
STORAGE_ACCOUNT_KEY=xxx
CONTAINER_NAME=xxx
DB_SERVER=xxx
DB_DATABASE=xxx
DB_USERNAME=xxx
DB_PASSWORD=xxx
```

### Dépendances Python
```bash
pip install -r requirements.txt        
```

## Logs et Monitoring
- Scraping : logs Scrapy standards
- Data Lake : scrap_auto_to_datalake.log
- ETL : etl_dimensions_auto.log

## Objectif final
Ces données alimentent une base comparative des dimensions de pneumatiques par véhicule, permettant :
- Analyse des compatibilités
- Intégration avec les données Carter Cash
- Études statistiques sur les configurations pneumatiques

## Performance et volumétrie
- 260 000+ fiches techniques collectées
- Temps de scraping optimisé : ~24h
- Chargement BDD par lots de 500 entrées

