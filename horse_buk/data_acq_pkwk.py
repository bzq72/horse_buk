"""Contain methods for acquisition data from race protocols (pkwk.pl)"""

import urllib.request, urllib.error, urllib.parse
import re
import requests
import PyPDF2
import db_insert
import db_creation as db

from sqlalchemy.orm import sessionmaker

import data_acq_kw as dck


Session = sessionmaker(bind = db.engine)

class data_acq_pkwk():
    
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
        elif not self.isSthNew(): print("No new version available")
        
    def update_protocol_set(self):
        pattern_url = re.compile('https:\/\/www\.pkwk\.pl\/wp-content\/uploads\/2022\/\d{1,}\/Wyniki_(WARSZAWA|SOPOT)_\d{1,}-\d{1,}-\d{4,}_Dzien_\d{3,}\.pdf')
        protocols_iterator = pattern_url.finditer(self.last_version)
        for protocol in protocols_iterator:
            if protocol not in self.protocols_urls_list: 
                self.protocols_urls_list.append(protocol.group())
    
    def get_extracted_protocol(self,url):
        response = requests.get(url)
        response.encoding = response.apparent_encoding
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
        extracted_protocol = extracted_protocol.replace(" ż","ż").replace(" Ż","Ż").replace(" ń","ń").replace(" ą", "ą")
        extracted_protocol = extracted_protocol.replace(" ęż ", "ęż")
        return extracted_protocol

    def obtain_race_day_info(self, page_text):
        """race day data contain also datas about race, booking rates and race places"""
        rd_date = re.findall(r", .*",page_text)[0]
        rd_date = rd_date[1:].rstrip().lstrip()
        rd_track_info = re.findall(r".*",page_text)
        rd_track = rd_track_info[8].rstrip().lstrip()
        rd_track_condition = re.search(r", .*",rd_track_info[12]).group()[2:]
        rd_weather = re.search(r".*C\)",rd_track_info[12]).group()
        session = Session()
        db_insert.insert_race_day(rd_date=rd_date, rd_track=rd_track, rd_track_condition=rd_track_condition, rd_weather=rd_weather)
        session = Session()
        query = session.query(db.Race_days.ID).filter((db.Race_days.date == str(rd_date)) & (db.Race_days.track == rd_track)).first()
        
        pattern_race = re.compile('((\d \(\d{1,3}\)(.+\n){5,25})ZWC.+)\n')
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
        """race data contain also datas about booking rates and race places"""
        race_horse_age=re.search(r"\d{1}-letnich",race_info).group()[0]
        race_distance=re.search(r"\d{4}m",race_info).group()
        race_horse_group=re.search(r"koni [\s\S]+m *\)|handikapowa [\s\S]+m *\)",race_info).group()
        race_horse_group = " ".join(race_horse_group.split()[1:(len(race_horse_group.split())-1)])
        race_time_finish = re.search(r"Czas:.*",race_info).group()
        race_time = re.search(r".*\),",race_time_finish).group()[6:-1]
        race_finish = re.search(r"\),.*",race_time_finish).group()[3:]
        race_booking_rates = re.search(r"ZWC.*",race_info).group()
        session = Session()
        db_insert.insert_race(race_race_day_ID=race_race_day_id, race_horse_group=race_horse_group , race_horse_age=race_horse_age
                              , race_distance=race_distance, race_time=race_time,race_finish=race_finish)    
        session = Session()
        race_id = session.query(db.Race.ID).filter((db.Race.horse_group == race_horse_group) & (db.Race.time ==race_time)).first()
        self.get_booking_rates(race_booking_rates, race_id[0])
        self.get_race_places(race_info, race_id[0])
    
    def get_race_places(self, race_info, race_id):
        pattern_place = re.compile(r'^\d{1,2}(.+\n){0,0}.*●.*|^\d{1,2}(.+\n){0,2}.*●.*', flags=re.MULTILINE)
        place_info_iter = pattern_place.finditer(race_info)
        for place_info in place_info_iter:
            rp_place = int(place_info.group()[0])
            rp_horse = re.search(r"\).*[\n|●]",place_info.group()).group()[2:-1].strip()
            try: 
                rp_horse = re.search(r"^[A-Z]{1}.{,35}\)",rp_horse, flags=re.MULTILINE).group().strip()[0:-5].strip()
            except: pass
            query_horse = (db.Horses.name == str(rp_horse.strip()))
            if db_insert.is_exist(db.Horses,query_horse):
                session = Session()
                rp_horse_ID = session.query(db.Horses.ID).filter(db.Horses.name == rp_horse).first()[0]
            else: 
                obj = dck.data_acq_kw()
                obj.get_horse_data(rp_horse)
                #dataget_horse_data(value)
                session = Session()
                try: rp_horse_ID = session.query(db.Horses.ID).filter(db.Horses.name == str(rp_horse).strip()).first()[0]
                except: rp_horse_ID = 25
            
            rp_jockey = re.search(r"●.*\w{1,2}\. {0,2}\S{2,26}",place_info.group(),flags=re.MULTILINE).group().strip()
            rp_jockey = re.search(r"[A-Z]+\.( )*\S*",rp_jockey,flags=re.MULTILINE).group().strip()
            rp_jockey_name = re.search(r"[A-Z]+\.",rp_jockey,flags=re.MULTILINE).group().strip()
            rp_jockey_surname = re.search(r"\.( )*\S*",rp_jockey,flags=re.MULTILINE).group().strip()

            query_jockeys = ((db.Jockeys.name == rp_jockey_name) & (db.Jockeys.surname == rp_jockey_surname))
            
            if db_insert.is_exist(db.Jockeys,query_jockeys):
                session = Session()
                rp_jockey_ID = session.query(db.Jockeys.ID).filter(query_jockeys).first()[0]
            else: 
                db_insert.insert_jockey(jockey_name=rp_jockey_name,jockey_surname=rp_jockey_surname)
                rp_jockey_ID = session.query(db.Jockeys.ID).filter(query_jockeys).first()[0]               
                
            db_insert.insert_race_place(rp_race_ID=int(race_id), rp_place=int(rp_place) , rp_horse_ID=rp_horse_ID , rp_jockey_ID=rp_jockey_ID)
    
    def get_booking_rates(self, br_info, race_id):
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
        
        
              
checker = data_acq_pkwk()
#checker.getNewVersion(
#checker.updateProtocolSet()
#checker.get_horse_page()
#print(checker.protocols_urls_list)
#checker.get_horse_data()
#checker.get_extracted_protocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf")
checker.obtain_race_day_info(checker.get_extracted_protocol("https://www.pkwk.pl/wp-content/uploads/2022/05/Wyniki_WARSZAWA_07-05-2022_Dzien_004.pdf"))
#print(checker.get_extrected_protocol("https://www.pkwk.pl/wp-content/uploads/2022/06/Wyniki_WARSZAWA_25-06-2022_Dzien_016.pdf"))

#print(checker.get_extracted_protocol("https://www.pkwk.pl/wp-content/uploads/2022/05/Wyniki_WARSZAWA_07-05-2022_Dzien_004.pdf"))