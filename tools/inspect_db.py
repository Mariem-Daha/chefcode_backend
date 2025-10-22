import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'chefcode.db'

print(f"Opening DB: {DB_PATH}")
conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("\nTables:")
for t in tables:
    print(f" - {t}")

# Show schema for key tables and sample rows
for t in tables:
    print(f"\nSchema for {t}:")
    cur.execute(f"PRAGMA table_info('{t}')")
    cols = cur.fetchall()
    for c in cols:
        print(f"  - {c['name']} {c['type']} {'PK' if c['pk'] else ''}")
    
    print(f"\nTop 5 rows from {t}:")
    try:
        cur.execute(f"SELECT * FROM '{t}' LIMIT 5")
        rows = cur.fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"  <no rows or error: {e}>")

conn.close()
print("\nDone.")
