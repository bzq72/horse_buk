import urllib.request, urllib.error, urllib.parse
import re
import requests
import PyPDF2
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

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

    def getHorseData(self):
        self.url_horse = " https://koniewyscigowe.pl/horse/30003-herbatka"
        #request = urllib.request.Request(self.url_horse, headers={'User-Agent': 'python-requests/2.21.0'})
        #our_horse = urllib.request.urlopen(request)
        #time.sleep(20)
        #our_horse = our_horse.read().
        ##our_horse = requests.get(self.url_horse, 'html.parser')
        #content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        #print(our_horse)
        
        # https://stackoverflow.com/questions/60072138/selenium-will-not-load-full-dom-tree-just-the-page-source
        options = webdriver.ChromeOptions() 
        #options.add_argument("start-maximized")
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\48725\AppData\Local\Programs\Python\Python310\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe')
        driver.get("https://koniewyscigowe.pl/horse/30003-herbatka")
        #time.sleep(100)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "section.g-py-50")))
        content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        print(content)
        
        with open("outfile.txt", "wb") as outfile:
	        outfile.write(content.encode('utf-8'))
         
        content = driver.page_source.encode('utf-8')
        print(content)
        
        with open("outfile2.txt", "wb") as outfile2:
	        outfile2.write(content)

        #print(driver.page_source)
        #driver.quit()
        
        
            
checker = DataAcquisition()
#checker.getNewVersion()
#checker.updateProtocolSet()
checker.getHorseData()
#print(checker.protocols_urls_list)

#print(checker.getExtractedProtocol("https://www.pkwk.pl/wp-content/uploads/2022/08/Wyniki_WARSZAWA_21-08-2022_Dzien_026.pdf"))