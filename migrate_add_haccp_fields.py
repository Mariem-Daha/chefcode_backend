"""
Database migration script to add HACCP traceability fields
Adds lot_number and expiry_date columns to inventory_items table
"""

import sqlite3
from pathlib import Path

def migrate_database():
    # Connect to the database
    db_path = Path(__file__).parent / "chefcode.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(inventory_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add lot_number if it doesn't exist
        if 'lot_number' not in columns:
            print("Adding lot_number column...")
            cursor.execute("ALTER TABLE inventory_items ADD COLUMN lot_number TEXT")
            print("[OK] lot_number column added")
        else:
            print("[OK] lot_number column already exists")
        
        # Add expiry_date if it doesn't exist
        if 'expiry_date' not in columns:
            print("Adding expiry_date column...")
            cursor.execute("ALTER TABLE inventory_items ADD COLUMN expiry_date DATE")
            print("[OK] expiry_date column added")
        else:
            print("[OK] expiry_date column already exists")
        
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Migration error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("HACCP Traceability Migration")
    print("Adding lot_number and expiry_date to inventory_items")
    print("=" * 60)
    migrate_database()

