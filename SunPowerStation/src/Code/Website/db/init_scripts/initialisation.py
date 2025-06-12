import sqlite3
import os

db_filname = "temperatur.db"
db_folder = "SunPowerStation/src/Code/Website/db"

def create_user_db():
    """Erstellt eine SQLite-Datenbank für die Temperaturdaten."""
    db_path = os.path.join(db_folder, db_filname)

    # Stelle sicher, dass der Ordner existiert
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Datenbank und Tabelle erstellen
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS temperatur (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Datum TEXT NOT NULL,
                Uhrzeit TEXT NOT NULL,
                Temperatur REAL NOT NULL
                  )
        ''')
        conn.commit()
        print(f"Datenbank erstellt unter: {db_path}")

if __name__ == "__main__":
    create_user_db()