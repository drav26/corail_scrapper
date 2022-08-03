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
import pprint, re

html = open(Path('html-test.html'))
soup = BeautifulSoup(html)
divs = soup.find_all('div', {'class', 'pl16'})
i=0
ii=0
print("START".ljust(100,"="))
cell_list = []
for div in divs:
    if i > 0 :
        table = div.find('table')
        for row in table.find_all("tr"):
            for cell in row.find_all('td'):
                for div in cell.find_all('div'):
                #or string in cell.stripped_strings:
                    ii+=1
                    cell_list.append(str(ii)+div.get_text())
    i+=1
print(cell_list)
pprint.pprint(cell_list)

#for i in range (5):

split_cell = cell_list[2].split('\n')

name = cell_list[1].split("\n")[1]

regionre = re.compile(r'(\()(.+)(\))')
region = regionre.search(cell_list[2]).group(2)

categorie_re = re.compile(r'\d{4}')
categorie = categorie_re.search(cell_list[2]).group()

nb_salaries_re = re.compile(r'(\d+)(.+)')
nb_salaries = nb_salaries_re.search(split_cell[7]).group(1)

num_accreditation = split_cell[6].lstrip()

split_cell = cell_list[3].split('\n')

date_re = re.compile(r'(: )(.+)(,)')
date_signature = date_re.search(split_cell[2]).group(2).strip()
date_expiration = date_re.search(split_cell[3]).group(2).strip()
duree_re = re.compile(r'( \d+)( mois)')
duree = duree_re.search(split_cell[4]).group(1).strip()


print('name : '+name)
print('region : '+region)
print('categorie : '+categorie)
print('nb_salaries : '+nb_salaries)
print('num_accreditation : '+num_accreditation)
print('date_signature : '+date_signature)
print('date_expiration : '+date_expiration)
print('duree : '+duree)

for lignes in split_cell:
    print("nouvelle ligne : "+lignes.lstrip())

    # table = div.find('table')
    # for row in table.findAll("tr"):
    #     for cell in row.findAll("td"):
    #         print(cell.text)