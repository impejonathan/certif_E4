import os
from dotenv import load_dotenv
import pyodbc

# Charger les variables d'environnement
load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

driver = '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Compter le nombre de lignes dans la table Produit avant la suppression
cursor.execute("SELECT COUNT(*) FROM Produit")
nombre_lignes_avant_suppression = cursor.fetchone()[0]

# Récupérer les ID des doublons dans la table Produit
cursor.execute("""
WITH CTE AS (
    SELECT ID_Produit, URL_Produit, Date_scrap,
           RN = ROW_NUMBER() OVER (PARTITION BY URL_Produit, Prix, Date_scrap ORDER BY ID_Produit)
    FROM Produit
)
SELECT ID_Produit FROM CTE WHERE RN > 1
""")
duplicates = cursor.fetchall()

# Suppression des enregistrements liés dans la table Caracteristiques
for id_produit in duplicates:
    cursor.execute("DELETE FROM Caracteristiques WHERE ID_Produit = ?", id_produit)

# Suppression des enregistrements liés dans la table Dimensions
for id_produit in duplicates:
    cursor.execute("DELETE FROM Dimensions WHERE ID_Produit = ?", id_produit)

# Suppression des doublons dans la table Produit
cursor.execute("""
WITH CTE AS (
    SELECT ID_Produit, URL_Produit, Date_scrap,
           RN = ROW_NUMBER() OVER (PARTITION BY URL_Produit, Prix, Date_scrap ORDER BY ID_Produit)
    FROM Produit
)
DELETE FROM CTE WHERE RN > 1
""")
cnxn.commit()

# Compter le nombre de lignes restantes dans la table Produit après la suppression
cursor.execute("SELECT COUNT(*) FROM Produit")
nombre_lignes_apres_suppression = cursor.fetchone()[0]

# Calculer le nombre de lignes supprimées
lignes_supprimees = nombre_lignes_avant_suppression - nombre_lignes_apres_suppression

print("Nombre de lignes supprimées de la table Produit :", lignes_supprimees)

cnxn.close()
