#!python3
import os, io, time, math
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Charger les régions depuis le fichier
regions_dict = {}
with io.open('parsed-regions.txt', mode="r", encoding="utf-8") as file:
    for line in file:
        regions_dict[line.split(',')[0]] = line.split(',')[1].strip()

# Demander à l'utilisateur les années à télécharger
date_range_input = input("Entrez les années à télécharger, séparées par des virgules (ex: 2022,2023): ")
date_range = [year.strip() for year in date_range_input.split(',') if year.strip().isdigit()]

# Initialiser le navigateur
url = 'https://www.corail.gouv.qc.ca/abonnement/acceder.do'
driver = webdriver.Chrome()
driver.get(url)

# Attente que l'utilisateur résolve le captcha
print("Veuillez résoudre le captcha sur le site Web...")
bienvenue = driver.title
while driver.title == bienvenue:
    time.sleep(5)

url_recherche = 'https://www.corail.gouv.qc.ca/abonnement/docs/rechercher.do?type=1'

def download(file, cat, date, page_numb):
    download_path = f'download/{cat}/{date}'
    file_name = f'/{date}_page{page_numb}.html'
    Path(download_path).mkdir(parents=True, exist_ok=True)
    full_path = download_path + file_name
    with open(full_path, 'wb+') as f:
        f.write(file.encode('Latin-1'))

def click_option(driver, value_to_click):
    for value in driver.find_element(By.NAME, "requete.region").find_elements(By.TAG_NAME, "option"):
        if value.get_attribute("value") == value_to_click:
            value.click()
            break

def send_date(driver, date_to_send):
    expiration_field = driver.find_element(By.NAME, "requete.dateExpiration")
    expiration_field.clear()
    expiration_field.send_keys(date_to_send)

def download_pages(driver, option, date):
    option_label = regions_dict.get(option, "Unknown")
    try:
        page_elem = driver.find_element(By.XPATH, '/html/body/form/div/div[1]/table/tbody/tr/td[2]')
        nb_pages = math.ceil(float(page_elem.text.split(" ")[-1])/5)
        print(f'{nb_pages} pages à télécharger pour {option_label} en {date}')
    except:
        nb_pages = 1
        print(f"Une seule page pour {option_label} en {date}")

    for page in range(nb_pages):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except:
            print("⏳ Timeout : la page n'a pas pu être validée avant le téléchargement.")

        html = driver.page_source
        if not html.strip().endswith('</html>'):
            print("⚠️ HTML incomplet détecté")
        download(html, option_label, date, page + 1)
        try:
            driver.execute_script("post('rech-nxt');")
        except:
            print("Impossible de passer à la page suivante.")
            break

def main():
    driver.get(url_recherche)
    all_options = []
    region_field = driver.find_element(By.NAME, "requete.region")
    for option in region_field.find_elements(By.TAG_NAME, "option"):
        all_options.append(option.get_attribute("value"))

    for date in date_range:
        for option in all_options[1:]:
            if option not in regions_dict:
                continue

            click_option(driver, option)
            send_date(driver, date)
            print(f'Recherche pour {date} dans la catégorie {regions_dict.get(option)}')
            driver.find_element(By.TAG_NAME, "input").submit()
            time.sleep(1)

            try:
                info_elem = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/for2m/div/div[1]/div[3]/span'))
                )
                if "Plus de 100 documents" in info_elem.get_attribute('innerHTML'):
                    print("Plus de 100 documents. Raffinement par mois...")
                    for month in range(1, 13):
                        driver.get(url_recherche)
                        date_with_month = f"{date}-{month:02}"
                        click_option(driver, option)
                        send_date(driver, date_with_month)
                        driver.find_element(By.TAG_NAME, "input").submit()
                        download_pages(driver, option, date_with_month)
                else:
                    print("Pas de message de surcharge. Téléchargement normal.")
                    download_pages(driver, option, date)
            except:
                print("Aucun message de surcharge détecté, on télécharge normalement.")
                download_pages(driver, option, date)

            driver.get(url_recherche)

    print("Téléchargement terminé.")
    driver.quit()

if __name__ == '__main__':
    main()
