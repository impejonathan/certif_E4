from .db_connection import db
from fastapi import HTTPException
from typing import List, Dict, Any
import re

def validate_dimensions_params(marque: str, modele: str, annee: int) -> bool:
    """Valide les paramètres d'entrée pour éviter les caractères non autorisés."""
    # Autoriser uniquement les lettres, chiffres, espaces et certains caractères spéciaux
    pattern = r'^[a-zA-Z0-9\s\-_.]+$'
    if not re.match(pattern, marque) or not re.match(pattern, modele):
        return False

    # Vérifie que l'année est un entier dans une plage raisonnable
    if not (1900 <= annee <= 2100):
        return False

    return True

def get_dimensions_by_params(marque: str, modele: str, annee: int) -> List[Dict[str, Any]]:
    """
    Recherche les données dans la table DimensionsParModel en fonction des
    paramètres Marque, Modele et Annee.
    """
    # Valider les paramètres
    if not validate_dimensions_params(marque, modele, annee):
        raise HTTPException(
            status_code=400,
            detail="Invalid input parameters"
        )

    # Requête SQL sécurisée avec des paramètres
    query = """
    SELECT marque, modele, annee, finition, largeur, hauteur, diametre
    FROM DimensionsParModel
    WHERE LOWER(marque) = LOWER(?) AND LOWER(modele) = LOWER(?) AND annee = ?
    """

    with db.get_cursor() as cursor:
        try:
            cursor.execute(query, (marque, modele, annee))
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error")
