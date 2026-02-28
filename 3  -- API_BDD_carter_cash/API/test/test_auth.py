import pytest
import re
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from jose import jwt, JWTError
from database.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_user, create_user, SECRET_KEY, ALGORITHM
)
from models import User, UserCreate, PasswordChange
from datetime import timedelta, datetime

def test_password_hashing():
    # Test cas standard
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
    
    # Test avec des caractères spéciaux
    special_password = "P@ssw0rd!#$%"
    special_hashed = get_password_hash(special_password)
    assert verify_password(special_password, special_hashed)
    assert not verify_password(password, special_hashed)
    
    # Test avec password vide (edge case)
    empty_password = ""
    empty_hashed = get_password_hash(empty_password)
    assert verify_password(empty_password, empty_hashed)

def test_token_creation():
    # Test cas standard
    data = {"sub": "test_user"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Décodage du token pour vérifier les claims
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "test_user"
    assert "exp" in payload
    
    # Test avec expires_delta None (utilise la valeur par défaut)
    token_default = create_access_token(data)
    assert isinstance(token_default, str)
    
    # Test avec données supplémentaires
    complex_data = {"sub": "test_user", "roles": ["admin", "user"], "email": "test@example.com"}
    complex_token = create_access_token(complex_data, expires_delta=timedelta(minutes=60))
    complex_payload = jwt.decode(complex_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert complex_payload["sub"] == "test_user"
    assert complex_payload["roles"] == ["admin", "user"]
    assert complex_payload["email"] == "test@example.com"

@patch('database.auth.db.get_cursor')
def test_get_user(mock_get_cursor):
    # Setup du mock
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = MagicMock(
        username="testuser", 
        email="test@example.com", 
        full_name="Test User", 
        hashed_password="hashedpassword123"
    )
    mock_get_cursor.return_value.__enter__.return_value = mock_cursor
    
    # Test récupération utilisateur
    user = get_user("testuser")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password == "hashedpassword123"
    
    # Vérification que la requête SQL a été appelée avec les bons paramètres
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT username, email, full_name, hashed_password" in call_args[0]
    assert call_args[1] == ("testuser",)
    
    # Test utilisateur inexistant
    mock_cursor.fetchone.return_value = None
    user = get_user("nonexistent")
    assert user is None

@patch('database.auth.db.get_cursor')
@patch('database.auth.get_password_hash')
def test_create_user(mock_get_password_hash, mock_get_cursor):
    # Setup des mocks
    mock_get_password_hash.return_value = "hashed_test_password"
    mock_cursor = MagicMock()
    mock_get_cursor.return_value.__enter__.return_value = mock_cursor
    
    # Créer un utilisateur valide
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        full_name="New User",
        password="password123"
    )
    
    user = create_user(user_data)
    
    # Vérifier que les fonctions ont été appelées correctement
    mock_get_password_hash.assert_called_once_with("password123")
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO USER_API" in call_args[0]
    assert call_args[1][0] == "newuser"
    assert call_args[1][1] == "new@example.com"
    assert call_args[1][2] == "New User"
    assert call_args[1][3] == "hashed_test_password"
    
    # Simuler une erreur d'intégrité (utilisateur déjà existant)
    import pyodbc
    mock_cursor.execute.side_effect = pyodbc.IntegrityError("Username already exists")
    
    with pytest.raises(HTTPException) as excinfo:
        create_user(user_data)
    
    assert excinfo.value.status_code == 400
    assert "Username already registered" in excinfo.value.detail

def test_register_user(test_client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword"
    }
    
    # Test enregistrement normal
    response = test_client.post("/register", json=user_data)
    assert response.status_code in [200, 400]  # 400 si l'utilisateur existe déjà
    
    if response.status_code == 200:
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data  # Le mot de passe ne doit pas être renvoyé
    
    # Test avec données invalides
    invalid_data = {
        "username": "",  # username vide
        "email": "invalid-email",  # email invalide
        "full_name": "Test User",
        "password": "pw"  # mot de passe trop court
    }
    response = test_client.post("/register", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_login(test_client):
    # Test login valide
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = test_client.post("/token", data=login_data)
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Validations supplémentaires sur le token
        try:
            payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
            assert "sub" in payload
            assert payload["sub"] == login_data["username"]
        except JWTError:
            pytest.fail("Le token généré n'est pas valide")
    
    # Test avec identifiants invalides
    invalid_login = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = test_client.post("/token", data=invalid_login)
    assert response.status_code == 401
    
    # Test avec des données manquantes
    incomplete_login = {
        "username": "testuser"
        # password manquant
    }
    response = test_client.post("/token", data=incomplete_login)
    assert response.status_code in [422, 401]  # 422 pour validation error

def test_change_password(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test cas normal
    valid_data = {
        "current_password": "testpassword",
        "new_password": "newpassword",
        "confirm_password": "newpassword"
    }
    response = test_client.put("/users/me/password", json=valid_data, headers=headers)
    assert response.status_code in [200, 401, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert "Password updated successfully" in data["message"]
    
    # Test avec nouveau mot de passe différent de confirmation
    mismatch_data = {
        "current_password": "testpassword",
        "new_password": "newpassword1",
        "confirm_password": "newpassword2"
    }
    response = test_client.put("/users/me/password", json=mismatch_data, headers=headers)
    assert response.status_code == 400
    
    # Test sans token d'authentification
    response = test_client.put("/users/me/password", json=valid_data)
    assert response.status_code == 401
    
    # Test avec données invalides
    invalid_data = {
        "current_password": "short",
        "new_password": "pw",  # Trop court
        "confirm_password": "pw"
    }
    response = test_client.put("/users/me/password", json=invalid_data, headers=headers)
    assert response.status_code in [422, 400]  # 422 pour validation error
