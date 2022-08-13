#!python3
from operator import truediv
import os, selenium, io
from pathlib import Path
from urllib.request import url2pathname

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, math
from bs4 import BeautifulSoup
#import corail_parser
#import ctypes

driver = webdriver.Chrome("chromedriver.exe")
url = 'https://www.corail.gouv.qc.ca/abonnement/acceder.do'


#initialise region dict
regions_dict = {}
regions_file = io.open('parsed-regions.txt', mode="r", encoding="utf-8")
with regions_file as file:
 for line in file:
    regions_dict[line.split(',')[0]] = line.split(',')[1][:-1]


#set date_range to search
date_range = ('2022', '2023', '2024', '2025', '2026', '2027', '2028')

def download(file, cat, date, page_numb):
    download_path = f'download\\{cat}\\{date}'
    file_name = f'\\{page_numb}.html'
    Path(download_path).mkdir(parents=True, exist_ok=True)
    full_path = download_path+file_name
    with open(full_path, 'wb+') as f:
        f.write(file.encode('Latin-1'))

def click_option(driver, value_to_click):
    for value in driver.find_element(By.NAME, "requete.region").find_elements(By.TAG_NAME, "option"):
        if value.get_attribute("value") == value_to_click:
            value.click()
    return True

def send_date(driver, date_to_send):
    expiration_field = driver.find_element(By.NAME, "requete.dateExpiration")
    expiration_field.send_keys(date_to_send)
    return True

def download_pages(driver, option, date):
    option = regions_dict.get(option)
    page_elem = driver.find_element(By.XPATH, '/html/body/form/div/div[1]/table/tbody/tr/td[2]')

    try:
        nb_pages = math.ceil(float(page_elem.text.split(" ")[-1])/5)
        print(f'Nous avons {nb_pages} pages à télécharger')
    except:
        nb_pages = 1
        print("une seule page")

    for page in range(nb_pages):
        download(driver.page_source, option, date, 'test'+str(page))
        driver.execute_script("post('rech-nxt');")
    return True

def get_categorie_name(key):
    return regions_dict.get(key)

#Main app loop
while True:
    start = time.time()
    driver.get(url)
    print(driver.title)
    
    #wait for user to solve captcha
    bienvenue = driver.title
    while driver.title == bienvenue:
        time.sleep(5)
    #elem = WebDriverWait(driver, 30).until(driver.title == "CORAIL - Accueil") 
    #This is a dummy element)
    

    url = 'https://www.corail.gouv.qc.ca/abonnement/docs/rechercher.do?type=1'
    driver.get(url)


    #time.sleep(1)

    #create options list to be referenched later
    all_options = []
    region_field = driver.find_element(By.NAME, "requete.region")
    for option in region_field.find_elements(By.TAG_NAME, "option"):
        all_options.append(option.get_attribute("value"))
    
    date_i = 0
    while date_i < len(date_range):
        
        option_i = 1
        while option_i < len(all_options):
            
            click_option(driver, all_options[option_i])
            
            expiration_field = driver.find_element(By.NAME, "requete.dateExpiration")
            expiration_field.send_keys(date_range[date_i])
            
            print(f'Recherche pour l\'année : {date_range[date_i]} et la catégorie {regions_dict.get(all_options[option_i])}')
            expiration_field.submit()
            time.sleep(1)
            
            #est-ce qu'on a un message d'erreur suite à la recherche
            try:
                info_elem = driver.find_element(By.XPATH, '/html/body/form/div/div[1]/div[3]/span')
                #ctypes.windll.user32.MessageBoxW(0, info_elem.get_attribute('innerHTML').strip().split(" ")[-1], "Your title", 1)
                #si c'est parce que trop de résultat, y aller mois par mois
                if info_elem.get_attribute('innerHTML').strip() == "Plus de 100 documents répondent à vos critères; affinez votre recherche.":
                    print("plus de 100 éléments")

                    #refaire la recherche mais pour chaque mois
                    for month in range(1,13):
                        driver.get(url)
                        date_with_month = date_range[date_i]+"-"+f"{month:02}"
                        click_option(driver, all_options[option_i])
                        send_date(driver, date_with_month)
                        print(f'Recherche pour l\'année : {date_with_month} et la catégorie {regions_dict.get(all_options[option_i])}')
                        driver.find_element(By.TAG_NAME, "input").submit()
                        download_pages(driver, all_options[option_i], date_with_month)

                #sinon on passe à la prochaine recherche, le message était qu'il n'y avait pas de résultat
            
            #si pas de message, on part le download
            except:
               download_pages(driver, all_options[option_i], date_range[date_i])

            option_i+=1
            driver.get(url)
        date_i+=1
    end = time.time()
    time = end-start
    print(f"La recherche a durée {time} secondes")
    driver.quit()
else:
    print("OVER")
