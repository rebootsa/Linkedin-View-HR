import time, random, os, csv, platform
import logging
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from Database import Data
from urllib.request import urlopen
from webdriver_manager.chrome import ChromeDriverManager
import re
from datetime import datetime, timedelta
def setupLogger() -> None:
    dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")
    if not os.path.isdir('./logs'):
        os.mkdir('./logs')
    # TODO need to check if there is a log dir available or not
    logging.basicConfig(filename=('./logs/' + str(dt) + 'applyJobs.log'), filemode='w',
                        format='%(asctime)s::%(name)s::%(levelname)s::%(message)s', datefmt='./logs/%d-%b-%y %H:%M:%S')
    log.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
    c_handler.setFormatter(c_format)
    log.addHandler(c_handler)
def browser_options():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    #  IF USE CHROME HIDE ACTIVE 
    #options.headless = True
    options.add_argument("--disable-extensions")
    # Disable webdriver flags or you will be easily detectable
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return options
log = logging.getLogger(__name__)
driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_options())
class LINKEDIN:
    setupLogger()
    def __init__(self,username,password) -> None:
        self.username = username
        self.password = password
        #self.options = self.browser_options()
        self.url = "https://linkedin.com"
        self.browser = driver
        self.wait = WebDriverWait(self.browser, 30)
        self.data = Data()
        self.Cookies()
    def start_linkedin(self) -> None:
        log.info("Logging in.....Please wait :)  ")
        self.browser.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        try:
            user_field = self.browser.find_element("id","username")
            pw_field = self.browser.find_element("id","password")
            login_button = self.browser.find_element("xpath",
                        '//*[@id="organic-div"]/form/div[3]/button')
            user_field.send_keys(self.username)
            user_field.send_keys(Keys.TAB)
            time.sleep(2)
            pw_field.send_keys(self.password)
            time.sleep(2)
            login_button.click()
            time.sleep(3)
            return True
        except TimeoutException:
            log.info("TimeoutException! Username/password field or login button not found")
            return False
    def Cookies(self):
        get = self.data.GetCookies(username=self.username)
        if get != False:
            self.browser.get(self.url)
            time.sleep(3)
            for i in get:
                self.browser.add_cookie(i)
            log.info("Succssful Cookies")
        else:
            Login = self.start_linkedin()
            if Login != False:
                self.data.SetCookies(Post=self.browser.get_cookies(),username=self.username)
    def View_People(self):
        get_URL = self.data.GetUrl_link(1)
        url = str(get_URL['URL'])
        get_Company = self.data.GetCompany()
        for i in get_Company:
            ID = i['ID']
            self.Company = i['Company']
            self.URL_NEW = url.replace("NUMBER",f"{ID}")
            log.info("START VIEW >> " + i['Company'])
            self.View()
    def While(self):
        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    def View(self):
        self.browser.get(self.URL_NEW)
        # Find Number URLS 
        try:
            wait = self.wait.until(EC.presence_of_element_located((By.XPATH,("//div[contains(@class,'search-marvel-srp')]"))))
        except TimeoutException as err:
            return self.View()
        whiles = self.While()
        soup = BeautifulSoup(self.browser.page_source,'lxml')
        time.sleep(3)
        id_main = soup.select_one(".artdeco-pagination__pages.artdeco-pagination__pages--number")
        if id_main != None:
            for i in id_main:
                try:
                    page = i.find('span').text
                except:
                    pass
            if int(page) == 0:
                page = 1
            log.info("PAGE Number: " + str(page))
            self.Page(page)   
        else:
            page = 1
            self.Page(page)
    def Page(self,page):
        pageNum = 1
        for i in range(int(page)):
            pageNum +=1
            wait = self.wait.until(EC.presence_of_element_located((By.XPATH,("//div[contains(@class,'search-marvel-srp')]"))))
            id_main = self.browser.find_element(By.XPATH,"//div[contains(@class,'search-marvel-srp')]")
            id_ul = id_main.find_element(By.TAG_NAME,"ul")
            id_il = id_ul.find_elements(By.TAG_NAME,"li")
            for i in id_il:
                url = i.find_element(By.TAG_NAME,"a").get_attribute('href')
                newTab = self.browser.execute_script(f'''window.open("{url}","_blank");''')
                time.sleep(randint(2,6))
                window_name = self.browser.window_handles[1]
                window = self.browser.window_handles[0]
                self.browser.switch_to.window(window_name=window_name)
                whiles = self.While()
                time.sleep(randint(6,18))
                try:
                    soup = BeautifulSoup(self.browser.page_source,'lxml')
                    Name = soup.select_one(".text-heading-xlarge.inline.t-24.v-align-middle.break-words").text
                    PROFILE = soup.select_one(".text-body-medium.break-words").text
                    POST = {"NAME":Name,"PROFILE":PROFILE,"URL":self.browser.current_url,"Company":self.Company}
                    # IF USE DATA BASE 
                    #self.data.Set_HR_profile(POST)
                    log.info("View >> " + Name)
                except:
                    log.debug("ERROR GET NAME USER")
                close = self.browser.close()
                self.browser.switch_to.window(window_name=window)
                time.sleep(4)
            Url_New = self.browser.current_url
            if re.findall("page",str(Url_New)):
                min = pageNum - 1
                Url = str(Url_New).replace(f"FACETED_SEARCH&page={min}",f"FACETED_SEARCH&page={pageNum}")
                self.browser.get(Url)
            else:
                Url = str(Url_New).replace("FACETED_SEARCH",f"FACETED_SEARCH&page={pageNum}")
                self.browser.get(Url)
            time.sleep(randint(15,30))                
if __name__ == '__main__':
    usuername = ""
    password = ""
    Class = LINKEDIN(usuername,password).View_People()