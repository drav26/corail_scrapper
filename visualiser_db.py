import sqlite3

def afficher_syndicats():
    conn = sqlite3.connect("syndicats.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM syndicats ORDER BY date_expiration DESC")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print("="*60)
        for key in row.keys():
            print(f"{key}: {row[key]}")
        print()

if __name__ == "__main__":
    afficher_syndicats()
