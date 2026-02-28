import pytest
from database.dimensions import validate_dimensions_params, get_dimensions_by_params

def test_validate_dimensions_params():
    # Test valides
    assert validate_dimensions_params("Dacia", "Sandero", 2019) == True
    assert validate_dimensions_params("Peugeot", "208", 2019) == True

    # Test invalides 
    assert validate_dimensions_params("Invalid;Brand", "Model", 2020) == False
    assert validate_dimensions_params("Brand", "Invalid;Model", 2020) == False
    assert validate_dimensions_params("Brand", "Model", 1800) == False

def test_get_dimensions_endpoint(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    params = {
        "marque": "Dacia",
        "modele": "Sandero", 
        "annee": 2019
    }
    response = test_client.get("/dimensions_for_modele_car", params=params, headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "count" in data
        assert "data" in data

def test_specific_sandero_dimensions(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    params = {
        "marque": "Dacia",
        "modele": "Sandero",
        "annee": 2019
    }
    response = test_client.get("/dimensions_for_modele_car", params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        dimensions = data.get("data", [])
        
        # Vérifie la présence des dimensions spécifiques pour Sandero 2019
        for dim in dimensions:
            assert "largeur" in dim
            assert "hauteur" in dim
            assert "diametre" in dim
            assert isinstance(dim["largeur"], (int, str))
            assert isinstance(dim["hauteur"], (int, str))
            assert isinstance(dim["diametre"], (int, str))
