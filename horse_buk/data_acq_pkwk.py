"""Contain methods for acquisition data from race protocols (pkwk.pl)"""
from datetime import datetime
from itertools import chain
import re
import requests
import PyPDF2
import db_insert
import db_creation as db
from sqlalchemy.orm import sessionmaker
import data_acq_kw as dck
from unidecode import unidecode
from db_insert import insert_record, is_exist

Session = sessionmaker(bind = db.engine)

class Data_Acq_pkwk():
    def __init__(self, url_protocols_adres = "https://www.pkwk.pl/language/pl/sprawozdania-2022/"):
        try:
            with open (f"last_pkwk_ver.txt","rb") as last_pkwk_ver:
                self.last_version = last_pkwk_ver.read().decode('UTF-8')
        except: self.last_version = None
        self.protocols_urls_list = []
        self.url_protocols = url_protocols_adres
        #response = urllib.request.urlopen(self.url_protocols)
        #self.last_version = response.read().decode('UTF-8')
        
    def is_sth_new(self):
        """checking if there is new protocol on website"""
        #response = urllib.request.urlopen(self.url_protocols)
        #self.checking_version = response.read().decode('UTF-8')
        response = requests.get(self.url_protocols)
        response.encoding = response.apparent_encoding
        self.checking_version = response.content
        if self.checking_version == self.last_version:
            while True:
                force =  input("No new version available\nDo you want to force updating? (y/n)") 
                if force== "y": return True
                elif force == "n": return False
        return True

    def get_new_version(self):
        """getting latest version of website"""
        sth_new = self.is_sth_new()
        if sth_new: 
            self.last_version = self.checking_version
            with open("last_pkwk_ver.txt", "wb") as last_pkwk_ver:
                last_pkwk_ver.write(self.last_version)
            print("New version downladed")
            self.last_version = str(self.checking_version)
        # next line only for debuging
        elif not sth_new: 
            print("No new version available")
             
            
        
    def update_protocol_set(self):
        """updating protocol sets"""
        if "2022" in self.url_protocols:
            pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/2022\/\d{1,}\/Wyniki_(WARSZAWA)_\d{1,}-\d{1,}-\d{4,}_Dzien_\d{3,}\.pdf')
        elif "2021" in self.url_protocols:
            pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/2021\/\d{1,}\/Wyniki_(Warszawa)_\d{1,}-\d{1,}-\d{4,}_Dzien_\d{2,}\.pdf')
        elif "2020" in self.url_protocols:
            pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/docs\/2020\/Wyniki_Warszawa_\d{1,}-\d{1,}-\d{4}_((Dzien)|(Dzień))_\d{2}\.pdf')
        else:
            breakpoint()
        protocols_iterator = pattern_url.finditer(self.last_version)
        for protocol in protocols_iterator:
            if protocol not in self.protocols_urls_list: 
                self.protocols_urls_list.append(protocol.group())
                
    def get_every_protocol(self):
        """getting all infos avaiable info from all protocols """
        for url in self.protocols_urls_list:
            if is_exist(db.Protocols, (db.Protocols.url_adress == url)): continue
            ask = None
            while ask not in ['y','n']:
                ask = input(f"Do you want to get info from {url} (y/n)")
                if ask == "y":
                    self.obtain_race_day_info(self.get_extracted_protocol(url))
                    record = db.Protocols(url_adress = url)
                    insert_record(record)
                elif ask == "n": continue
    
    def download_every_thing(self):
        ask = input("Do you really want do download? (y/n)")
        if ask == "y":
            self.get_new_version()
            self.update_protocol_set()
            self.get_every_protocol()
        elif ask == "n": return
        else: self.download_every_thing()

            
    def get_extracted_protocol(self,url):
        """getting extracted protocol"""
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            with open("currentPDF", "wb") as current_protocol:
                current_protocol.write(response.content)
                return(self.extract_protocol('currentPDF'))
        else:
            print(response.status_code)
                
    def extract_protocol(self,pdf_protocol):
        """extracting protocol"""
        extracted_protocol = ""
        reader = PyPDF2.PdfFileReader(pdf_protocol)
        for page_number in range(reader.numPages):
            page = reader.getPage(page_number)
            extracted_protocol += page.extractText()
        extracted_protocol = extracted_protocol.replace(" ż","ż").replace(" Ż","Ż").replace(" ń","ń").replace(" ą", "ą"). replace(" ę","ę")
        extracted_protocol = extracted_protocol.replace(" ęż ", "ęż").replace("ł ę","łę").replace(" ź","ź").replace("ążę ","ążę")
        return extracted_protocol

    def obtain_race_day_info(self, page_text):
        """searching and inserting informations about race day"""
        """race day data contain also datas about race, booking rates and race places"""
        rd_date = re.findall(r", .*",page_text)[0]
        rd_date = rd_date[1:].rstrip().lstrip()
        rd_track_info = re.findall(r".*",page_text)
        rd_track = re.search(r"(WARSZAWA SŁUŻEWIEC)|(WARSZAWA SŁU ŻEWIEC)",page_text).group()
        try: 
            rd_weather = re.search(r".*C\)",rd_track_info[12]).group()
            rd_track_condition = re.search(r", .*",rd_track_info[12]).group()[2:]
        except: 
            try: 
                rd_weather = re.search(r".*C\)",rd_track_info[14]).group()
                rd_track_condition = re.search(r", .*",rd_track_info[14]).group()[2:]
            except:
                try: 
                    rd_weather = re.search(r".*C\)",rd_track_info[10]).group()
                    rd_track_condition = re.search(r", .*",rd_track_info[10]).group()[2:]
                except:
                    breakpoint()

        session = Session()
        db_insert.insert_race_day(rd_date=rd_date, rd_track=rd_track, rd_track_condition=rd_track_condition, rd_weather=rd_weather)
        session = Session()
        query = session.query(db.Race_days.ID).filter((db.Race_days.date == str(rd_date)) & (db.Race_days.track == rd_track)).first()
       
        pattern_race = re.compile(r'Nagroda(.*\n){0,22}ZWC.*')
        #pattern_race = re.compile('((\d \(\d{1,3}\)(.+\n){5,25})ZWC.+)\n')
        race_iterator = pattern_race.finditer(page_text)
        for race_info in race_iterator:
            if len(re.findall("ZWC",race_info.group())) > 1:
                pattern_race_2 = re.compile(r'((\d \(\d{1,3}\)(.+\n){5,17})ZWC.+)\n')
                race_iterator_2 = pattern_race_2.finditer(race_info.group())
                for race_info_2 in race_iterator_2:
                    self.obtain_race_info(race_info_2.group(), int(query[0]))
            else:     
                self.obtain_race_info(race_info.group(),int(query[0]))
    
    def obtain_race_info(self, race_info, race_race_day_id):
        """searching and inserting informations about race"""
        """race data contain also datas about booking rates and race places"""
        try: race_horse_age=re.search(r"(\d{1}-letn)|(\d{1} -letn)",race_info).group()[0]
        except: breakpoint()
        try: race_distance=re.search(r"\d{4}m",race_info).group()
        except: 
            try: race_distance=re.search(r"(\d{1}\d{1}\d{1} \d{1}m)|(\d{4} m)|(\d{1} \d{3}m)|(\d{2} \d{2}m)",race_info).group()
            except: 
                breakpoint()
                pass
                
        try: 
            try: 
                race_horse_group=re.search(r"(koni|ko ni|k laczy|klaczy|handikapowa|mi ędzynarodowa|międzynarodowa)(.*\n)*.*((\d{4}m\))|(\d{1}\d{1}\d{1} \d{1}m\))|(\d{4} m\))|(\d{1} \d{3}m\))|(\d{2} \d{2}m\)))",race_info).group()
                race_horse_group = " ".join(race_horse_group.split()[0:(len(race_horse_group.split())-2)])
            except: race_horse_group=re.search(r"(kłusaków)|(Gonitwa .* (koni)|(klaczy))",race_info).group()

        except: 
            breakpoint()
            race_horse_group="No group"
        race_time_finish = re.search(r"Czas:.*",race_info).group()
        try:
            race_time = re.search(r".*\),",race_time_finish).group()[6:-1]
            race_finish = re.search(r"\),.*",race_time_finish).group()[3:]
        except: 
            race_time = race_time_finish
            race_finish = None
        race_booking_rates = re.search(r"ZWC.*",race_info).group()
        session = Session()
        race_time = unidecode(race_time)
        if race_finish: race_finish = unidecode(race_finish)
        db_insert.insert_race(race_race_day_ID=race_race_day_id, race_horse_group=race_horse_group , race_horse_age=race_horse_age
                              , race_distance=race_distance, race_time=race_time,race_finish=race_finish)    
        session = Session()
        race_id = session.query(db.Race.ID).filter((db.Race.horse_group == race_horse_group) & (db.Race.time ==race_time)).first()
        try: self.get_booking_rates(race_booking_rates, race_id[0])
        except: 
            breakpoint()
        self.get_race_places(race_info, race_id[0])
    
    def get_race_places(self, race_info, race_id):
        """searching and inserting informations about places in race"""
        pattern_place = re.compile(r'^\d{1,2}(.+\n){0,0}.*●.*|^\d{1,2}(.+\n){0,2}.*●.*', flags=re.MULTILINE)
        places_iter = pattern_place.finditer(race_info)
        pattern_second_place = re.compile(r'^2(.+\n){0,0}.*●.*', flags=re.MULTILINE)
        second_place_iter = pattern_second_place.finditer(race_info)
        places_iter = chain(places_iter, second_place_iter)
        for place_info in places_iter:
            try: rp_place = int(place_info.group().split()[0].split("-")[0])
            except: breakpoint()
            rp_horse = re.search(r"\) .*[\n|●]",place_info.group(), flags=re.MULTILINE).group()[2:-1].strip()
            if rp_horse == "": 
                rp_horse = re.search(r"[A-Z]{1}.{0,20}((kl\.)|(wał)|(og\.)){1}",place_info.group(), flags=re.MULTILINE).group()[0:-4].strip()
            try: 
                rp_horse = re.search(r"^[A-Z]{1}.{,35}\)",rp_horse, flags=re.MULTILINE).group().strip()[0:-5].strip()
                try: rp_horse = re.search(r"^[A-Z]{1}.{0,20}((kl\.)|(wał)|(og\.)){1}",rp_horse, flags=re.MULTILINE).group().strip()[0:-4].strip()
                except: pass
            except: 
                try: 
                    rp_horse = re.search(r"^[A-Z]{1}.{0,20}((kl\.)|(wał)|(og\.)){1}",rp_horse, flags=re.MULTILINE).group().strip()[0:-4].strip()
                except: pass
            if "'oa'" in rp_horse.lower(): rp_horse = rp_horse[0:-1]
            query_horse = (db.Horses.name == str(rp_horse.strip()))
            if "  " in rp_horse: rp_horse = rp_horse.replace("  ", " ")
            if db_insert.is_exist(db.Horses,query_horse):
                session = Session()
                rp_horse_ID = session.query(db.Horses.ID).filter(db.Horses.name == rp_horse).first()[0]
            else: 
                obj = dck.Data_Acq_kw()
                while True:
                    obj.get_horse_data(rp_horse)
                    session = Session()
                    try: 
                        rp_horse_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(rp_horse).strip()).first()[0]
                        break
                    except:     
                        print("*********************************")
                        print(place_info.group())
                        rp_horse = input("write horse name or add {name of Horsce} without brackets to add new Horse\n")
                        if "add" in rp_horse.split(): 
                            rp_horse = rp_horse[4:]
                            horse_gender = input("Write horse gender\n")
                            horse_brith_date = input("Write horse year of brith\n")
                            horse_brith_date = datetime.strptime(str(input("Write horse year of brith\n")),"%Y")
                            db_insert.insert_horse(rp_horse, horse_gender, horse_brith_date)
                        
            try:
                rp_jockey = re.search(r"●.*\w{1,2}\. {0,2}\S{2,26}",place_info.group(),flags=re.MULTILINE).group().strip()
                rp_jockey = re.search(r"[A-Z]+\.( )*\S*",rp_jockey,flags=re.MULTILINE).group().strip()
                rp_jockey_name = re.search(r"[A-Z]+\.",rp_jockey,flags=re.MULTILINE).group().strip()
                rp_jockey_surname = re.search(r"\.( )*\S*",rp_jockey,flags=re.MULTILINE).group()[1:].strip()
            except:
                print("*********************************")
                print(place_info.group())
                rp_jockey_name = input("Put jockey name\n")
                rp_jockey_surname =  input("Put jockey surname\n")

                
            query_jockeys = ((db.Jockeys.name == rp_jockey_name) & (db.Jockeys.surname == rp_jockey_surname))
            
            if db_insert.is_exist(db.Jockeys,query_jockeys):
                session = Session()
                rp_jockey_ID = session.query(db.Jockeys.ID).filter(query_jockeys).first()[0]
            else: 
                db_insert.insert_jockey(jockey_name=rp_jockey_name,jockey_surname=rp_jockey_surname)
                rp_jockey_ID = session.query(db.Jockeys.ID).filter(query_jockeys).first()[0]               
                
            db_insert.insert_race_place(rp_race_ID=int(race_id), rp_place=int(rp_place) , rp_horse_ID=rp_horse_ID , rp_jockey_ID=rp_jockey_ID)
    
    def get_booking_rates(self, br_info, race_id):
        """searching and inserting informations about booking rates for race"""
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
                try: br_zwc = float(br_list[i+1].replace(",","."))      
                except: pass     
            elif value == "PDK":
                try: br_pdk = float(br_list[i+1].replace(",","."))   
                except: pass     
            elif value == "TRJ":
                try: br_trj = float(br_list[i+1].replace(",","."))      
                except: pass     
            elif value == "TPL":
                try: br_tpl = float(br_list[i+1].replace(",","."))    
                except: pass     
            elif value == "KWN":
                try: br_kwn = float(br_list[i+1].replace(",","."))   
                except: pass     
            elif value == "CZW":
                try: br_czw = float(br_list[i+1].replace(",","."))   
                except: pass     
            elif value == "SPT":
                try: br_spt = float(br_list[i+1].replace(",","."))    
                except: pass     
        db_insert.insert_booking_rates(br_race_id=race_id, br_zwc=br_zwc, br_pdk=br_pdk, br_trj=br_trj, br_tpl=br_tpl,
                                       br_kwn=br_kwn, br_czw=br_czw,br_spt=br_spt)      
        
        