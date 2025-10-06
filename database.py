"""
Database configuration and connection management for SQLite
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, Any, Optional
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables should be set manually
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self):
        self.database_path = os.getenv('DB_PATH', 'water_bill.db')
        self.backup_dir = os.getenv('BACKUP_DIR', 'backups')
        
    def get_database_path(self) -> str:
        """Get the database file path."""
        return self.database_path

class DatabaseManager:
    """Database connection and transaction management."""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._connection = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection."""
        try:
            if self._connection is None:
                self._connection = sqlite3.connect(
                    self.config.get_database_path(),
                    check_same_thread=False
                )
                # Enable foreign key constraints
                self._connection.execute("PRAGMA foreign_keys = ON")
                # Set row factory for dict-like access
                self._connection.row_factory = sqlite3.Row
                logger.info("Database connection established")
            return self._connection
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """Context manager for database cursor with automatic transaction management."""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a query and optionally fetch results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def initialize_database(self, schema_file: str = 'database_schema_sqlite.sql'):
        """Initialize database with schema from SQL file."""
        try:
            if not os.path.exists(schema_file):
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split and execute statements (SQLite doesn't support executescript with parameters)
            with self.get_cursor() as cursor:
                cursor.executescript(schema_sql)
            
            logger.info("Database schema initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def backup_database(self, backup_file: str = None) -> bool:
        """Create a backup of the database."""
        import shutil
        from datetime import datetime
        
        try:
            if backup_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"water_bill_backup_{timestamp}.db"
            
            # Ensure backup directory exists
            backup_dir = self.config.backup_dir
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_path = os.path.join(backup_dir, backup_file)
            source_path = self.config.get_database_path()
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, backup_path)
                logger.info(f"Database backup created: {backup_path}")
                return True
            else:
                logger.error(f"Source database not found: {source_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

# Create a global database manager instance
db_manager = DatabaseManager()