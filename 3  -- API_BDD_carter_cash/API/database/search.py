# search.py
from .db_connection import db
from fastapi import HTTPException
from typing import List, Dict, Any
import re
# search.py
def validate_marque(marque: str) -> bool:
    """Valide que la marque ne contient que des caractères autorisés"""
    # Liste de mots-clés SQL interdits
    sql_keywords = [
        'SELECT', 'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 
        'INSERT', 'TABLE', 'DATABASE', 'UNION', 'ALTER'
    ]
    
    # Vérifie si la marque contient des mots-clés SQL
    if any(keyword in marque.upper() for keyword in sql_keywords):
        return False
    
    # Regex pour n'autoriser que les caractères valides
    pattern = r'^[a-zA-Z0-9\s\-_.]+$'
    return bool(re.match(pattern, marque))

def get_data_from_db(marque: str) -> List[Dict[str, Any]]:
    # Validation renforcée des entrées
    if not validate_marque(marque):
        raise HTTPException(
            status_code=400,
            detail="Invalid or suspicious brand name detected"
        )
    
    # Log des tentatives suspectes avec plus de détails
    suspicious_patterns = ['SELECT', 'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 
                         'INSERT', 'TABLE', 'DATABASE', 'UNION', 'ALTER']
    if any(pattern in marque.upper() for pattern in suspicious_patterns):
        print(f"WARNING: Blocked SQL injection attempt - Input: {marque}")
        raise HTTPException(
            status_code=400,
            detail="Suspicious input detected"
        )

    query = """
    SELECT ID_Produit, URL_Produit, Prix, Info_generale, 
           Descriptif, Note, Marque, Date_scrap
    FROM Produit 
    WHERE Marque = ?
    """
    
    with db.get_cursor() as cursor:
        try:
            cursor.execute(query, (marque,))
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return {
                "success": True,
                "count": len(results),
                "data": results
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your request"
            )
