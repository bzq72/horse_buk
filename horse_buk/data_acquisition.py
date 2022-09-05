import string
from unicodedata import name
import urllib.request, urllib.error, urllib.parse
import re
import requests
import PyPDF2
from selenium import webdriver
import db_creation, db_insert
import db_creation as db


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker


Session = sessionmaker(bind = db.engine)
""" 
    checking if there is already new protocol
    downlading protocols
    https://www.pkwk.pl/language/pl/sprawozdania-2022/ 
"""

class DataAcquisition():
    
    def __init__(self):
        self.protocols_urls_list = []
        self.url_protocols = "https://www.pkwk.pl/language/pl/sprawozdania-2022/"
        response = urllib.request.urlopen(self.url_protocols)
        self.last_version = response.read().decode('UTF-8')
        
    def isSthNew(self):
        response = urllib.request.urlopen(self.url_protocols)
        self.checking_version = response.read().decode('UTF-8')
        return self.checking_version != self.last_version
    
    def getNewVersion(self):
        if self.isSthNew(): 
            self.last_version = self.checking_version
            print("New version downladed")
        # next line only for debuging
        elif not self.isSthNew(): print(
            "No new version available")
        
    def updateProtocolSet(self):
        pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/2022\/\d{1,}\/Wyniki_(WARSZAWA|SOPOT)_\d{1,}-\d{1,}-\d{4,}_Dzien_\d{3,}\.pdf')
        protocols_iterator = pattern_url.finditer(self.last_version)
        for protocol in protocols_iterator:
            if protocol not in self.protocols_urls_list: 
                self.protocols_urls_list.append(protocol.group())
    
    def getExtractedProtocol(self,url):
        response = requests.get(url)
        if response.status_code == 200:
            with open("currentPDF", "wb") as current_protocol:
                current_protocol.write(response.content)
                return(self.extractProtocol('currentPDF'))
        else:
            print(response.status_code)
                
    def extractProtocol(self,pdf_protocol):
        extracted_protocol = ""
        reader = PyPDF2.PdfFileReader(pdf_protocol)
        for page_number in range(reader.numPages):
            page = reader.getPage(page_number)
            extracted_protocol += page.extractText()
        return extracted_protocol

    def get_horse_page(self):
        self.url_horse = "https://koniewyscigowe.pl/horse/23947-gabonn"
        options = webdriver.ChromeOptions() 
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\48725\AppData\Local\Programs\Python\Python310\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe')
        driver.get(self.url_horse)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "section.g-py-50")))
        content = driver.page_source.encode('utf-8')
        
        with open ("horse_page.txt","wb") as horse_page:
            horse_page.write(content)
       
    def get_horse_data(self):
        with open("horse_page.txt","r",encoding="utf-8") as horse_page:    
            page = BeautifulSoup(horse_page,"html.parser")
            horse_name = str(page.h1.string)
            info = page.find("tbody").find_all("tr")
            main_horse_info = info[0].strong.string.split()
            horse_coat, horse_gender, horse_brith_date = main_horse_info[0], main_horse_info[1], main_horse_info[3]
            for pair in info[1:]:
                column, value = pair.find("th").string, pair.find("td").string
                if not value: value = pair.td.a.string
                if column == "Rasa:": horse_breed = value
                elif column == "Pochodzenie:": horse_origin = value
                elif column == "Ojciec:": horse_father_ID = 1
                elif column   == "Matka:": horse_mother_ID = 1
                elif column == "Trener:": 
                        value = value.split()
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
                            query = session.query(db.Owners.ID).filter(db.Owners.name == str(value)).first()
                            horse_owner_ID = query[0]
                            
                elif column == "Stajnia:": 
                        session = Session()
                        try: 
                            query = session.query(db.Stables.ID).filter(db.Stables.name == str(value)).first()
                            horse_stable_ID = query[0]
                        except:
                            db_insert.insert_stable(stable_name=str(value), stable_adress=None)
                            query = session.query(db.Stables.ID).filter(db.Stables.name == str(value)).first()
                            horse_stable_ID = query[0] 
                                               
                elif column == "Wymiary:": size = value

            db_insert.insert_horse(horse_name = horse_name, horse_gender = horse_gender, horse_brith_date = horse_brith_date
                                   , horse_coat = horse_coat, horse_breed = horse_breed, horse_origin = horse_origin
                                   , horse_father_ID = horse_father_ID, horse_mother_ID = horse_mother_ID
                                   , horse_trainer_ID = horse_trainer_ID, horse_owner_ID = horse_owner_ID
                                   , horse_stable_ID = horse_stable_ID, horse_size = size)

            
    def get_race_day(self, page_text):
        rd_date = re.findall(r", .*",page_text)[0]
        rd_date = rd_date[1:].rstrip().lstrip()
        rd_track_info = re.findall(r".*",page_text)
        rd_track = rd_track_info[8].rstrip().lstrip()
        rd_track_condition = re.search(r", .*",rd_track_info[12]).group()[2:]
        rd_weather = re.search(r".*C\)",rd_track_info[12]).group()
        print(rd_track_condition, rd_track, rd_weather)
        db_insert.insert_race_day(rd_date=rd_date, rd_track=rd_track, rd_track_condition=rd_track_condition, rd_weather=rd_weather)
        
        pattern_race = re.compile('((\d \(\d{1,3}\)(.+\n){5,25})ZWC.+)\n')
        race_iterator = pattern_race.finditer(page_text)
        for race_data in race_iterator:
            pass
            #print(race_data.group())
    
    def get_race(self, race_info):
        pass
    
    def get_booking_rates():
        pass        
checker = DataAcquisition()
#checker.getNewVersion()
#checker.updateProtocolSet()
#checker.get_horse_page()
#print(checker.protocols_urls_list)
#checker.get_horse_data()
#checker.getExtractedProtocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf")
checker.get_race_day(checker.getExtractedProtocol("https://www.pkwk.pl/wp-content/uploads/2022/05/Wyniki_WARSZAWA_07-05-2022_Dzien_004.pdf")
)
#print(checker.getExtractedProtocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf"))
