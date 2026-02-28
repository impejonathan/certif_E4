import os
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient
import logging
import shutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrap_auto_to_datalake.log'),
        logging.StreamHandler()
    ]
)

# Charger les variables d'environnement
load_dotenv()

class ScrapAutoToDataLake:
    def __init__(self):
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME')
        self.source_file_path = r"fiche_technique_auto\fiche_technique_auto\resultats_autos.csv"
        self.absolute_source_path = r"C:\Users\impej\Desktop\Certificatoin Data Engineer\E4-E7\scrap_2 paruvendu\fiche_technique_auto\fiche_technique_auto\resultats_autos.csv"
        
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

    def copy_to_working_directory(self):
        """Copie le fichier source vers le dossier de travail"""
        try:
            # Créer le dossier data s'il n'existe pas
            os.makedirs('data', exist_ok=True)

            # Générer le nom du fichier avec la date
            current_date = datetime.now().strftime("%Y%m%d")
            self.local_filename = f'data/resultats_autos_{current_date}.csv'

            # Copier le fichier
            if os.path.exists(self.source_file_path):
                source = self.source_file_path
            elif os.path.exists(self.absolute_source_path):
                source = self.absolute_source_path
            else:
                raise FileNotFoundError("Fichier source introuvable")

            shutil.copy2(source, self.local_filename)
            logging.info(f"Fichier copié avec succès vers: {self.local_filename}")
            return True

        except Exception as e:
            logging.error(f"Erreur lors de la copie du fichier: {str(e)}")
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
            datalake_path = f"scrap_auto/{current_date.year}/{current_date.month:02d}/{os.path.basename(self.local_filename)}"

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
        scrap_dl = ScrapAutoToDataLake()

        # Copie du fichier
        if scrap_dl.copy_to_working_directory():
            # Upload vers Data Lake
            scrap_dl.upload_to_datalake()
        else:
            logging.error("Le processus s'est arrêté suite à l'échec de la copie")

        logging.info("Processus terminé")

    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()
