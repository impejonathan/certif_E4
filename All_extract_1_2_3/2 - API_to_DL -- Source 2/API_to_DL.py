import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bornes_irve_to_datalake.log'),
        logging.StreamHandler()
    ]
)

# Charger les variables d'environnement
load_dotenv()

class BornesIrveToDataLake:
    def __init__(self):
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME_bronze-data')
        self.api_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/bornes-irve/exports/csv"
        
        # Validation des variables d'environnement
        self._validate_env_variables()
        
        # Initialisation du client Data Lake
        self.service_client = self._initialize_datalake_client()

    def _validate_env_variables(self):
        """Valide la présence des variables d'environnement requises"""
        required_vars = ['STORAGE_ACCOUNT_NAME', 'STORAGE_ACCOUNT_KEY', 'CONTAINER_NAME']
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

    def download_csv_file(self):
        """Télécharge le fichier CSV des bornes IRVE"""
        params = {
            'lang': 'fr',
            'refine': 'region:"Hauts-de-France"',
            'facet': 'facet(name="region", disjunctive=true)',
            'timezone': 'Europe/Berlin',
            'use_labels': 'true',
            'delimiter': ';'
        }

        try:
            # Créer le dossier data s'il n'existe pas
            os.makedirs('data', exist_ok=True)

            # Faire la requête HTTP
            logging.info("Début du téléchargement du fichier")
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()

            # Générer un nom de fichier avec la date
            current_date = datetime.now().strftime("%Y%m%d")
            self.local_filename = f'data/bornes_irve_hdf_{current_date}.csv'

            # Sauvegarder le fichier
            with open(self.local_filename, 'wb') as f:
                f.write(response.content)

            logging.info(f"Fichier téléchargé avec succès: {self.local_filename}")
            return True

        except Exception as e:
            logging.error(f"Erreur lors du téléchargement: {str(e)}")
            return False

    def upload_to_datalake(self):
        """Upload le fichier vers Azure Data Lake"""
        try:
            # Obtenir une référence au container
            file_system_client = self.service_client.get_file_system_client(
                file_system=self.container_name
            )

            # Définir le chemin dans le Data Lake
            current_date = datetime.now()
            datalake_path = f"bornes-irve/{current_date.year}/{current_date.month:02d}/{os.path.basename(self.local_filename)}"

            # Upload du fichier
            file_client = file_system_client.get_file_client(datalake_path)
            
            with open(self.local_filename, 'rb') as file:
                file_contents = file.read()
                file_client.upload_data(file_contents, overwrite=True)

            logging.info(f"Fichier uploadé avec succès vers: {datalake_path}")
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'upload: {str(e)}")
            return False

def main():
    try:
        logging.info("Démarrage du processus")
        
        # Création de l'instance
        bornes_dl = BornesIrveToDataLake()

        # Téléchargement du fichier
        if bornes_dl.download_csv_file():
            # Upload vers Data Lake
            bornes_dl.upload_to_datalake()
        else:
            logging.error("Le processus s'est arrêté suite à l'échec du téléchargement")

        logging.info("Processus terminé")

    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()
