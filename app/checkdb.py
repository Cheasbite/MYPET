import os
import sqlite3

root_path = os.path.abspath(os.path.curdir)

record_db_dir = os.path.join(root_path, "db", "record.db")
db_path = os.path.dirname(record_db_dir)

# Create files if not exists yet
def check_db_exists():
    if not os.path.exists(db_path): os.makedirs(db_path)
    if not os.path.exists(record_db_dir):
        con = sqlite3.connect(record_db_dir)

        try:
            cursor = con.cursor()

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        expense REAL NOT NULL,
                        frequency TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

            con.commit()

        except sqlite3.Error as e:
            print(f"Error while working with sqlite. {e}")

        finally:
            if con: con.close()

def check_db_has_values() -> bool:
    con = None
    try:
        # only read and write
        con = sqlite3.connect(record_db_dir, uri=True)
        cursor = con.cursor()

        cursor.execute("SELECT * FROM Records ORDER BY id ASC LIMIT 1.")

        value = cursor.fetchone()

        print(value)

        if value: return True

        return False

    except sqlite3.Error as e:
        print(f"Error while checking sqlite has values. Did you create it? {e}")
        return False
    finally:
        if con is not None: con.close()

