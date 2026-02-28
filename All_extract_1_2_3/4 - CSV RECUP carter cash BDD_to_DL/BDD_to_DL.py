import os
from dotenv import load_dotenv
import pyodbc
import pandas as pd
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sql_to_datalake.log'),
        logging.StreamHandler()
    ]
)

class SQLToDataLake:
    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()
        
        # Configuration SQL
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        
        # Configuration Data Lake
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME_gold-data')
        
        # Liste des tables à exporter
        self.tables = ['Produit', 'Caracteristiques', 'Dimensions']
        
        # Initialisation des clients
        self.sql_conn = self._init_sql_connection()
        self.datalake_client = self._init_datalake_client()

    def _init_sql_connection(self):
        """Initialise la connexion SQL"""
        try:
            driver = '{ODBC Driver 17 for SQL Server}'
            conn_str = f'DRIVER={driver};SERVER={self.server};PORT=1433;DATABASE={self.database};UID={self.username};PWD={self.password}'
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.error(f"Erreur de connexion SQL: {str(e)}")
            raise

    def _init_datalake_client(self):
        """Initialise le client Data Lake"""
        try:
            return DataLakeServiceClient(
                account_url=f"https://{self.storage_account_name}.dfs.core.windows.net",
                credential=self.storage_account_key
            )
        except Exception as e:
            logging.error(f"Erreur d'initialisation du client Data Lake: {str(e)}")
            raise

    def export_table_to_csv(self, table_name):
        """Exporte une table en CSV"""
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, self.sql_conn)
            
            # Créer le dossier data s'il n'existe pas
            os.makedirs('data', exist_ok=True)
            
            # Générer le nom du fichier avec la date
            current_date = datetime.now().strftime("%Y%m%d")
            filename = f'data/{table_name}_{current_date}.csv'
            
            # Sauvegarder en CSV
            df.to_csv(filename, index=False)
            logging.info(f"Table {table_name} exportée vers {filename}")
            return filename
        except Exception as e:
            logging.error(f"Erreur lors de l'export de {table_name}: {str(e)}")
            return None

    def upload_to_datalake(self, local_file, table_name):
        """Upload un fichier vers Data Lake"""
        try:
            # Obtenir une référence au container
            file_system_client = self.datalake_client.get_file_system_client(self.container_name)  # ici nom du Container ####################
            
            # Définir le chemin dans le Data Lake
            current_date = datetime.now()
            datalake_path = f"Data_Carter_cash_BDD_SQL/{table_name}/{current_date.year}/{current_date.month:02d}/{os.path.basename(local_file)}"
            
            # Upload du fichier
            file_client = file_system_client.get_file_client(datalake_path)
            
            with open(local_file, 'rb') as file:
                file_contents = file.read()
                file_client.upload_data(file_contents, overwrite=True)
                
            logging.info(f"Fichier uploadé avec succès vers: {datalake_path}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'upload de {local_file}: {str(e)}")
            return False

    def process_all_tables(self):
        """Traite toutes les tables"""
        try:
            for table in self.tables:
                logging.info(f"Traitement de la table {table}")
                
                # Export en CSV
                local_file = self.export_table_to_csv(table)
                if local_file:
                    # Upload vers Data Lake
                    self.upload_to_datalake(local_file, table)
                    
            logging.info("Traitement de toutes les tables terminé")
        except Exception as e:
            logging.error(f"Erreur lors du traitement des tables: {str(e)}")

    def cleanup(self):
        """Ferme les connexions"""
        try:
            self.sql_conn.close()
            logging.info("Nettoyage effectué avec succès")
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage: {str(e)}")

def main():
    try:
        logging.info("Démarrage du processus d'export SQL vers Data Lake")
        
        # Création de l'instance
        sql_dl = SQLToDataLake()
        
        # Traitement des tables
        sql_dl.process_all_tables()
        
        # Nettoyage
        sql_dl.cleanup()
        
        logging.info("Processus terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()
