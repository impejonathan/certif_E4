from fastapi import APIRouter, Depends, HTTPException
from database.dimensions import get_dimensions_by_params
from database.auth import oauth2_scheme

router = APIRouter()

@router.get("/dimensions_for_modele_car")
async def get_dimensions(
    marque: str,
    modele: str,
    annee: int,
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint pour rechercher les informations dans la table DimensionsParModel.
    """
    # Nettoyage de base des entrées
    marque = marque.strip()
    modele = modele.strip()

    # Vérifications des entrées utilisateur
    if not marque or not modele or not annee:
        raise HTTPException(status_code=400, detail="All parameters (marque, modele, annee) are required.")
    if len(marque) > 50 or len(modele) > 50:
        raise HTTPException(status_code=400, detail="Marque or Modele too long.")

    try:
        results = get_dimensions_by_params(marque, modele, annee)
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
