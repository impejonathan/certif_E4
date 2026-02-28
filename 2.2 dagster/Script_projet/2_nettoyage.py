import os
from dotenv import load_dotenv
import pyodbc

import pyodbc
import requests


# Charger les variables d'environnement
load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()



# Sélection de la date la plus élevée dans la colonne Date_scrap de la table Produit
cursor.execute("SELECT MAX(Date_scrap) FROM Produit")
max_date = cursor.fetchone()[0]

# Sélection des tables qui ont la date la plus élevée dans la colonne Date_scrap de la table Produit
cursor.execute("SELECT ID_Produit, URL_Produit FROM Produit WHERE Date_scrap = ?", max_date)
rows = cursor.fetchall()

for row in rows:
    id_produit = row[0]
    url_produit = row[1]
    
    try:
        # Suivre les redirections pour obtenir l'URL finale
        response = requests.get(url_produit)
        url_final = response.url
        
        # Mettre à jour l'URL_Produit dans la table Produit si une redirection a eu lieu
        if url_produit != url_final:
            cursor.execute("UPDATE Produit SET URL_Produit = ? WHERE ID_Produit = ?", url_final, id_produit)
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la tentative d'accès à l'URL {url_produit} : {e}")

cnxn.commit()
cnxn.close()
