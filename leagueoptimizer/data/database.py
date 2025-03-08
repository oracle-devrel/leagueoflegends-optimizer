"""
Database abstraction layer for the League Optimizer.

This module provides a unified interface for different database backends.
"""
import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import oracledb

from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import data_logger as logger


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class Database(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """Execute a query with optional parameters."""
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database."""
        pass
    
    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a row into the database."""
        pass
    
    @abstractmethod
    def update(self, table: str, data: Dict[str, Any], condition: str, params: Tuple[Any, ...]) -> int:
        """Update rows in the database."""
        pass
    
    @abstractmethod
    def delete(self, table: str, condition: str, params: Tuple[Any, ...]) -> int:
        """Delete rows from the database."""
        pass
    
    @abstractmethod
    def create_table(self, table: str, columns: Dict[str, str]) -> None:
        """Create a table if it doesn't exist."""
        pass


class OracleDatabase(Database):
    """Oracle database implementation."""
    
    def __init__(self, username: str, password: str, dsn: str):
        """Initialize the Oracle database connection."""
        self.username = username
        self.password = password
        self.dsn = dsn
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        """Establish a connection to the Oracle database."""
        try:
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn,
                thick_mode=True
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to Oracle database")
        except oracledb.Error as e:
            logger.error(f"Oracle database connection error: {e}")
            raise DatabaseError(f"Failed to connect to Oracle database: {e}")
    
    def disconnect(self) -> None:
        """Close the Oracle database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Oracle database")
    
    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """Execute a query with optional parameters."""
        try:
            if params:
                result = self.cursor.execute(query, params)
            else:
                result = self.cursor.execute(query)
            self.connection.commit()
            return result
        except oracledb.Error as e:
            self.connection.rollback()
            logger.error(f"Oracle database execution error: {e}")
            raise DatabaseError(f"Failed to execute query: {e}")
    
    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        try:
            self.execute(query, params)
            columns = [col[0].lower() for col in self.cursor.description]
            row = self.cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None
        except oracledb.Error as e:
            logger.error(f"Oracle database fetch error: {e}")
            raise DatabaseError(f"Failed to fetch data: {e}")
    
    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database."""
        try:
            self.execute(query, params)
            columns = [col[0].lower() for col in self.cursor.description]
            rows = self.cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except oracledb.Error as e:
            logger.error(f"Oracle database fetch error: {e}")
            raise DatabaseError(f"Failed to fetch data: {e}")
    
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a row into the database."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{i+1}" for i in range(len(data))])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute(query, tuple(data.values()))
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: Tuple[Any, ...]) -> int:
        """Update rows in the database."""
        set_clause = ", ".join([f"{k} = :{i+1}" for i, k in enumerate(data.keys())])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute(query, tuple(data.values()) + params)
        return self.cursor.rowcount
    
    def delete(self, table: str, condition: str, params: Tuple[Any, ...]) -> int:
        """Delete rows from the database."""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute(query, params)
        return self.cursor.rowcount
    
    def create_table(self, table: str, columns: Dict[str, str]) -> None:
        """Create a table if it doesn't exist."""
        column_defs = ", ".join([f"{k} {v}" for k, v in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})"
        self.execute(query)


class SQLiteDatabase(Database):
    """SQLite database implementation."""
    
    def __init__(self, db_path: str):
        """Initialize the SQLite database connection."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to SQLite database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"SQLite database connection error: {e}")
            raise DatabaseError(f"Failed to connect to SQLite database: {e}")
    
    def disconnect(self) -> None:
        """Close the SQLite database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from SQLite database")
    
    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """Execute a query with optional parameters."""
        try:
            if params:
                result = self.cursor.execute(query, params)
            else:
                result = self.cursor.execute(query)
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"SQLite database execution error: {e}")
            raise DatabaseError(f"Failed to execute query: {e}")
    
    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        try:
            self.execute(query, params)
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            logger.error(f"SQLite database fetch error: {e}")
            raise DatabaseError(f"Failed to fetch data: {e}")
    
    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database."""
        try:
            self.execute(query, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"SQLite database fetch error: {e}")
            raise DatabaseError(f"Failed to fetch data: {e}")
    
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a row into the database."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in range(len(data))])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute(query, tuple(data.values()))
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: Tuple[Any, ...]) -> int:
        """Update rows in the database."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute(query, tuple(data.values()) + params)
        return self.cursor.rowcount
    
    def delete(self, table: str, condition: str, params: Tuple[Any, ...]) -> int:
        """Delete rows from the database."""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute(query, params)
        return self.cursor.rowcount
    
    def create_table(self, table: str, columns: Dict[str, str]) -> None:
        """Create a table if it doesn't exist."""
        column_defs = ", ".join([f"{k} {v}" for k, v in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})"
        self.execute(query)


class MockDatabase(Database):
    """Mock database implementation for testing."""
    
    def __init__(self):
        """Initialize the mock database."""
        self.tables = {}
        self.connected = False
        logger.info("Initialized mock database")
    
    def connect(self) -> None:
        """Establish a connection to the mock database."""
        self.connected = True
        logger.info("Connected to mock database")
    
    def disconnect(self) -> None:
        """Close the mock database connection."""
        self.connected = False
        logger.info("Disconnected from mock database")
    
    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """Execute a query with optional parameters."""
        logger.debug(f"Mock execute: {query} with params {params}")
        return None
    
    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        logger.debug(f"Mock fetch_one: {query} with params {params}")
        for table_name, table_data in self.tables.items():
            if table_name in query.lower():
                if table_data:
                    return table_data[0]
        return None
    
    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database."""
        logger.debug(f"Mock fetch_all: {query} with params {params}")
        for table_name, table_data in self.tables.items():
            if table_name in query.lower():
                return table_data
        return []
    
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a row into the database."""
        if table not in self.tables:
            self.tables[table] = []
        self.tables[table].append(data)
        logger.debug(f"Mock insert into {table}: {data}")
        return None
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: Tuple[Any, ...]) -> int:
        """Update rows in the database."""
        logger.debug(f"Mock update {table}: {data} where {condition} with params {params}")
        return 1
    
    def delete(self, table: str, condition: str, params: Tuple[Any, ...]) -> int:
        """Delete rows from the database."""
        logger.debug(f"Mock delete from {table} where {condition} with params {params}")
        return 1
    
    def create_table(self, table: str, columns: Dict[str, str]) -> None:
        """Create a table if it doesn't exist."""
        if table not in self.tables:
            self.tables[table] = []
        logger.debug(f"Mock create table {table} with columns {columns}")


def get_database() -> Database:
    """
    Get a database instance based on configuration.
    
    Returns:
        A database instance
    """
    db_config = CONFIG["database"]
    db_type = db_config["type"].lower()
    
    if db_type == "oracle":
        return OracleDatabase(
            username=db_config["username"],
            password=db_config["password"],
            dsn=db_config["dsn"]
        )
    elif db_type == "sqlite":
        return SQLiteDatabase(db_path=db_config["sqlite_path"])
    elif db_type == "mock":
        return MockDatabase()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# Singleton database instance
db = get_database() 