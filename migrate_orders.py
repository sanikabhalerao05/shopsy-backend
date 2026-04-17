import sqlite3
import os

db_path = 'shopsyhub.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR DEFAULT 'Not Specified'")
        conn.commit()
        print("Migration successful: added payment_method to orders")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists, skipping.")
        else:
            print(f"Migration error: {e}")
    finally:
        conn.close()
else:
    print("Database not found")
