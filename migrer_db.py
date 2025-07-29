import sqlite3
import shutil
from pathlib import Path

def migrer_base_vers_structure_relationnelle(old_db="syndicats.db"):
    # Backup
    backup_path = Path(old_db).with_stem(Path(old_db).stem + "_backup")
    shutil.copy(old_db, backup_path)
    print(f"✅ Copie de sauvegarde créée : {backup_path}")

    conn = sqlite3.connect(old_db)
    cursor = conn.cursor()

    # Créer les nouvelles tables
    cursor.executescript("""
    DROP TABLE IF EXISTS conventions;
    DROP TABLE IF EXISTS accreditations;
    DROP TABLE IF EXISTS syndicats_clean;
    DROP TABLE IF EXISTS employeurs;

    CREATE TABLE employeurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE
    );

    CREATE TABLE syndicats_clean (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        affiliation TEXT,
        UNIQUE(nom, affiliation)
    );

    CREATE TABLE accreditations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_accreditation TEXT UNIQUE,
        syndicat_id INTEGER,
        FOREIGN KEY (syndicat_id) REFERENCES syndicats_clean(id)
    );

    CREATE TABLE conventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accreditation_id INTEGER,
        date_signature TEXT,
        date_expiration TEXT,
        duree INTEGER,
        nb_salaries INTEGER,
        region TEXT,
        categorie TEXT,
        code_corail INTEGER UNIQUE,
        fichier TEXT,
        absent INTEGER,
        employeur_nom TEXT,
        FOREIGN KEY (accreditation_id) REFERENCES accreditations(id)
    );
    """)

    # Récupérer les anciennes données
    cursor.execute("SELECT * FROM syndicats")
    lignes = cursor.fetchall()
    colonnes = [col[0] for col in cursor.description]
    idx = {k: i for i, k in enumerate(colonnes)}

    for ligne in lignes:
        try:
            nom_emp = (ligne[idx['nom']] or '').strip()
            nom_syn = (ligne[idx['syndicat']] or '').strip()
            aff_syn = (ligne[idx['affiliation']] or '').strip()
            num_accr = (ligne[idx['num_accreditation']] or '').strip()

            # ignorer les entrées sans num_accreditation
            if not num_accr:
                continue

            # insérer syndicat
            cursor.execute("INSERT OR IGNORE INTO syndicats_clean(nom, affiliation) VALUES (?, ?)", (nom_syn, aff_syn))
            cursor.execute("SELECT id FROM syndicats_clean WHERE nom = ? AND affiliation = ?", (nom_syn, aff_syn))
            syn_id = cursor.fetchone()[0]

            # insérer accréditation
            cursor.execute("INSERT OR IGNORE INTO accreditations(num_accreditation, syndicat_id) VALUES (?, ?)",
                           (num_accr, syn_id))
            cursor.execute("SELECT id FROM accreditations WHERE num_accreditation = ?", (num_accr,))
            acc_id = cursor.fetchone()[0]

            # insérer convention avec nom d'employeur associé à cette version
            cursor.execute("""
                INSERT OR IGNORE INTO conventions (
                    accreditation_id, date_signature, date_expiration, duree, nb_salaries,
                    region, categorie, code_corail, fichier, absent, employeur_nom
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                acc_id,
                ligne[idx['date_signature']],
                ligne[idx['date_expiration']],
                ligne[idx['duree']],
                ligne[idx['nb_salaries']],
                ligne[idx['region']],
                ligne[idx['categorie']],
                ligne[idx['code_corail']],
                ligne[idx['fichier']],
                ligne[idx['absent']],
                nom_emp
            ))
        except Exception as e:
            print(f"❌ Erreur lors du traitement de la ligne : {ligne}\n{e}")

    conn.commit()
    conn.close()
    print("✅ Migration terminée.")

if __name__ == "__main__":
    migrer_base_vers_structure_relationnelle()