Je vais créer un README.md professionnel en français pour votre projet. Voici la proposition :

# Projet de Gestion de Base de Données pour Pneus

## Description
Ce projet permet la création et la gestion d'une base de données pour stocker et manipuler des informations sur les pneus, incluant leurs caractéristiques, dimensions et la gestion des utilisateurs de l'API.

## Structure du Projet
```
│   .env
│   CRUD.ipynb
│   Création _BDD.ipynb
│   Nettoyage_BDD.ipynb
│   README.md
│   requirements.txt
│   RGPD.ipynb
│   tailles_de_pneus_par_voiture.csv
│
└───autre
        Csv_to_BDD.ipynb
        Model_vehicule.ipynb
```

## Composants Principaux

### 1. Création de la Base de Données (`Création _BDD.ipynb`)
- Initialisation de la structure de la base de données
- Création des tables principales :
  - Produit (informations sur les pneus)
  - Caractéristiques (spécifications techniques)
  - Dimensions (tailles et mesures)
  - USER_API (gestion des utilisateurs)
  - DimensionsParModel (correspondance véhicules/pneus)

### 2. Opérations CRUD (`CRUD.ipynb`)
Module de test permettant de :
- Créer des entrées dans la base de données
- Lire les données existantes
- Mettre à jour les informations
- Supprimer des entrées

### 3. Nettoyage des Données (`Nettoyage_BDD.ipynb`)
- Traitement des données brutes issues du scraping de Carter Cash
- Intégration avec l'orchestrateur Dagster pour le pipeline de données
- Nettoyage automatisé des données lors de l'acquisition

### 4. Gestion RGPD (`RGPD.ipynb`)
Module de conformité RGPD permettant :
- Suppression des comptes inactifs (>24 mois)
- Gestion des comptes sans activité
- Suppression des comptes sur demande utilisateur

## Configuration

### Variables d'Environnement (.env)
```
DB_SERVER=xxxxxxxxxxxxxxxxxxxxxxxx
DB_DATABASE=xxxxxxxxxxxxxxxxx
DB_USERNAME=xxxxxxxxxxxxxx
DB_PASSWORD=xxxxxxxxxxxxxxxxx
```

## Prérequis
Les dépendances nécessaires sont listées dans le fichier `requirements.txt`

## Installation
1. Cloner le repository
2. Créer et configurer le fichier `.env`
3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation
1. Exécuter d'abord `Création _BDD.ipynb` pour initialiser la base de données
2. Utiliser les autres notebooks selon les besoins :
   - `CRUD.ipynb` pour les tests de manipulation des données
   - `Nettoyage_BDD.ipynb` pour le traitement des données
   - `RGPD.ipynb` pour la gestion des utilisateurs

## Notes Techniques
- Utilisation de PyODBC pour la connexion à SQL Server
- Driver ODBC 17 requis pour SQL Server
- Gestion des connexions via variables d'environnement 