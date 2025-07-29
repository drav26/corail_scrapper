import re
from bs4 import BeautifulSoup
from pathlib import Path

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

def parser_test_visuel(path):
    print(f"\n🔍 Test du fichier : {path}")
    with open(path, encoding="ISO-8859-1") as f:
        soup = BeautifulSoup(f, "html.parser")

    lignes = soup.find_all('tr')
    for row in lignes:
        h5 = row.find("div", class_="h5")
        h6s = row.find_all("div", class_="h6")
        if not h5 or len(h6s) < 2:
            continue

        # Employeur
        employeur = h5.get_text(" ").strip()
        employeur = re.sub(r'\s*\([^)]*ko,\s*\d+\s*pages\)', '', employeur)
        employeur = re.sub(r'^(.*?)\s+\1$', r'\1', employeur).strip()

        # Bloc 1
        bloc1 = h6s[0].get_text("\n")
        bloc1_lines = [l.strip().strip(',') for l in bloc1.split('\n') if l.strip()]
        bloc1_joined = " ".join(bloc1_lines)

        # Région
        region = ""
        match_region = re.search(r'\(([^()]+)\)', bloc1)
        if match_region:
            region = match_region.group(1).strip()

        # Code corail
        match_code = re.search(r'id="div(\d+)"', str(row))
        code_corail = int(match_code.group(1)) if match_code else 0

        # Catégorie
        categorie = ""
        match_cat = re.search(r'\b(\d{4})\s*-\s*[^,]+', bloc1)
        if match_cat:
            categorie = match_cat.group(1)

        # Accréditation
        match_accr = re.search(r'\bA[A-Z]\d+\b', bloc1)
        acc = match_accr.group(0) if match_accr else ""

        # Nb salariés
        match_sal = re.search(r'(\d+)\s+salari[eé]s?\s+vis[eé]s?', bloc1)
        nb_salaries = int(match_sal.group(1)) if match_sal else 0

        # Affiliation
        affiliation = ""
        for aff in AFFILIATIONS_VALIDES:
            if aff in bloc1:
                affiliation = aff
                break

        # Nettoyage du syndicat
        syndicat = bloc1
        for patt in [region, acc, affiliation, match_sal.group(0) if match_sal else ""]:
            if patt:
                syndicat = syndicat.replace(patt, "")
        if match_cat:
            syndicat = syndicat.replace(match_cat.group(0), "")
        syndicat = re.sub(r'\(\s*\)', '', syndicat)
        syndicat = re.sub(r'\s{2,}', ' ', syndicat).strip(" ,")

        # Bloc 2 (dates)
        bloc2 = h6s[1].get_text(" ")
        date_sig = re.search(r'Date de signature\xa0: ([^,]+)', bloc2)
        date_exp = re.search(r'Expiration\xa0: ([^,]+)', bloc2)
        duree = re.search(r'(\d+) mois', bloc2)

        print("\n--- Convention trouvée ---")
        print(f"Code Corail     : {code_corail}")
        print(f"Employeur       : {employeur}")
        print(f"Syndicat        : {syndicat}")
        print(f"Affiliation     : {affiliation}")
        print(f"Num Accréditation: {acc}")
        print(f"Région          : {region}")
        print(f"Catégorie       : {categorie}")
        print(f"Salariés        : {nb_salaries}")
        print(f"Signature       : {date_sig.group(1) if date_sig else ''}")
        print(f"Expiration      : {date_exp.group(1) if date_exp else ''}")
        print(f"Durée           : {duree.group(1) if duree else ''} mois")

if __name__ == "__main__":
    parser_test_visuel(Path("test2.htm"))
