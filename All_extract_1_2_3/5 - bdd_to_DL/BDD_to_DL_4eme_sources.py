import os
import pandas as pd
from sqlalchemy import create_engine, text
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv
import logging
import io
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bdd_to_datalake.log'),
        logging.StreamHandler()
    ]
)

# Chargement des variables d'environnement
load_dotenv()

class BDDToDataLake:
    def __init__(self):
        # Variables pour Azure Data Lake
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME_gold-data')

        # Variables pour PostgreSQL
        self.azure_host = os.getenv('AZURE_HOST')
        self.azure_port = os.getenv('AZURE_PORT')
        self.azure_database = os.getenv('AZURE_DATABASE')
        self.azure_user = os.getenv('AZURE_USER')
        self.azure_password = os.getenv('AZURE_PASSWORD')

        # Validation des variables d'environnement
        self._validate_env_variables()

        # Initialisation des clients
        self.service_client = self._initialize_datalake_client()
        self.engine = self._initialize_db_engine()

    def _validate_env_variables(self):
        """Valide la présence des variables d'environnement requises"""
        required_vars = [
            'STORAGE_ACCOUNT_NAME', 'STORAGE_ACCOUNT_KEY', 'CONTAINER_NAME_gold-data',
            'AZURE_HOST', 'AZURE_PORT', 'AZURE_DATABASE', 'AZURE_USER', 'AZURE_PASSWORD'
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")

    def _initialize_datalake_client(self):
        """Initialise le client Data Lake"""
        try:
            return DataLakeServiceClient(
                account_url=f"https://{self.storage_account_name}.dfs.core.windows.net",
                credential=self.storage_account_key
            )
        except Exception as e:
            logging.error(f"Erreur d'initialisation du client Data Lake: {str(e)}")
            raise

    def _initialize_db_engine(self):
        """Initialise le moteur de connexion à la base de données"""
        try:
            return create_engine(
                f"postgresql+psycopg2://{self.azure_user}:{self.azure_password}@{self.azure_host}:{self.azure_port}/{self.azure_database}?sslmode=require"
            )
        except Exception as e:
            logging.error(f"Erreur d'initialisation du moteur de base de données: {str(e)}")
            raise

    def extract_and_upload_data(self):
        """Extrait les données de la base de données et les envoie directement vers le Data Lake"""
        try:
            tables = ["departments", "regions", "cities", "communes_france_2025"]

            file_system_client = self.service_client.get_file_system_client(file_system=self.container_name)

            with self.engine.connect() as conn:
                for table in tables:
                    # Extraction des données
                    query = text(f'SELECT * FROM "{table}"')
                    df = pd.read_sql(query, conn)
                    logging.info(f"Données extraites de la table {table}: {len(df)} lignes")

                    # Conversion du DataFrame en CSV dans un buffer en mémoire
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)

                    # Nom du fichier avec la date
                    date_str = datetime.now().strftime("%Y%m%d")
                    remote_file_path = f"data_to_BDD_data_gouv_city_france/{table}/{table}_{date_str}.csv"

                    # Upload direct vers Data Lake
                    file_client = file_system_client.get_file_client(remote_file_path)
                    file_client.upload_data(csv_buffer.getvalue().encode('utf-8'), overwrite=True)

                    logging.info(f"Fichier {table} uploadé vers Data Lake: {remote_file_path}")

        except Exception as e:
            logging.error(f"Erreur lors de l'extraction ou de l'upload: {str(e)}")
            raise

def main():
    try:
        bdd_dl = BDDToDataLake()
        bdd_dl.extract_and_upload_data()
    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()
