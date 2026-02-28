import pytest
from database.search import validate_marque, get_data_from_db

def test_validate_marque():
    # Test valides
    assert validate_marque("Michelin") == True
    assert validate_marque("Good-Year") == True

    # Test invalides
    assert validate_marque("DROP TABLE") == False
    assert validate_marque("SELECT *") == False
    assert validate_marque("'; DELETE FROM") == False

def test_search_endpoint(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test recherche valide
    response = test_client.get("/search/Michelin", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "count" in data
    assert "data" in data

    # Test recherche avec marque invalide
    response = test_client.get("/search/DROP%20TABLE", headers=headers)
    assert response.status_code == 400

def test_search_without_auth(test_client):
    response = test_client.get("/search/Michelin")
    assert response.status_code == 401
