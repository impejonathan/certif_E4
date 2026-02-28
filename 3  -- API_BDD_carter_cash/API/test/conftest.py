import pytest
from fastapi.testclient import TestClient
from main import app
from database.db_connection import DatabaseConnection
from unittest.mock import MagicMock, patch

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    with patch('database.db_connection.DatabaseConnection') as mock:
        db_instance = MagicMock()
        mock.return_value = db_instance
        yield db_instance

@pytest.fixture
def test_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example_test_token"
