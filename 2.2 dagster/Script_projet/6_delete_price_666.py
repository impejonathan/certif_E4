import os
from dotenv import load_dotenv
import pyodbc
import logging

# Charger les variables d'environnement
load_dotenv()

# Configuration du système de journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

driver = '{ODBC Driver 17 for SQL Server}'

try:
    # Connexion à la base de données
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

    # Suppression des lignes correspondantes dans la table Caracteristiques
    cursor.execute("""
        DELETE FROM Caracteristiques
        WHERE ID_Produit IN (
            SELECT ID_Produit
            FROM Produit
            WHERE Prix = 666
        )
    """)
    logger.info("Lignes supprimées dans la table 'Caracteristiques' pour les produits avec 'Prix' = 666.")

    # Suppression des lignes correspondantes dans la table Dimensions
    cursor.execute("""
        DELETE FROM Dimensions
        WHERE ID_Produit IN (
            SELECT ID_Produit
            FROM Produit
            WHERE Prix = 666
        )
    """)
    logger.info("Lignes supprimées dans la table 'Dimensions' pour les produits avec 'Prix' = 666.")

    # Suppression des lignes dans la table Produit
    cursor.execute("""
        DELETE FROM Produit
        WHERE Prix = 666
    """)
    logger.info("Lignes supprimées dans la table 'Produit' avec 'Prix' = 666.")

    # Valider les modifications
    cnxn.commit()
    logger.info("Les modifications ont été validées.")

except Exception as e:
    logger.error(f"Une erreur s'est produite : {e}")

finally:
    # Fermer la connexion
    if cnxn:
        cnxn.close()
        logger.info("La connexion à la base de données a été fermée.")
