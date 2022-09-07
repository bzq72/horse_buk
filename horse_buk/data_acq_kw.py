"""Contain methods for acquisition data from koniewyscigowe.pl"""
from pathlib import Path
from genericpath import exists
import urllib.request, urllib.error, urllib.parse
from selenium import webdriver
import db_insert
import db_creation as db
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind = db.engine)

class data_acq_kw():
    def get_horse_page(self, name):
        self.url_horse = f"https://koniewyscigowe.pl/horse/szukaj?search={name}"
        options = webdriver.ChromeOptions() 
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\48725\AppData\Local\Programs\Python\Python310\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe')
        driver.get(self.url_horse)
        try: WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "section.g-py-50")))
        except: return
        content = driver.page_source.encode('utf-8')
        with open (f"horse_page_{name}.txt","wb") as horse_page:
            horse_page.write(content)
       
    def get_horse_data(self, name):
        query = db.Horses.name == name
        if db_insert.is_exist(db.Horses,query): return
        if name in ["_",""," "]:return
        self.get_horse_page(name)
        horse_name = None
        horse_gender = None
        horse_brith_date = None
        horse_breed = None
        horse_origin = None
        horse_father_ID = None
        horse_mother_ID = None
        horse_trainer_ID = None
        horse_owner_ID = None
        horse_stable_ID = None
        size = None
        path_to_file = f'horse_page_{name}.txt'
        path = Path(path_to_file)
        if path.is_file():
            with open(f"horse_page_{name}.txt","r",encoding="utf-8") as horse_page:    
                page = BeautifulSoup(horse_page,"html.parser")
                horse_name = str(page.h1.string)
                info = page.find("tbody").find_all("tr")
                main_horse_info = info[0].strong.string.split()
                try: horse_coat, horse_gender, horse_brith_date = main_horse_info[0], main_horse_info[1], main_horse_info[3]
                except: 
                    horse_brith_date = None
                    try: horse_coat, horse_gender = main_horse_info[0], main_horse_info[1]
                    except:
                        horse_gender = None
                        try: horse_coat = main_horse_info[0]
                        except: horse_coat = None


                for pair in info[1:]:
                    column, value = pair.find("th").string, pair.find("td").string
                    if value in ["-",' ','\n']: continue
                    if not value: value = pair.td.a.string
                    if column == "Rasa:": horse_breed = value
                    elif column == "Pochodzenie:": horse_origin = value
                    elif column == "Trener:": 
                            try: value = value.split()
                            except: continue
                            session = Session()
                            try: 
                                query = session.query(db.Trainers.ID).filter(db.Trainers.surname == str(value[1])).first()
                                horse_trainer_ID = query[0]
                            except:
                                db_insert.insert_trainer(trainer_name=str(value[0]), trainer_surname=str(value[1]))
                                query = session.query(db.Trainers.ID).filter(db.Trainers.surname == str(value[1])).first()
                                horse_trainer_ID = query[0]
                            
                    elif column == "Właściciel:": 
                            session = Session()
                            try: 
                                query = session.query(db.Owners.ID).filter(db.Owners.name == str(value)).first()
                                horse_owner_ID = query[0]
                            except:
                                db_insert.insert_owner(owner_name=str(value))
                                query = session.query(db.Owners.ID).filter(db.Owners.name == str(value)[:20]).first()
                                horse_owner_ID = query[0]
                                
                    elif column == "Stajnia:": 
                            session = Session()
                            try: 
                                query = session.query(db.Stables.ID).filter(db.Stables.name == str(value).strip()).first()
                                horse_stable_ID = query[0]
                            except:
                                db_insert.insert_stable(stable_name=str(value).strip(), stable_adress=None)
                                query = session.query(db.Stables.ID).filter(db.Stables.name == str(value).strip()).first()
                                horse_stable_ID = query[0] 
                                                
                    elif column == "Wymiary:": 
                        size = value
                    elif column == "Ojciec:": 
                        query = (db.Horses.name == str(value))
                        if db_insert.is_exist(db.Horses,query):
                            session = Session()
                            horse_father_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                        else: 
                            self.get_horse_data(value)
                            session = Session()
                            try: horse_father_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                            except: horse_father_ID = None
                            
                    elif column   == "Matka:":
                        query = (db.Horses.name == str(value))
                        if db_insert.is_exist(db.Horses,query):
                            session = Session()
                            horse_mother_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                        else: 
                            self.get_horse_data(value)
                            session = Session()
                            try: horse_mother_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                            except: horse_mother_ID = None
                            
                db_insert.insert_horse(horse_name = horse_name, horse_gender = horse_gender, horse_brith_date = horse_brith_date
                                    , horse_coat = horse_coat, horse_breed = horse_breed, horse_origin = horse_origin
                                    , horse_father_ID = horse_father_ID, horse_mother_ID = horse_mother_ID
                                    , horse_trainer_ID = horse_trainer_ID, horse_owner_ID = horse_owner_ID
                                    , horse_stable_ID = horse_stable_ID, horse_size = size)
        #except: return
            os.remove(f"horse_page_{name}.txt")
 
 
#checker = data_acq_kw()
#checker.get_horse_data("Abadan")
"""session = Session()
ask = session.query(db.Horses.ID).filter(db.Horses.name == "Hilal Muscat").first()[0]
print(ask)
"""
# https://koniewyscigowe.pl/horse/12892-abadan