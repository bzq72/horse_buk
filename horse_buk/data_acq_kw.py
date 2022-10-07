"""Contain methods for acquisition data from koniewyscigowe.pl"""
from pathlib import Path
from selenium import webdriver
import db_insert
import db_creation as db
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind = db.engine)

class Data_Acq_kw():
    def find_right_horse(self, name, search_page):
        """selecting right horses href from few serching results"""
        href = None
        with open (f"searcher.txt","wb") as searcher: searcher.write(search_page)
        with open (f"searcher.txt","rb") as searcher:
            page = BeautifulSoup(searcher,"html.parser")
            pageee = str(page.header).lower()
            info = page.find("tbody").find_all("tr")
            last_year = year = 0
            for value in info:
                try: year = int(value.find_all("td")[2].string[-4:])
                except: year = 0
                if not href: href = value.find('a', href=True)['href']
                if last_year < year:
                    last_year = year
                    href = value.find('a', href=True)['href']
        self.get_horse_data(name, href)
        
    
    def get_horse_page(self, name, parent_href = None):
        """getting horse page"""
        if not parent_href: self.url_horse = f"https://koniewyscigowe.pl/horse/szukaj?search={name}"
        else: 
            self.url_horse = f"https://koniewyscigowe.pl{parent_href}"
        options = webdriver.ChromeOptions() 
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\48725\AppData\Local\Programs\Python\Python310\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe')
        driver.get(self.url_horse)
        try: WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "section.g-py-50")))
        except: 
            s_results = driver.page_source.encode('utf-8')
            hrefs = f'a href="/horse'.encode("utf-8")
            if not hrefs in s_results: return
            else:
                self.find_right_horse(name,s_results)
                return
        content = driver.page_source.encode('utf-8')
        pageee = str(content)
        counter = pageee.count(name)
        if counter > 6: return
        with open (f"horse_page_{name}.txt","wb") as horse_page:
            horse_page.write(content)
       
    def get_horse_data(self, name, href_parent = None):
        """getting informations about horses: name, gender, broth date, breed, origin, parents etc.
        and putting them into database"""
        if "'oa'" in name.lower(): name = name[0:-1]
        if "'" in name: name = name.replace("'","''")
        query = db.Horses.name == name
        if db_insert.is_exist(db.Horses,query): 
            return
        if name in ["_",""," "]:
            return
        self.get_horse_page(name, href_parent)
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
        horse_coat = None
        size = None
        path_to_file = f'horse_page_{name}.txt'
        path = Path(path_to_file)
        if path.is_file():
            with open(f"horse_page_{name}.txt","r",encoding="utf-8") as horse_page:    
                page = BeautifulSoup(horse_page,"html.parser")
                horse_name = str(page.h1.string)
                info = page.find("tbody").find_all("tr")
                main_horse_info = info[0].strong.string.lower().split()
                horse_coat_types = ["gnida","gniady","kasztanowata","kasztanowaty","siwa","siwy", "ciemnogniada", "ciemnogniady"]
                horse_gender_types = ["klacz","ogier","walach"]
                for i_info in main_horse_info:
                    if i_info in horse_coat_types: horse_coat = i_info
                    elif i_info in horse_gender_types: horse_gender = i_info
                    else: 
                        try: horse_brith_date = datetime.strptime(i_info, "%d.%m.%Y")
                        except: 
                                try: horse_brith_date = datetime.strptime(i_info, "%Y")
                                except: pass

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
                                try:    
                                    db_insert.insert_trainer(trainer_name=str(value[0]), trainer_surname=str(value[1]))
                                    query = session.query(db.Trainers.ID).filter(db.Trainers.surname == str(value[1])).first()
                                    horse_trainer_ID = query[0]
                                except: breakpoint()
                            
                    elif column == "Właściciel:": 
                            session = Session()
                            try: 
                                query = session.query(db.Owners.ID).filter(db.Owners.name == str(value)).first()
                                horse_owner_ID = query[0]
                            except:
                                db_insert.insert_owner(owner_name=str(value))
                                query = session.query(db.Owners.ID).filter(db.Owners.name == str(value)).first()
                                try: horse_owner_ID = query[0]
                                except: breakpoint()
                                
                    elif column == "Stajnia:": 
                            session = Session()
                            try: 
                                query = session.query(db.Stables.ID).filter(db.Stables.name == str(value).strip()).first()
                                horse_stable_ID = query[0]
                            except:
                                db_insert.insert_stable(stable_name=str(value).strip(), stable_adress=None)
                                query = session.query(db.Stables.ID).filter(db.Stables.name == str(value).strip()).first()
                                try: horse_stable_ID = query[0] 
                                except: horse_stable_ID = None # to fix
                                                
                    elif column == "Wymiary:": 
                        size = value
                    elif column == "Ojciec:": 
                        query = (db.Horses.name == str(value))
                        if db_insert.is_exist(db.Horses,query):
                            session = Session()
                            horse_father_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                        else: 
                            try: 
                                parent_href = pair.find('a', href=True)['href'] 
                                try: 
                                    int(parent_href)
                                    parent_href = f'/horse/{parent_href}'
                                except: parent_href = f'/{parent_href}'
                            except: parent_href = None  
                            
                            self.get_horse_data(value, parent_href)
                            session = Session()
                            while not horse_father_ID:
                                try: 
                                    horse_father_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                                except: 
                                    value = value[0:-1]
                                    if len(value) == 1:
                                        break
                            
                    elif column   == "Matka:":
                        query = (db.Horses.name == str(value))
                        if db_insert.is_exist(db.Horses,query):
                            session = Session()
                            horse_mother_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                        else: 
                            try:
                                parent_href = pair.find('a', href=True)['href'] 
                                try: 
                                    int(parent_href)
                                    parent_href = f'/horse/{parent_href}'
                                except: parent_href = f'/{parent_href}'
                            except: 
                                parent_href = None  
                            self.get_horse_data(value, parent_href)
                            session = Session()
                            while not horse_mother_ID:
                                try: 
                                    horse_mother_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(value)).first()[0]
                                except: 
                                    value = value[0:-1]
                                    if len(value) == 1:
                                        break
                            
                db_insert.insert_horse(horse_name = horse_name, horse_gender = horse_gender, horse_brith_date = horse_brith_date
                                    , horse_coat = horse_coat, horse_breed = horse_breed, horse_origin = horse_origin
                                    , horse_father_ID = horse_father_ID, horse_mother_ID = horse_mother_ID
                                    , horse_trainer_ID = horse_trainer_ID, horse_owner_ID = horse_owner_ID
                                    , horse_stable_ID = horse_stable_ID, horse_size = size)
        #except: return
            os.remove(f"horse_page_{name}.txt")