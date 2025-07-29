import sqlite3

def afficher_syndicats():
    conn = sqlite3.connect("syndicats.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, affiliation FROM syndicats_clean ORDER BY nom")
    rows = cursor.fetchall()

    print(f"\n📋 {len(rows)} syndicats trouvés :\n")
    for row in rows:
        id_, nom, affiliation = row
        print(f"- {nom or '(aucun nom)'} | {affiliation or '(aucune affiliation)'}")

    conn.close()

if __name__ == "__main__":
    afficher_syndicats()
