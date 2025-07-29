import sqlite3

DB_PATH = "syndicats.db"  # Change le nom si nécessaire
TABLE_NAME = "syndicats"  # Change si la table s'appelle autrement
ACCRED_FIELD = "num_accreditation"

def clean_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Compter les entrées à supprimer
    cursor.execute(f"""
        SELECT COUNT(*) FROM {TABLE_NAME}
        WHERE {ACCRED_FIELD} IS NULL OR TRIM({ACCRED_FIELD}) = ''
    """)
    count = cursor.fetchone()[0]

    # Supprimer les entrées
    cursor.execute(f"""
        DELETE FROM {TABLE_NAME}
        WHERE {ACCRED_FIELD} IS NULL OR TRIM({ACCRED_FIELD}) = ''
    """)
    conn.commit()

    print(f"{count} entrées supprimées (sans numéro d'accréditation).")
    conn.close()

if __name__ == "__main__":
    clean_db()
