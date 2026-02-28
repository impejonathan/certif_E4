import pandas as pd
import re
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv
import os
import logging
import io
import pyodbc
from tqdm import tqdm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_dimensions_auto.log'),
        logging.StreamHandler()
    ]
)

class ETLDimensionsAuto:
    def __init__(self):
        load_dotenv()
        # Configuration Data Lake
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME')
        
        # Configuration SQL
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        
        # Initialisation des connexions
        self.datalake_client = self._init_datalake_client()
        self.sql_conn = self._init_sql_connection()

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

    def _init_sql_connection(self):
        """Initialise la connexion SQL"""
        try:
            driver = '{ODBC Driver 17 for SQL Server}'
            conn_str = f'DRIVER={driver};SERVER={self.server};PORT=1433;DATABASE={self.database};UID={self.username};PWD={self.password}'
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.error(f"Erreur de connexion SQL: {str(e)}")
            raise

    def get_data_from_datalake(self):
        """Récupère le fichier CSV du Data Lake"""
        try:
            file_system_client = self.datalake_client.get_file_system_client(self.container_name)
            file_path = "scrap_auto/2025/01/resultats_autos_20250129.csv"
            file_client = file_system_client.get_file_client(file_path)
            
            download = file_client.download_file()
            file_content = download.readall()
            
            return pd.read_csv(io.BytesIO(file_content))
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données: {str(e)}")
            raise

    def clean_finition(self, row):
        """Nettoie la colonne finition"""
        try:
            titre = row['titre'].replace("Fiche technique ", "")
            marque = str(row['marque']).replace('-', ' ').title()
            modele = str(row['modele']).upper()
            annee = str(row['annee'])
            
            titre = titre.replace(marque, "", 1)
            titre = titre.replace(modele, "", 1)
            titre = titre.replace(annee, "", 1)
            
            return titre.strip()
        except Exception as e:
            logging.warning(f"Erreur dans clean_finition: {str(e)}")
            return None

    def parse_pneumatiques(self, pneu):
        """Parse les dimensions des pneumatiques"""
        try:
            if pd.isna(pneu) or pneu == 'non renseigné' or pneu.startswith('/'):
                return None, None, None
            
            pattern = r'(\d+)/(\d+)\s*[rR]?(\d+)'
            match = re.match(pattern, pneu)
            
            if not match:
                return None, None, None
                
            largeur = int(match.group(1))
            hauteur = int(match.group(2))
            diametre = int(match.group(3))
            
            if len(str(diametre)) == 1:
                return None, None, None
                
            return largeur, hauteur, diametre
        except Exception as e:
            logging.warning(f"Erreur dans parse_pneumatiques: {str(e)}")
            return None, None, None

    def transform_data(self, df):
        """Transforme les données selon les spécifications"""
        try:
            # Filtrer les lignes avec pneumatiques non renseignés
            df = df[df['pneumatiques'] != 'non renseigné'].copy()
            
            # Nettoyer la finition
            df['finition'] = df.apply(self.clean_finition, axis=1)
            
            # Traiter les pneumatiques
            dimensions = df['pneumatiques'].apply(self.parse_pneumatiques)
            df['largeur'] = dimensions.apply(lambda x: x[0] if x else None)
            df['hauteur'] = dimensions.apply(lambda x: x[1] if x else None)
            df['diametre'] = dimensions.apply(lambda x: x[2] if x else None)
            
            # Filtrer les lignes avec des dimensions valides
            df = df.dropna(subset=['largeur', 'hauteur', 'diametre'])
            
            # Convertir les types
            df['largeur'] = df['largeur'].astype(int)
            df['hauteur'] = df['hauteur'].astype(int)
            df['diametre'] = df['diametre'].astype(int)
            df['annee'] = df['annee'].astype(int)
            
            return df[['marque', 'modele', 'annee', 'finition', 'largeur', 'hauteur', 'diametre']]
        except Exception as e:
            logging.error(f"Erreur dans transform_data: {str(e)}")
            raise

    def load_to_database(self, df):
        """Charge les données dans la base de données par lots"""
        try:
            cursor = self.sql_conn.cursor()
            total_rows = len(df)
            batch_size = 500

            # Préparer la requête d'insertion
            insert_query = """
            INSERT INTO DimensionsParModel 
            (Marque, Modele, Annee, Finition, Largeur, Hauteur, Diametre)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            # Créer des lots et insérer avec barre de progression
            with tqdm(total=total_rows, desc="Chargement des données") as pbar:
                for start_idx in range(0, total_rows, batch_size):
                    end_idx = min(start_idx + batch_size, total_rows)
                    batch_df = df.iloc[start_idx:end_idx]

                    # Insérer le lot
                    for _, row in batch_df.iterrows():
                        cursor.execute(insert_query, (
                            row['marque'],
                            row['modele'],
                            int(row['annee']),
                            row['finition'],
                            int(row['largeur']),
                            int(row['hauteur']),
                            int(row['diametre'])
                        ))

                    self.sql_conn.commit()
                    pbar.update(len(batch_df))

            logging.info(f"Total des lignes insérées: {total_rows}")

        except Exception as e:
            logging.error(f"Erreur lors du chargement dans la base de données: {str(e)}")
            self.sql_conn.rollback()
            raise

    def run_etl(self):
        """Exécute le processus ETL complet"""
        try:
            logging.info("Début du processus ETL")
            
            # Extract
            df = self.get_data_from_datalake()
            logging.info(f"Données extraites: {len(df)} lignes")
            
            # Transform
            transformed_df = self.transform_data(df)
            logging.info(f"Données transformées: {len(transformed_df)} lignes")
            
            # Load
            self.load_to_database(transformed_df)
            logging.info("Processus ETL terminé avec succès")
            
        except Exception as e:
            logging.error(f"Erreur dans le processus ETL: {str(e)}")
        finally:
            self.sql_conn.close()

def main():
    try:
        etl = ETLDimensionsAuto()
        etl.run_etl()
    except Exception as e:
        logging.error(f"Erreur dans le processus principal: {str(e)}")

if __name__ == "__main__":
    main()
