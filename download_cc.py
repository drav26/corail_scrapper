from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sqlite3
import shutil


CONVENTION_DIR = os.path.join(os.getcwd(), "conventions")
os.makedirs(CONVENTION_DIR, exist_ok=True)


def get_latest_csn_conventions():
    conn = sqlite3.connect("syndicats.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE syndicats ADD COLUMN fichier TEXT")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    try:
        cursor.execute("ALTER TABLE syndicats ADD COLUMN absent INTEGER")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    conn.commit()

    cursor.execute('''
        SELECT num_accreditation, date_expiration 
        FROM syndicats 
        WHERE affiliation LIKE 'CSN - Confédération des Syndicats Nationaux%' 
        AND (absent IS NULL OR absent != 1)
        AND fichier IS NULL
        ORDER BY date_expiration DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    seen = set()
    unique = []
    for num, date in rows:
        if num and num not in seen:
            unique.append((num, date))
            seen.add(num)
    return unique


def update_fichier_in_db(num_accreditation, filepath):
    conn = sqlite3.connect("syndicats.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE syndicats SET fichier = ?, absent = NULL WHERE num_accreditation = ?
    """, (filepath, num_accreditation))
    conn.commit()
    conn.close()


def mark_as_absent(num_accreditation):
    conn = sqlite3.connect("syndicats.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE syndicats SET absent = 1 WHERE num_accreditation = ?
    """, (num_accreditation,))
    conn.commit()
    conn.close()


def telecharger_conventions(numero_dossiers_dates):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    download_temp_dir = os.path.join(os.getcwd(), "temp_dl")
    os.makedirs(download_temp_dir, exist_ok=True)

    options.add_experimental_option("prefs", {
        "download.default_directory": download_temp_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Attente que l'utilisateur passe le CAPTCHA
        url = "https://www.corail.gouv.qc.ca/abonnement/acceder.do"
        driver.get(url)
        bienvenue = driver.title
        while driver.title == bienvenue:
            print("🔐 En attente de la résolution du CAPTCHA...")
            time.sleep(5)

        for numero, expiration in numero_dossiers_dates:
            print(f"\n🔎 Recherche du dossier : {numero}")
            driver.get("https://www.corail.gouv.qc.ca/abonnement/docs/rechercher.do?type=1")

            champ_recherche = driver.find_element(By.NAME, "requete.motsCles")
            champ_recherche.clear()
            champ_recherche.send_keys(numero)
            champ_recherche.send_keys(Keys.RETURN)

            time.sleep(2)
            # Vérifier s'il y a un message "précisez votre recherche"
            if "précisez votre recherche" in driver.page_source.lower():
                print(f"❌ Aucun résultat pour : {numero} — marqué comme absent")
                mark_as_absent(numero)
                continue

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@href, 'javascript:postDoc')]")))
                liens_js = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:postDoc')]")
                if liens_js:
                    lien = liens_js[0]  # télécharger seulement le plus récent
                    print(f"⬇️ Téléchargement de : {lien.get_attribute('href')}")
                    lien.click()
                    time.sleep(2)

                    # Attente du fichier PDF dans le dossier de téléchargement
                    pdf_file = None
                    for _ in range(10):
                        pdfs = [f for f in os.listdir(download_temp_dir) if f.endswith(".pdf")]
                        if pdfs:
                            pdf_file = pdfs[0]
                            break
                        time.sleep(1)

                    if pdf_file:
                        new_name = f"{numero}_{expiration}.pdf"
                        new_path = os.path.join(CONVENTION_DIR, new_name)
                        shutil.move(os.path.join(download_temp_dir, pdf_file), new_path)
                        update_fichier_in_db(numero, new_path)
                        print(f"✅ Fichier enregistré sous : {new_path}")
                    else:
                        print("⚠️ Aucun PDF détecté après le téléchargement.")
                else:
                    print("⚠️ Aucun lien trouvé pour ce dossier.")
            except Exception as e:
                print(f"❌ Erreur pendant la récupération du document : {e}")
                mark_as_absent(numero)

    finally:
        print("⏳ Nettoyage...")
        time.sleep(5)
        driver.quit()
        shutil.rmtree(download_temp_dir, ignore_errors=True)


if __name__ == "__main__":
    dossiers = get_latest_csn_conventions()
    if dossiers:
        print(f"✅ {len(dossiers)} dossiers CSN à télécharger")
        telecharger_conventions(dossiers)
    else:
        print("❌ Aucun dossier CSN trouvé dans la base de données.")