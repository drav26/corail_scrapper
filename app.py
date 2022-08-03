#!python3
from operator import truediv
import os, selenium, io
from pathlib import Path
from urllib.request import url2pathname
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import corail_parser

PATH = "chromedriver.exe"
driver = webdriver.Chrome(PATH)
url = 'https://www.corail.gouv.qc.ca/abonnement/acceder.do'

def Syndicat():
    def __init__():
        print("init")
regions = []
regions_file = io.open('parsed-regions.txt', mode="r", encoding="utf-8")
with regions_file as file:
 for line in file:
    regions.append(line)

date_range = ('2022', '2023', '2024', '2025', '2026')

while True:
    driver.get(url)
    print(driver.title)
    time.sleep(10)
    #wait for user to solve captcha

    url = 'https://www.corail.gouv.qc.ca/abonnement/docs/rechercher.do?type=1'
    driver.get(url)
    region_field = driver.find_element(By.NAME, "requete.region")
    expiration_field = driver.find_element(By.NAME, "requete.dateExpiration")
    time.sleep(1)
    all_options = region_field.find_elements(By.TAG_NAME, "option")
    for date in date_range:
        for option in all_options:
            if option.get_attribute("value") != '-1':
                option.click()
                expiration_field.send_keys(date)
                region_field.submit()
                time.sleep(10)
                corail_parser.parse_results_page(driver.page_source)
                






    driver.quit()
else:
    print("OVER")
