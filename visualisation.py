from flask import Flask, render_template, request
import sqlite3
import math

app = Flask(__name__)

@app.route("/")
def index():
    page = int(request.args.get("page", 1))
    par_page = 200
    offset = (page - 1) * par_page
    query = request.args.get("query", "").strip()

    conn = sqlite3.connect("syndicats.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT COUNT(*) FROM syndicats_clean
            WHERE nom LIKE ?
        """, (f"%{query}%",))
    else:
        cursor.execute("SELECT COUNT(*) FROM syndicats_clean")
    total_syndicats = cursor.fetchone()[0]
    nb_pages = math.ceil(total_syndicats / par_page)

    if query:
        cursor.execute("""
            SELECT s.id AS syndicat_id, s.nom AS nom_syndicat, s.affiliation
            FROM syndicats_clean s
            WHERE s.nom LIKE ?
            ORDER BY s.nom
            LIMIT ? OFFSET ?
        """, (f"%{query}%", par_page, offset))
    else:
        cursor.execute("""
            SELECT s.id AS syndicat_id, s.nom AS nom_syndicat, s.affiliation
            FROM syndicats_clean s
            ORDER BY s.nom
            LIMIT ? OFFSET ?
        """, (par_page, offset))

    syndicats = cursor.fetchall()

    data = []
    for syn in syndicats:
        cursor.execute("""
            SELECT a.num_accreditation, c.*
            FROM accreditations a
            JOIN conventions c ON c.accreditation_id = a.id
            WHERE a.syndicat_id = ?
            ORDER BY a.num_accreditation, c.date_expiration DESC
        """, (syn["syndicat_id"],))
        conventions = cursor.fetchall()

        regroupes = {}
        for c in conventions:
            key = c["num_accreditation"]
            regroupes.setdefault(key, []).append(c)

        data.append({
            "syndicat": syn["nom_syndicat"],
            "affiliation": syn["affiliation"],
            "accreditations": regroupes
        })

    conn.close()
    return render_template("index.html", data=data, page=page, nb_pages=nb_pages, query=query)


if __name__ == "__main__":
    app.run(debug=True)
