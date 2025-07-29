from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def telecharger_conventions(numero_dossier):
    # Initialiser le navigateur
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),  # Télécharger dans le répertoire actuel
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Accéder au site
        url = "https://www.corail.gouv.qc.ca:443/abonnement/docs/rechercher.do"
        driver.get(url)
        
        # Attendre que l'utilisateur résolve le CAPTCHA
        bienvenue = driver.title
        while driver.title == bienvenue:
            print("En attente de la résolution du CAPTCHA...")
            time.sleep(5)
        
        # Trouver le champ de recherche et entrer le numéro de dossier
        champ_recherche = driver.find_element(By.NAME, "requete.motsCles")
        champ_recherche.send_keys(numero_dossier)
        champ_recherche.send_keys(Keys.RETURN)
        
        time.sleep(5)  # Attendre que la page se charge
        
        # Trouver les liens vers les fichiers PDF et les télécharger
        liens_pdfs = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        for lien in liens_pdfs:
            pdf_url = lien.get_attribute("href")
            print(f"Téléchargement : {pdf_url}")
            driver.get(pdf_url)
        
        time.sleep(10)  # Attendre la fin des téléchargements
    
    finally:
        driver.quit()

# Exemple d'utilisation
numero_dossier = "123456"  # Remplacez par le numéro de dossier réel
telecharger_conventions(numero_dossier)
