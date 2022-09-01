import string
import urllib.request, urllib.error, urllib.parse
import re
import requests
import PyPDF2
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
""" 
    checking if there is already new protocol
    downlading protocols
    https://www.pkwk.pl/language/pl/sprawozdania-2022/ 
"""

class DataAcquisition:
    
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
        elif not self.isSthNew(): print("No new version available")
        
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
        self.url_horse = "https://koniewyscigowe.pl/horse/20899-a-dee-joe"
        options = webdriver.ChromeOptions() 
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\48725\AppData\Local\Programs\Python\Python310\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe')
        driver.get(self.url_horse)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "section.g-py-50")))
        content = driver.page_source.encode('utf-8')
        
        with open ("horse_page.txt","wb") as horse_page:
            horse_page.write(content)
       
    def get_horse_data(self):
        with open("horse_page.txt","r",encoding="utf-8") as horse_page:    
            info = BeautifulSoup(horse_page,"html.parser").find("tbody").find_all("tr")
            main_horse_info = info[0].strong.string.split()
            print(info[0].strong.string)
            print(main_horse_info[3])
            for pair in info[1:]:
                column, value = pair.find("th").string, pair.find("td").string
                if not value: value = pair.td.a.string
                
                print(column,value)
            

            
    def get_horse_name(self):
        doc = BeautifulSoup(outfile2,"html.parser")
        
            
checker = DataAcquisition()
#checker.getNewVersion()
#checker.updateProtocolSet()
checker.get_horse_page()
#print(checker.protocols_urls_list)
checker.get_horse_data()

#print(checker.getExtractedProtocol("https://www.pkwk.pl/wp-content/uploads/2022/08/Wyniki_WARSZAWA_21-08-2022_Dzien_026.pdf"))