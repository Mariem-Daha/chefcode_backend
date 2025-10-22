"""
Database Migration: Add Web Recipe Fields
Adds new columns to the recipes table to support web recipe imports
Run this script once to update the database schema
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "chefcode.db"

def migrate():
    """Add new columns to recipes table for web recipe support"""
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("   Run the main application first to create the database.")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("[*] Starting migration: Adding web recipe fields...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(recipes)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = [
            ("source_url", "TEXT"),
            ("image_url", "TEXT"),
            ("cuisine", "TEXT"),
            ("ingredients_raw", "TEXT"),
            ("ingredients_mapped", "TEXT")
        ]
        
        added_count = 0
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE recipes ADD COLUMN {col_name} {col_type}")
                print(f"   [OK] Added column: {col_name}")
                added_count += 1
            else:
                print(f"   [SKIP] Column already exists: {col_name}")
        
        conn.commit()
        
        if added_count > 0:
            print(f"\n[SUCCESS] Migration completed successfully! Added {added_count} column(s).")
        else:
            print(f"\n[SUCCESS] Migration completed - no changes needed (all columns already exist).")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {str(e)}")
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("DATABASE MIGRATION: Add Web Recipe Fields")
    print("=" * 70)
    print()
    
    success = migrate()
    
    print()
    if success:
        print("[SUCCESS] You can now use the Web Recipe Search feature!")
    else:
        print("[WARNING] Migration failed. Please check the errors above.")
    print()

