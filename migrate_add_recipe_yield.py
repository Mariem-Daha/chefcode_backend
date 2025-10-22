#!/usr/bin/env python3
"""
Migration Script: Add yield_data column to recipes table
Run this script once to update existing database with yield_data field
"""

import sqlite3
import os

def migrate():
    db_path = "chefcode.db"
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'yield_data' in columns:
            print("[OK] Column 'yield_data' already exists in recipes table")
            return True
        
        # Add yield_data column
        print("[INFO] Adding 'yield_data' column to recipes table...")
        cursor.execute("""
            ALTER TABLE recipes 
            ADD COLUMN yield_data TEXT
        """)
        
        conn.commit()
        print("[SUCCESS] Migration successful! yield_data column added to recipes table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"[INFO] Current columns in recipes table: {', '.join(columns)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Recipe Yield Data Migration")
    print("=" * 60)
    success = migrate()
    print("=" * 60)
    if success:
        print("[SUCCESS] Migration completed successfully!")
        print("You can now save and retrieve recipe yield data.")
    else:
        print("[ERROR] Migration failed. Please check the error messages above.")
    print("=" * 60)

