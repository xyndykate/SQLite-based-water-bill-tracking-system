"""
Database utilities for SQLite Water Bill Tracking System
"""

import os
import sys
import shutil
from datetime import datetime
import logging

from database import db_manager

logger = logging.getLogger(__name__)

def check_database_status():
    """Check database connection and schema status."""
    print("🔍 Checking database status...")
    
    # Test connection
    try:
        if db_manager.test_connection():
            print("✅ Database connection: OK")
        else:
            print("❌ Database connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    # Check if tables exist
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = cursor.fetchall()
            
            if tables:
                print("✅ Database tables found:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("⚠️  No tables found. Run setup to initialize schema.")
            
            return len(tables) > 0
            
    except Exception as e:
        print(f"❌ Error checking database schema: {e}")
        return False

def initialize_schema():
    """Initialize the database schema."""
    try:
        if not os.path.exists('database_schema_sqlite.sql'):
            print("❌ Schema file 'database_schema_sqlite.sql' not found!")
            return False
        
        success = db_manager.initialize_database('database_schema_sqlite.sql')
        if success:
            print("✅ Database schema initialized successfully!")
        else:
            print("❌ Failed to initialize database schema!")
        
        return success
        
    except Exception as e:
        logger.error(f"Schema initialization failed: {e}")
        print(f"❌ Schema initialization failed: {e}")
        return False

def backup_database(backup_file: str = None):
    """Create a backup of the database."""
    try:
        if backup_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"water_bill_backup_{timestamp}.db"
        
        success = db_manager.backup_database(backup_file)
        if success:
            print(f"✅ Backup created successfully!")
        else:
            print("❌ Backup failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        print(f"❌ Backup failed: {e}")
        return False

def restore_database(backup_file: str):
    """Restore database from backup."""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"⚠️  This will restore the database from: {backup_file}")
    print("⚠️  All current data will be replaced!")
    confirm = input("Are you sure? (yes/no): ").lower()
    
    if confirm != 'yes':
        print("Restore cancelled.")
        return False
    
    try:
        # Close existing connection
        db_manager.disconnect()
        
        # Get database path
        db_path = db_manager.config.get_database_path()
        
        # Copy backup file over current database
        shutil.copy2(backup_file, db_path)
        
        print("✅ Database restored successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def setup_database():
    """Complete database setup process."""
    print("🚀 Setting up Water Bill Tracking Database (SQLite)...")
    print("="*60)
    
    # Initialize schema
    print("\n1️⃣ Initializing schema...")
    if not initialize_schema():
        return False
    
    # Check status
    print("\n2️⃣ Verifying setup...")
    if check_database_status():
        print("\n🎉 Database setup completed successfully!")
        print(f"\nDatabase location: {os.path.abspath(db_manager.config.get_database_path())}")
        print("\nYou can now run the application with: python main.py")
        return True
    else:
        print("\n❌ Setup verification failed!")
        return False

def main():
    """Main utility function."""
    if len(sys.argv) < 2:
        print("Database Utilities for SQLite Water Bill Tracking System")
        print("="*60)
        print("Usage: python db_utils.py <command>")
        print("\nCommands:")
        print("  setup     - Complete database setup")
        print("  check     - Check database status")
        print("  backup    - Create database backup")
        print("  restore   - Restore from backup")
        print("  schema    - Initialize schema only")
        print("\nExamples:")
        print("  python db_utils.py setup")
        print("  python db_utils.py backup")
        print("  python db_utils.py restore backups/water_bill_backup_20231006_143022.db")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        setup_database()
    
    elif command == 'check':
        check_database_status()
    
    elif command == 'backup':
        backup_file = sys.argv[2] if len(sys.argv) > 2 else None
        backup_database(backup_file)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Please specify backup file to restore from.")
            print("Usage: python db_utils.py restore <backup_file>")
        else:
            restore_database(sys.argv[2])
    
    elif command == 'schema':
        initialize_schema()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python db_utils.py' to see available commands.")

if __name__ == "__main__":
    main()