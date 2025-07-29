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


def separer_blocs_syndicats(html):
    """
    Extrait les blocs syndicaux du HTML. Chaque bloc correspond à un syndicat.
    Retourne une liste de blocs HTML (chaque bloc est un objet BeautifulSoup).
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Supposons que chaque bloc est dans une <div> ou autre balise identifiable
    # Ici, on imagine que chaque bloc commence par un <table> avec un attribut ou un contenu spécifique
    tables = soup.find_all('table')  # à ajuster selon la structure réelle
    blocs = []

    for table in tables:
        # Heuristique simple : un bloc contient des mots-clés spécifiques ou un nombre de colonnes attendu
        if 'Syndicat' in table.text or 'Nom du syndicat' in table.text:
            blocs.append(table)

    return blocs

def parse_bloc(bloc):

    """
    Prend un bloc BeautifulSoup et retourne un dictionnaire correspondant à une entrée Corail.
    """
    texte = bloc.get_text(separator=' ', strip=True)

    # Exemples de champs typiques à extraire
    entree = {
        'no_entente': None,
        'employeur': None,
        'syndicat': None,
        'secteur': None,
        'date_entree_vigueur': None,
        'date_fin': None,
        'region': None,
        'lien_pdf': None
    }

    # Extraction simple (à améliorer selon structure)
    import re

    no_entente = re.search(r'Entente\s*:\s*(\d{6})', texte)
    if no_entente:
        entree['no_entente'] = no_entente.group(1)

    employeur = re.search(r'Employeur\s*:\s*(.+?)Syndicat', texte)
    if employeur:
        entree['employeur'] = employeur.group(1).strip()

    syndicat = re.search(r'Syndicat\s*:\s*(.+?)Secteur', texte)
    if syndicat:
        entree['syndicat'] = syndicat.group(1).strip()

    secteur = re.search(r'Secteur\s*:\s*(.+?)Date.*vigueur', texte)
    if secteur:
        entree['secteur'] = secteur.group(1).strip()

    date_debut = re.search(r'Date.*vigueur\s*:\s*(\d{2}/\d{2}/\d{4})', texte)
    if date_debut:
        entree['date_entree_vigueur'] = date_debut.group(1)

    date_fin = re.search(r'Fin.*:\s*(\d{2}/\d{2}/\d{4})', texte)
    if date_fin:
        entree['date_fin'] = date_fin.group(1)

    # Tu pourrais aussi extraire le lien PDF s'il est dans un <a href="..."> à l'intérieur du bloc
    lien = bloc.find('a', href=True)
    if lien:
        entree['lien_pdf'] = lien['href']

    # À personnaliser selon les cas
    return entree

def update_bdd(entree_corail, db_path='corail.db'):
    """
    Met à jour la base de données SQLite avec les infos extraites d'un bloc.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Assurons-nous que la table existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corail (
            no_entente TEXT PRIMARY KEY,
            employeur TEXT,
            syndicat TEXT,
            secteur TEXT,
            date_entree_vigueur TEXT,
            date_fin TEXT,
            region TEXT,
            lien_pdf TEXT
        )
    ''')

    # Upsert
    cursor.execute('''
        INSERT INTO corail (
            no_entente, employeur, syndicat, secteur,
            date_entree_vigueur, date_fin, region, lien_pdf
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(no_entente) DO UPDATE SET
            employeur=excluded.employeur,
            syndicat=excluded.syndicat,
            secteur=excluded.secteur,
            date_entree_vigueur=excluded.date_entree_vigueur,
            date_fin=excluded.date_fin,
            region=excluded.region,
            lien_pdf=excluded.lien_pdf
    ''', (
        entree_corail['no_entente'],
        entree_corail['employeur'],
        entree_corail['syndicat'],
        entree_corail['secteur'],
        entree_corail['date_entree_vigueur'],
        entree_corail['date_fin'],
        entree_corail['region'],
        entree_corail['lien_pdf']
    ))

    conn.commit()
    conn.close()

def parser_tous_les_fichiers():
    conn = sqlite3.connect("syndicats.db")
    base = Path("download")
    fichiers = base.rglob("*.html")
    for f in fichiers:
        print(f"🔍 Traitement de {f.relative_to(base)}")
        with open(f, encoding='latin1') as file:
            html = file.read()
            for b in separer_blocs_syndicats(html):
                entree = parse_bloc(b)
                if entree.get('no_entente'):  # petite sécurité pour éviter les lignes vides
                    update_bdd(entree)
    conn.close()
    print("✅ Parser terminé.")

if __name__ == "__main__":
    parser_tous_les_fichiers()
