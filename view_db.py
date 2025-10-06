#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite Database Viewer
Quick utility to explore the water_bill.db database
"""

import sqlite3
import os
from datetime import datetime

def view_database(db_path='water_bill.db'):
    """View all data in the SQLite database."""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print("\n" + "="*70)
    print("🔍 SQLite Database Viewer - water_bill.db")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Found {len(tables)} tables: {', '.join(tables)}")
    
    # View each table
    for table in tables:
        print("\n" + "="*70)
        print(f"📋 Table: {table}")
        print("="*70)
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        print(f"Columns: {', '.join(col_names)}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Rows: {count}")
        
        # Show data
        if count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 10")
            rows = cursor.fetchall()
            
            print("\nData (first 10 rows):")
            print("-"*70)
            
            # Print header
            print("  ".join(f"{col:<15}" for col in col_names))
            print("-"*70)
            
            # Print rows
            for row in rows:
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str) and len(val) > 15:
                        values.append(val[:12] + "...")
                    else:
                        values.append(str(val))
                print("  ".join(f"{val:<15}" for val in values))
        else:
            print("(Empty table)")
    
    # Show views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = [row[0] for row in cursor.fetchall()]
    
    if views:
        print("\n" + "="*70)
        print(f"👁️  Views: {', '.join(views)}")
        print("="*70)
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Database exploration complete!")
    print("="*70 + "\n")

def interactive_query():
    """Run custom SQL queries interactively."""
    db_path = 'water_bill.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print("\n🔍 Interactive SQL Query Mode")
    print("="*60)
    print("Enter SQL queries (or 'exit' to quit)")
    print("Example: SELECT * FROM tenants;")
    print("="*60 + "\n")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    while True:
        query = input("SQL> ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query:
            continue
        
        try:
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                rows = cursor.fetchall()
                if rows:
                    # Print header
                    columns = rows[0].keys()
                    print("\n" + " | ".join(columns))
                    print("-" * (len(columns) * 20))
                    
                    # Print rows
                    for row in rows:
                        print(" | ".join(str(row[col]) for col in columns))
                    print(f"\n({len(rows)} rows)\n")
                else:
                    print("(No results)\n")
            else:
                conn.commit()
                print(f"✅ Query executed. Rows affected: {cursor.rowcount}\n")
        
        except sqlite3.Error as e:
            print(f"❌ Error: {e}\n")
    
    conn.close()
    print("👋 Goodbye!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'query':
        interactive_query()
    else:
        view_database()
        
        print("\n💡 Tips:")
        print("   - Run 'python view_db.py query' for interactive SQL mode")
        print("   - Use DB Browser for SQLite for a GUI experience")
        print("   - Run 'python main.py' to see system status")
