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


# Mise à jour de la colonne Marque dans la table Produit
cursor.execute("""
UPDATE Produit
SET Marque = CASE 
    WHEN CHARINDEX(' ', Descriptif) > 0 THEN LEFT(Descriptif, CHARINDEX(' ', Descriptif) - 1)
    ELSE Descriptif
END
WHERE Marque IS NULL OR Marque = ''
""")

cnxn.commit()
cnxn.close()

print("La colonne 'Marque' a été mise à jour avec succès.")
