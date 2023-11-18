#!python3
from operator import truediv
import os, selenium, io
from pathlib import Path, WindowsPath
from urllib.request import url2pathname
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup 
import pprint, re, datetime

class Syndicat:

    def __init__(self):
        self.nom =""
        self.num_accreditation=""
        self.region =""
        self.categorie =""
        self.nb_salaries = 0
        self.date_signature = None
        self.date_expiration = None
        self.affiliation =""
        self.code_corail = 0
        self.duree = 0

    def print(self):
        print('name : '+self.nom)
        print('region : '+self.region)
        print('categorie : '+self.categorie)
        print('nb_salaries : '+self.nb_salaries)
        print('num_accreditation : '+self.num_accreditation)
        print('date_signature : '+self.date_signature)
        print('date_expiration : '+self.date_expiration)
        print('duree : '+self.duree)
        #print('affiliation : '+affiliation[:-1])
        #print('code_corail : '+str(codes_corail[iteration]))
        print('code_corail :'+str(self.code_corail))

syndicats =[]

html = open(Path('html-test.html'))
html_raw = html.read()
soup = BeautifulSoup(html_raw)
divs = soup.find_all('div', {'class', 'pl16'})
i=0
ii=0
print("START".ljust(100,"="))

code_corail_re = re.compile(r'id="div([\d]+)"')
codes_corail = code_corail_re.findall(html_raw)

    
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
#print(cell_list)
pprint.pprint(cell_list)
iteration = 0 #??
for code_corail in codes_corail:
    print('traitons maintenant le code corail :'+str(code_corail))
    
    syndicat = Syndicat()
    
    #split_cell = cell_list[2+(4*iteration)].split('\n')
    
    #for lignes in split_cell:
    #   print("nouvelle ligne : "+lignes.lstrip())

    
    syndicat.nom = cell_list[1+(4*iteration)].split("\n")[1]

    regionre = re.compile(r'(\()(.+)(\))')
    syndicat.region = regionre.search(cell_list[2+(4*iteration)]).group(2)

    categorie_re = re.compile(r'\d{4}')
    syndicat.categorie = categorie_re.search(cell_list[2+(4*iteration)]).group()

    nb_salaries_re = re.compile(r'([\d]+) salariés visés')
    syndicat.nb_salaries = nb_salaries_re.search(cell_list[2+(4*iteration)]).group(1)

    #affiliation = split_cell[5].lstrip()
    #affiliation_re = re.compile(r'.+,.+,.+,(.+),')
    #affiliation = affiliation_re.search(cell_list[2+(4*iteration)]).group(1)

    accreditation_re = re.compile(r'(AM[\d]+)')
    syndicat.num_accreditation = accreditation_re.search(cell_list[2+(4*iteration)]).group(1)

    #split_cell = cell_list[3].split('\n')

    date__signature_re = re.compile(r'(Date de signature\xa0: )(.+)(,)')
    syndicat.date_signature = date__signature_re.search(cell_list[3+(4*iteration)]).group(2).strip()

    date_expiration_re = re.compile(r"(Expiration\xa0: )(.+)(,)")
    syndicat.date_expiration = date_expiration_re.search(cell_list[3+(4*iteration)]).group(2).strip()

    duree_re = re.compile(r'( \d+)( mois)')
    syndicat.duree = duree_re.search(cell_list[3+(4*iteration)]).group(1).strip()
    syndicat.code_corail = code_corail
    
    iteration+=1
    syndicats.append(syndicat)
  

for syndicat in syndicats:
    syndicat.print()
    ##dump un DB


#for i in range (5):

# split_cell = cell_list[2].split('\n')

# name = cell_list[1].split("\n")[1]

# regionre = re.compile(r'(\()(.+)(\))')
# region = regionre.search(cell_list[2]).group(2)

# categorie_re = re.compile(r'\d{4}')
# categorie = categorie_re.search(cell_list[2]).group()

# nb_salaries_re = re.compile(r'(\d+)(.+)')
# nb_salaries = nb_salaries_re.search(split_cell[7]).group(1)

# affiliation = split_cell[5].lstrip()

# num_accreditation = split_cell[6].lstrip()

# split_cell = cell_list[3].split('\n')

# date_re = re.compile(r'(: )(.+)(,)')
# date_signature = date_re.search(split_cell[2]).group(2).strip()
# date_expiration = date_re.search(split_cell[3]).group(2).strip()
# duree_re = re.compile(r'( \d+)( mois)')
# duree = duree_re.search(split_cell[4]).group(1).strip()






    # table = div.find('table')
    # for row in table.findAll("tr"):
    #     for cell in row.findAll("td"):
    #         print(cell.text)