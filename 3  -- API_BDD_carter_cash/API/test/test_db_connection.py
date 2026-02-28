import pytest
import os
import pyodbc
from unittest.mock import patch, MagicMock
from database.db_connection import DatabaseConnection
from contextlib import contextmanager

def test_db_connection_initialization():
    # Configuration des variables d'environnement pour le test
    with patch.dict(os.environ, {
        'DB_SERVER': 'test_server',
        'DB_DATABASE': 'test_db',
        'DB_USERNAME': 'test_user',
        'DB_PASSWORD': 'test_password'
    }):
        db = DatabaseConnection()
        
        # Vérifier que les valeurs sont chargées correctement
        assert db.server == 'test_server'
        assert db.database == 'test_db'
        assert db.username == 'test_user'
        assert db.password == 'test_password'
        assert db.driver == '{ODBC Driver 17 for SQL Server}'
        
        # Vérifier que la chaîne de connexion est correctement formée
        expected_connection_string = (
            f'DRIVER={db.driver};'
            f'SERVER=test_server;'
            f'DATABASE=test_db;'
            f'UID=test_user;'
            f'PWD=test_password'
        )
        assert db.connection_string == expected_connection_string

@pytest.mark.parametrize("env_vars,expected", [
    # Test avec toutes les variables définies
    ({
        'DB_SERVER': 'server1',
        'DB_DATABASE': 'db1',
        'DB_USERNAME': 'user1',
        'DB_PASSWORD': 'pass1'
    }, 'SERVER=server1;DATABASE=db1;UID=user1;PWD=pass1'),
    
    # Test avec des valeurs particulières (caractères spéciaux)
    ({
        'DB_SERVER': 'server-123',
        'DB_DATABASE': 'db_test;',  # caractère spécial ;
        'DB_USERNAME': 'user@domain',
        'DB_PASSWORD': 'p@$$w0rd!'
    }, 'SERVER=server-123;DATABASE=db_test;;UID=user@domain;PWD=p@$$w0rd!')
])
def test_db_connection_with_different_values(env_vars, expected):
    with patch.dict(os.environ, env_vars):
        db = DatabaseConnection()
        for key, value in env_vars.items():
            env_var_name = key.split('_')[1].lower()
            assert getattr(db, env_var_name) == value
        
        for part in expected.split(';'):
            if part:  # Ignore empty parts
                assert part in db.connection_string

@patch('pyodbc.connect')
def test_get_cursor_success(mock_connect):
    # Setup des mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Test du gestionnaire de contexte avec succès
    db = DatabaseConnection()
    with db.get_cursor() as cursor:
        assert cursor is mock_cursor
        cursor.execute("SELECT 1")
    
    # Vérifications des appels
    mock_connect.assert_called_once_with(db.connection_string)
    mock_conn.cursor.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('pyodbc.connect')
def test_get_cursor_with_exception(mock_connect):
    # Setup des mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simuler une exception pendant l'exécution
    mock_cursor.execute.side_effect = Exception("Database error")
    
    # Test du gestionnaire de contexte avec exception
    db = DatabaseConnection()
    with pytest.raises(Exception) as excinfo:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1")
    
    assert "Database error" in str(excinfo.value)
    
    # Vérifier que le rollback est appelé et que les ressources sont fermées
    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@pytest.mark.integration
@patch('pyodbc.connect')
def test_real_database_query(mock_connect):
    # Setup pour simuler une vraie requête à la base de données
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simuler le résultat d'une requête
    mock_cursor.fetchone.return_value = [1]
    
    db = DatabaseConnection()
    with db.get_cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    
    # Vérification des appels
    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_cursor.fetchone.assert_called_once()
