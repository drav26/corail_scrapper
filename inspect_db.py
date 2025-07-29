import sqlite3

def inspect_db(db_path="syndicats.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\n🔍 Inspection de la base de données : {db_path}\n")

    # Liste les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        print("❌ Aucune table trouvée.")
        return

    for table in tables:
        print(f"📌 Table : {table}")

        # Colonnes de la table
        cursor.execute(f"PRAGMA table_info({table})")
        colonnes = cursor.fetchall()
        for col in colonnes:
            print(f"   - {col[1]} ({col[2]}){' [PK]' if col[5] else ''}")

        # Nombre de lignes
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            nb_lignes = cursor.fetchone()[0]
            print(f"   → {nb_lignes} lignes\n")
        except:
            print("   ⚠️ Impossible de compter les lignes (vue ou table complexe)\n")

    conn.close()

if __name__ == "__main__":
    inspect_db()
