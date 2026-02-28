import os
from dotenv import load_dotenv
import pyodbc

# Charger les variables d'environnement
load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Exécuter la requête SQL pour obtenir le nombre de lignes avec la date la plus élevée dans Date_scrap
cursor.execute("""
SELECT COUNT(*)
FROM Produit
WHERE Date_scrap = (SELECT MAX(Date_scrap) FROM Produit)
""")

# Récupérer le résultat de la requête
nombre_lignes = cursor.fetchone()[0]

print("Il y a  : -- ", nombre_lignes, " -- lignes qui ont été injecter lors du dernier scraping")

cnxn.close()
