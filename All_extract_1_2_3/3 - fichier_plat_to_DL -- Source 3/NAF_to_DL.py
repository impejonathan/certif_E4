import requests
import os
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('insee_to_datalake.log'),
        logging.StreamHandler()
    ]
)

# Chargement des variables d'environnement
load_dotenv()

class InseeToDataLake:
    def __init__(self):
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME')
        self.insee_url = os.getenv('INSEE_URL', 
            "https://www.insee.fr/fr/statistiques/fichier/2120875/int_courts_naf_rev_2.xls")
        
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

    def download_insee_file(self):
        """Télécharge le fichier INSEE"""
        try:
            # Créer le dossier 'data' s'il n'existe pas
            os.makedirs('data', exist_ok=True)

            # Télécharger le fichier
            response = requests.get(self.insee_url)
            response.raise_for_status()

            # Générer le nom du fichier avec la date
            date_str = datetime.now().strftime("%Y%m%d")
            self.local_filename = f"data/naf_rev2_{date_str}.xls"

            # Sauvegarder le fichier
            with open(self.local_filename, 'wb') as file:
                file.write(response.content)

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

            # Construire le chemin distant
            file_name = os.path.basename(self.local_filename)
            remote_file_path = f"data_NAF/{file_name}"  # Modification ici pour le nouveau chemin

            # Upload du fichier
            file_client = file_system_client.get_file_client(remote_file_path)
            
            with open(self.local_filename, 'rb') as file:
                file_contents = file.read()
                file_client.upload_data(file_contents, overwrite=True)

            logging.info(f"Fichier uploadé avec succès vers: {remote_file_path}")
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'upload: {str(e)}")
            return False

def main():
    try:
        # Création de l'instance
        insee_dl = InseeToDataLake()

        # Téléchargement du fichier
        if insee_dl.download_insee_file():
            # Upload vers Data Lake
            insee_dl.upload_to_datalake()
        else:
            logging.error("Le processus s'est arrêté suite à l'échec du téléchargement")

    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()
