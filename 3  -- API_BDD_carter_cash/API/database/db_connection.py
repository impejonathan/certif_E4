# db_connection.py
import os
import pyodbc
from dotenv import load_dotenv
from contextlib import contextmanager

# SÉCURITÉ : Chargement des variables d'environnement depuis .env
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        # SÉCURITÉ : Utilisation de variables d'environnement pour les informations sensibles
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.driver = '{ODBC Driver 17 for SQL Server}'
        
        # SÉCURITÉ : Construction sécurisée de la chaîne de connexion
        self.connection_string = (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password}'
        )

    @contextmanager
    def get_cursor(self):
        # SÉCURITÉ : Gestion automatique des connexions
        conn = pyodbc.connect(self.connection_string)
        try:
            cursor = conn.cursor()
            yield cursor
            # SÉCURITÉ : Validation explicite des transactions
            conn.commit()
        except Exception as e:
            # SÉCURITÉ : Rollback automatique en cas d'erreur
            conn.rollback()
            raise e
        finally:
            # SÉCURITÉ : Fermeture garantie des ressources
            cursor.close()
            conn.close()

# SÉCURITÉ : Instance unique de connexion
db = DatabaseConnection()
