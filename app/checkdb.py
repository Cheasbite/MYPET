import os
import sqlite3

root_path = os.path.abspath(os.path.curdir)

record_db_dir = os.path.join(root_path, "db", "record.db")
db_path = os.path.dirname(record_db_dir)

# Create files if not exists yet
def check_db_exists():
    if not os.path.exists(db_path): os.makedirs(db_path)
    if not os.path.exists(record_db_dir):
        with open(record_db_dir, 'w') as f:
            f.write("")

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
                if con:
                    con.close()

