import re
import sqlite3
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

AFFILIATIONS_VALIDES = [
    'FTQ - Fédération des Travailleurs et Travailleuses du Québec',
    'CSN - Confédération des Syndicats Nationaux',
    'CSQ - Centrale des Syndicats du Québec',
    'CSD - Centrale des Syndicats Démocratiques',
    'IND PRO - Indépendant - Provincial',
    'IND NAT - Indépendant - National',
    'IND INT - Indépendant - International',
    'IND LOC - Indépendant - Local'
]

def insert_or_get_id(cursor, table, columns, values):
    placeholders = ', '.join(['?'] * len(values))
    cols = ', '.join(columns)
    cursor.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})", values)
    cursor.execute(
        f"SELECT id FROM {table} WHERE " + ' AND '.join([f"{col} = ?" for col in columns]), values
    )
    row = cursor.fetchone()
    return row[0] if row else None

def update_convention(conn, code_corail, data):
    cursor = conn.cursor()
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [code_corail]
    cursor.execute(f"UPDATE conventions SET {set_clause} WHERE code_corail = ?", values)
    conn.commit()

def process_html_file(path, conn):
    with open(path, encoding="ISO-8859-1") as f:
        soup = BeautifulSoup(f, "html.parser")

    divs = soup.find_all('div', class_='pl16')
    if not divs:
        print(f"⚠️ Aucun bloc trouvé dans {path.name}")
        return

    rows = divs[1].find_all("tr")
    for row in rows:
        h5 = row.find("div", class_="h5")
        h6s = row.find_all("div", class_="h6")
        if not h5 or len(h6s) < 2:
            continue

        nom_employeur = h5.get_text(" ").strip()
        nom_employeur = re.sub(r'\s*\([^)]*ko,\s*\d+\s*pages\)', '', nom_employeur)
        nom_employeur = re.sub(r'^(.*?)\s+\1$', r'\1', nom_employeur).strip()

        bloc1 = h6s[0].get_text("\n")
        bloc1_lines = [l.strip().strip(',') for l in bloc1.split('\n') if l.strip()]
        bloc1_joined = " ".join(bloc1_lines)

        region = ""
        match_region = re.search(r'\(([^()]+)\)', bloc1)
        if match_region:
            region = match_region.group(1).strip()

        match_code = re.search(r'id="div(\d+)"', str(row))
        code_corail = int(match_code.group(1)) if match_code else 0

        categorie = ""
        match_cat = re.search(r'\b(\d{4})\s*-\s*[^,]+', bloc1)
        if match_cat:
            categorie = match_cat.group(1)

        match_accr = re.search(r'\bA[A-Z]\d+\b', bloc1)
        num_accr = match_accr.group(0) if match_accr else ""

        match_sal = re.search(r'(\d+)\s+salari[eé]s?\s+vis[eé]s?', bloc1)
        nb_salaries = int(match_sal.group(1)) if match_sal else 0

        affiliation = ""
        for aff in AFFILIATIONS_VALIDES:
            if aff in bloc1:
                affiliation = aff
                break

        syndicat = bloc1
        for patt in [region, num_accr, affiliation, match_sal.group(0) if match_sal else ""]:
            if patt:
                syndicat = syndicat.replace(patt, "")
        if match_cat:
            syndicat = syndicat.replace(match_cat.group(0), "")
        syndicat = re.sub(r'\(\s*\)', '', syndicat)
        syndicat = re.sub(r'\s{2,}', ' ', syndicat).strip(" ,")

        bloc2 = h6s[1].get_text(" ").strip()
        date_sig = re.search(r'Date de signature\xa0: ([^,]+)', bloc2)
        date_exp = re.search(r'Expiration\xa0: ([^,]+)', bloc2)
        duree = re.search(r'(\d+) mois', bloc2)

        cursor = conn.cursor()

        if not syndicat:
            print(f"❌ Nom de syndicat manquant pour {num_accr} / {nom_employeur}")
            continue

        syn_id = insert_or_get_id(cursor, "syndicats_clean", ["nom", "affiliation"], [syndicat, affiliation])
        if syn_id is None:
            print(f"❌ Impossible d'insérer ou trouver le syndicat : {syndicat} ({affiliation})")
            continue

        if not num_accr:
            print(f"❌ Numéro d'accréditation manquant pour syndicat {syndicat}")
            continue

        acc_id = insert_or_get_id(cursor, "accreditations", ["num_accreditation", "syndicat_id"], [num_accr, syn_id])
        if acc_id is None:
            print(f"❌ Impossible d'insérer ou trouver l'accréditation : {num_accr} (syndicat ID: {syn_id})")
            continue

        update_convention(conn, code_corail, {
            "accreditation_id": acc_id,
            "date_signature": date_sig.group(1).strip() if date_sig else None,
            "date_expiration": date_exp.group(1).strip() if date_exp else None,
            "duree": int(duree.group(1)) if duree else None,
            "nb_salaries": nb_salaries,
            "region": region,
            "categorie": categorie,
            "employeur_nom": nom_employeur
        })

def parser_tous_les_fichiers():
    conn = sqlite3.connect("syndicats.db")
    base = Path("download")
    fichiers = base.rglob("*.html")
    for f in fichiers:
        print(f"🔍 Traitement de {f.relative_to(base)}")
        process_html_file(f, conn)
    conn.close()
    print("✅ Parser terminé.")

if __name__ == "__main__":
    parser_tous_les_fichiers()
