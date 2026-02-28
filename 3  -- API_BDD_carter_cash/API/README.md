
# API FastAPI pour la recherche de produits et de dimensions de pneus (Carter Cash)

Ce projet est une API construite avec FastAPI qui permet :

• De rechercher des produits (pneus) en fonction de leur marque,  
• D’interroger la base de données pour connaître les dimensions de pneus par modèle de voiture (marque, modèle et année),  
• De gérer l’authentification et les utilisateurs,  
• D’éviter les injections SQL grâce à une validation renforcée des paramètres (regex, mots-clés interdits, etc.).  

L’API s’appuie sur une base de données SQL Server pour stocker les informations sur les produits, les utilisateurs et les dimensions de pneus.

## Sommaire

1. [Structure du projet](#structure-du-projet)  
2. [Configuration (.env)](#configuration-env)  
3. [Installation des dépendances](#installation-des-dépendances)  
4. [Démarrage de l’application](#démarrage-de-lapplication)  
5. [Endpoints disponibles](#endpoints-disponibles)  
   - [Endpoints de recherche de produits](#endpoints-de-recherche-de-produits)  
   - [Endpoints de recherche de dimensions](#endpoints-de-recherche-de-dimensions)  
   - [Endpoints d’authentification](#endpoints-dauthentification)  
6. [Modèles de données](#modèles-de-données)  
7. [Sécurité et prévention des injections SQL](#sécurité-et-prévention-des-injections-sql)  

---

## Structure du projet

Le projet est organisé de la manière suivante :

```
.
├── .env
├── main.py
├── models.py
├── README.md
├── requirements.txt
├── structure.txt
├── database
│   ├── auth.py
│   ├── db_connection.py
│   ├── dimensions.py
│   ├── search.py
│   └── __pycache__
├── routers
│   ├── auth_router.py
│   ├── dimensions_router.py
│   ├── search_router.py
│   └── __pycache__
├── test
└── __pycache__
```

- Le dossier `database` contient la logique de connexion à la base de données, les fonctions de recherche de produits, les fonctions gérant l’authentification et la validation d’informations.  
- Le dossier `routers` contient les routeurs FastAPI, chacun consacré à une partie fonctionnelle de l’API (authentification, recherche de produits, recherche de dimensions).  
- `main.py` lance l’application FastAPI et inclut tous les routeurs.  
- `models.py` regroupe les modèles Pydantic (requêtes, réponses, etc.).  
- `.env` stocke les informations sensibles de connexion.  
- `requirements.txt` liste toutes les dépendances nécessaires au projet.

---

## Configuration (.env)

Avant de lancer l’application, vous devez créer un fichier `.env` à la racine du projet pour y renseigner vos informations de connexion à la base de données et les variables de sécurité :

```
DB_SERVER=<votre_serveur>
DB_DATABASE=<votre_base_de_données>
DB_USERNAME=<votre_nom_d_utilisateur>
DB_PASSWORD=<votre_mot_de_passe>
SECRET_KEY=<cle_secrete_pour_jwt>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Ces variables sont chargées automatiquement par l’application (via `python-dotenv`) pour sécuriser la connexion à la base de données et la génération de tokens.

---

## Installation des dépendances

Assurez-vous d’avoir Python 3.10 (ou version supérieure). Installez ensuite les dépendances depuis le fichier `requirements.txt` :

```
pip install -r requirements.txt
```

---

## Démarrage de l’application

Pour lancer l’API en local :

```
uvicorn main:app --host 127.0.0.1 --port 8000
```

L’API sera alors accessible à l’adresse :  
http://127.0.0.1:8000

Vous pouvez également spécifier un autre port (ex. 8080) ou hôte selon vos besoins.

---

## Endpoints disponibles

### Endpoints de recherche de produits

1. `GET /search/{marque}`  
   • Recherche tous les produits (pneus) correspondant à la marque indiquée.  
   • Exemple : `/search/Michelin`  
   • Nécessite un token d’accès (via header Authorization: Bearer <token>).

### Endpoints de recherche de dimensions

1. `GET /dimensions_for_modele_car?marque={marque}&modele={modele}&annee={annee}`  
   • Recherche et retourne les dimensions de pneus pour une marque, modèle et année de véhicule (table DimensionsParModel).  
   • Exemple : `/dimensions_for_modele_car?marque=Renault&modele=Clio&annee=2015`  
   • Nécessite un token d’accès.  

### Endpoints d’authentification

1. `POST /token`  
   • Permet de générer un token JWT pour un utilisateur déjà enregistré.  
   • Utilise le schéma `OAuth2PasswordRequestForm` (nécessite `username` et `password`).  

2. `POST /register`  
   • Permet de créer un nouvel utilisateur (nécessite `username`, `email`, `full_name` et `password`).  

3. `PUT /users/me/password`  
   • Permet de modifier le mot de passe d’un utilisateur authentifié.  
   • Nécessite le token d’accès, ainsi que la saisie de l’ancien et du nouveau mot de passe.  

---

## Modèles de données

• `Produit` : Représente un pneu ou produit.  
• `UserCreate` : Pour la création d’un nouvel utilisateur (username, email, full_name, password).  
• `User` : Représente un utilisateur stocké en base, avec mot de passe haché.  
• `Token` : Renvoie le token d’accès généré par l’API.  
• `PasswordChange` : Permet de modifier son mot de passe en fournissant :  
   - current_password  
   - new_password  
   - confirm_password  

---

## Sécurité et prévention des injections SQL

Pour assurer la sécurité et l’intégrité de la base de données, plusieurs mesures de prévention des injections SQL ont été implémentées :

1. Utilisation de requêtes paramétrées via des placeholders (ex. `WHERE marque = ?`).  
2. Validation des entrées utilisateurs avec :  
   • Des regex pour filtrer les caractères spéciaux non autorisés,  
   • Une liste de mots-clés SQL interdits (SELECT, DROP, DELETE, etc.) dans la fonction `validate_marque` de `search.py`.  
3. Gestion d’exception pour logs et blocage automatique de la requête si une tentative malveillante est détectée.  



