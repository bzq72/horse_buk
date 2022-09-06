import string
from unicodedata import name
import urllib.request, urllib.error, urllib.parse
import re
import requests
import PyPDF2
from selenium import webdriver
import db_insert
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
        
    def is_sth_new(self):
        response = urllib.request.urlopen(self.url_protocols)
        self.checking_version = response.read().decode('UTF-8')
        return self.checking_version != self.last_version
    
    def get_new_version(self):
        if self.isSthNew(): 
            self.last_version = self.checking_version
            print("New version downladed")
        # next line only for debuging
        elif not self.isSthNew(): print(
            "No new version available")
        
    def update_protocol_set(self):
        pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/2022\/\d{1,}\/Wyniki_(WARSZAWA|SOPOT)_\d{1,}-\d{1,}-\d{4,}_Dzien_\d{3,}\.pdf')
        protocols_iterator = pattern_url.finditer(self.last_version)
        for protocol in protocols_iterator:
            if protocol not in self.protocols_urls_list: 
                self.protocols_urls_list.append(protocol.group())
    
    def get_extracted_protocol(self,url):
        response = requests.get(url)
        if response.status_code == 200:
            with open("currentPDF", "wb") as current_protocol:
                current_protocol.write(response.content)
                return(self.extract_protocol('currentPDF'))
        else:
            print(response.status_code)
                
    def extract_protocol(self,pdf_protocol):
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
        session = Session()
        print(rd_date,rd_track)
        #db_insert.insert_race_day(rd_date=rd_date, rd_track=rd_track, rd_track_condition=rd_track_condition, rd_weather=rd_weather)
        session = Session()
        query = session.query(db.Race_days.ID).filter((db.Race_days.date == str(rd_date)) & (db.Race_days.track == rd_track)).first()
        
        pattern_race = re.compile('((\d \(\d{1,3}\)(.+\n){5,25})ZWC.+)\n')
        race_iterator = pattern_race.finditer(page_text)
        for race_info in race_iterator:
            if len(re.findall("ZWC",race_info.group())) > 1:
                pattern_race_2 = re.compile(r'((\d \(\d{1,3}\)(.+\n){5,17})ZWC.+)\n')
                race_iterator_2 = pattern_race_2.finditer(race_info.group())
                for race_info_2 in race_iterator_2:
                    self.get_race(race_info_2.group(), int(query[0]))
            else:                
                self.get_race(race_info.group(),int(query[0]))
    
    def get_race(self, race_info, race_race_day_id):
        race_horse_age=re.search(r"\d{1}-letnich",race_info).group()[0]
        race_distance=re.search(r"\d{4}m",race_info).group()
        race_horse_group=re.search(r"koni [\s\S]+m *\)|handikapowa [\s\S]+m *\)",race_info).group()
        race_horse_group = " ".join(race_horse_group.split()[1:(len(race_horse_group.split())-1)])
        race_time_finish = re.search(r"Czas:.*",race_info).group()
        race_time = re.search(r".*\),",race_time_finish).group()[6:-1]
        race_finish = re.search(r"\),.*",race_time_finish).group()[3:]
        race_booking_rates = re.search(r"ZWC.*",race_info).group()
        session = Session()
        #db_insert.insert_race(race_race_day_ID=race_race_day_id, race_horse_group=race_horse_group , race_horse_age=race_horse_age
        #                      , race_distance=race_distance, race_time=race_time,race_finish=race_finish)    
        session = Session()
        race_id = session.query(db.Race.ID).filter(db.Race.horse_group == race_horse_group).first()
        self.get_booking_rates(race_booking_rates, race_id[0])
        self.get_race_places(race_info, race_id[0])
    
    def get_race_places(self, race_info, race_id):
        #print(race_info)
        pattern_place = re.compile(r'^\d{1,2}(.+\n){0,0}.*●.*|^\d{1,2}(.+\n){0,2}.*●.*', flags=re.MULTILINE)
        #pattern_place = re.compile(r"\d{1,2}(.+\n){0,2}.*●.*")
        place_info_iter = pattern_place.finditer(race_info)
        for place_info in place_info_iter:
            #print(place_info.group())
            rp_place = int(place_info.group()[0])
            rp_horse_ID = re.search(r"\).*[\n|●]",place_info.group()).group()[2:-1].strip()
            try: 
                rp_horse_ID = re.search(r".*\(\w{2,3}\)",rp_horse_ID).group().split()[0]
                print("******")
            except: pass
            #print(place_info.group())
            rp_jockey_ID = re.search(r"●.*\w{1,2}\. {0,2}\S{2,26}",place_info.group(),flags=re.MULTILINE).group().strip()
            print(rp_horse_ID)
            print(rp_jockey_ID)
            
        #db_insert.insert_race_place(rp_race_ID=race_id, rp_place= , rp_horse_ID= , rp_jockey_ID=)
    
    def get_booking_rates(self, br_info, race_id):
        return
        br_zwc = None
        br_pdk = None
        br_trj = None
        br_tpl = None
        br_kwn = None
        br_czw = None
        br_spt = None
        br_list = br_info.split()
        for i, value in enumerate (br_list):
            if i%2 == 1: continue
            if value == "ZWC":
                br_zwc = float(br_list[i+1].replace(",","."))                
            elif value == "PDK":
                br_pdk = float(br_list[i+1].replace(",","."))         
            elif value == "TRJ":
                br_trj = float(br_list[i+1].replace(",","."))         
            elif value == "TPL":
                br_tpl = float(br_list[i+1].replace(",","."))         
            elif value == "KWN":
                br_kwn = float(br_list[i+1].replace(",","."))         
            elif value == "CZW":
                br_czw = float(br_list[i+1].replace(",","."))         
            elif value == "SPT":
                br_spt = float(br_list[i+1].replace(",","."))         
        db_insert.insert_booking_rates(br_race_id=race_id, br_zwc=br_zwc, br_pdk=br_pdk, br_trj=br_trj, br_tpl=br_tpl,
                                       br_kwn=br_kwn, br_czw=br_czw,br_spt=br_spt)      
        
        
              
checker = DataAcquisition()
#checker.getNewVersion(
#checker.updateProtocolSet()
#checker.get_horse_page()
#print(checker.protocols_urls_list)
#checker.get_horse_data()
#checker.get_extracted_protocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf")
checker.get_race_day(checker.get_extracted_protocol("https://www.pkwk.pl/wp-content/uploads/2022/05/Wyniki_WARSZAWA_07-05-2022_Dzien_004.pdf")
)
#print(checker.get_extrected_protocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf"))
