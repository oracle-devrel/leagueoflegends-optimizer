"""
Tests for the database module.
"""
import sqlite3
from unittest import mock

import pytest

from leagueoptimizer.data.database import (
    Database,
    DatabaseError,
    MockDatabase,
    SQLiteDatabase,
    get_database,
)


def test_mock_database():
    """Test the MockDatabase implementation."""
    db = MockDatabase()
    
    # Test connect and disconnect
    db.connect()
    assert db.connected is True
    db.disconnect()
    assert db.connected is False
    
    # Test create_table
    db.connect()
    db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
    assert "users" in db.tables
    
    # Test insert
    db.insert("users", {"id": 1, "name": "John"})
    db.insert("users", {"id": 2, "name": "Jane"})
    assert len(db.tables["users"]) == 2
    
    # Test fetch_one
    result = db.fetch_one("SELECT * FROM users WHERE id = 1")
    assert result == {"id": 1, "name": "John"}
    
    # Test fetch_all
    results = db.fetch_all("SELECT * FROM users")
    assert len(results) == 2
    assert results[0]["name"] == "John"
    assert results[1]["name"] == "Jane"
    
    # Test update
    db.update("users", {"name": "Johnny"}, "id = ?", (1,))
    result = db.fetch_one("SELECT * FROM users WHERE id = 1")
    assert result == {"id": 1, "name": "Johnny"}
    
    # Test delete
    db.delete("users", "id = ?", (1,))
    results = db.fetch_all("SELECT * FROM users")
    assert len(results) == 2  # Mock doesn't actually delete


def test_sqlite_database():
    """Test the SQLiteDatabase implementation with mocks."""
    # Mock sqlite3.connect
    mock_connection = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.row_factory = None
    
    with mock.patch("sqlite3.connect", return_value=mock_connection):
        db = SQLiteDatabase(":memory:")
        
        # Test connect
        db.connect()
        sqlite3.connect.assert_called_once_with(":memory:")
        assert db.connection is mock_connection
        assert db.cursor is mock_cursor
        
        # Test create_table
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        mock_cursor.execute.assert_called_with(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
        )
        
        # Test insert
        db.insert("users", {"id": 1, "name": "John"})
        mock_cursor.execute.assert_called_with(
            "INSERT INTO users (id, name) VALUES (?, ?)", (1, "John")
        )
        
        # Test disconnect
        db.disconnect()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


def test_get_database():
    """Test the get_database function."""
    # Test with mock database type
    with mock.patch("leagueoptimizer.data.database.CONFIG", {
        "database": {"type": "mock"}
    }):
        db = get_database()
        assert isinstance(db, MockDatabase)
    
    # Test with sqlite database type
    with mock.patch("leagueoptimizer.data.database.CONFIG", {
        "database": {"type": "sqlite", "sqlite_path": ":memory:"}
    }):
        db = get_database()
        assert isinstance(db, SQLiteDatabase)
        assert db.db_path == ":memory:"
    
    # Test with invalid database type
    with mock.patch("leagueoptimizer.data.database.CONFIG", {
        "database": {"type": "invalid"}
    }):
        with pytest.raises(ValueError):
            get_database() 