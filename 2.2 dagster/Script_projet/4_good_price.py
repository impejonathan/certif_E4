import os
from dotenv import load_dotenv
import pyodbc

import pyodbc
import requests

from lxml import html
import requests
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





# Connexion à la base de données
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Sélection de la date la plus élevée dans la colonne Date_scrap de la table Produit
cursor.execute("SELECT MAX(Date_scrap) FROM Produit")
date_max = cursor.fetchone()[0]

# Sélection des URL_Produit, Prix et Date_scrap de la table Produit pour la date la plus élevée
cursor.execute("SELECT ID_Produit, URL_Produit, Prix, Date_scrap FROM Produit WHERE Date_scrap = ?", date_max)
rows = cursor.fetchall()

for row in rows:
    id_produit = row[0]
    url_produit = row[1]
    prix_produit = row[2]
    
    # Obtenir le contenu HTML de la page
    response = requests.get(url_produit)
    tree = html.fromstring(response.content)
    
    # Extraire le prix de la page
    prix_page_list = tree.xpath('//*[@id="tire"]/div[2]/div[3]/div/div[3]/div[2]/div[2]/div[1]/div/form/div[1]/div[1]/div/div/span/text()')
    
    # Vérifier si la liste est vide
    if prix_page_list:
        prix_page = prix_page_list[0]
    else:
        prix_page = 666
    
    # Comparer le prix de la page avec le prix dans la base de données
    if prix_produit != prix_page:
        # Mettre à jour le prix dans la base de données
        cursor.execute("UPDATE Produit SET Prix = ? WHERE ID_Produit = ?", prix_page, id_produit)

cnxn.commit()
cnxn.close()
