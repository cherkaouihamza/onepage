import sqlite3
from datetime import datetime
from pathlib import Path
#import comtypes.client
#import comtypes

DB_PATH = Path("ppt_uploads.db")

# Initialiser la base de données
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Créer la table si elle n'existe pas
c.execute("""
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    folder_name TEXT NOT NULL,
    filename TEXT NOT NULL,
    upload_date TEXT NOT NULL
)
""")

conn.commit()
conn.close()


# Fonction d'enregistrement
def record_ppt_upload(username, folder_name, filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO uploads (username, folder_name, filename, upload_date)
        VALUES (?, ?, ?, ?)
    """, (username, folder_name, filename, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Fonction de récupération de l'historique
def get_user_uploads(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT folder_name, filename, upload_date FROM uploads
        WHERE username = ? ORDER BY upload_date DESC LIMIT 50
    """, (username,))
    results = c.fetchall()
    conn.close()
    return results
