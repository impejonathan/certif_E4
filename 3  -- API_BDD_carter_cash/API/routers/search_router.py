# search_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from database.search import get_data_from_db
from database.auth import oauth2_scheme

router = APIRouter()
# search_router.py
@router.get("/search/{marque}")
async def read_data(
    marque: str,
    token: str = Depends(oauth2_scheme)
):
    # Nettoyage de base des entrées
    marque = marque.strip()
    
    # Vérifications de base
    if not marque:
        raise HTTPException(
            status_code=400,
            detail="Brand name cannot be empty"
        )
    
    if len(marque) > 50:
        raise HTTPException(
            status_code=400,
            detail="Brand name too long"
        )

    try:
        return get_data_from_db(marque)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )
