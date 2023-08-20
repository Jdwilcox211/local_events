import time
from datetime import datetime, timedelta
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import chromedriver_autoinstaller
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

service=Service(executable_path=r'/home/kitchentv/python_scripts/chromedriver')

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
#comment/uncomment with the # on line below to toggle headless option.  make sure your login information is correct as headless mode will disable the manual login ability
options.add_argument("--headless")  
options.add_argument('--ignore-certificate-errors')
#this option is needed to run headless on some sites that deny headless browsers
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36}") 
#set system to look in lib folder for function files


#setup logging
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
logging.basicConfig(filename="app.log", filemode="a")
logger = logging.getLogger("ActivateAdminlog")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname) -8s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# #comment below is if you want to manually define chromedriver.  please comment out the next line below that if you wish to use your own chromedriver
# #driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=chrome_options)
#hromedriver_autoinstaller.install()
#driver = webdriver.Chrome(service=service,options=options)
driver = webdriver.Chrome(options=options)
driver.maximize_window()

#sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
#on linux change json path to full directory to run via crontab
credentials = ServiceAccountCredentials.from_json_keyfile_name(
#    "/home/kitchentv/python_scripts/glass-ranger-377322-28be46dc3b01.json", scope
   "C:/Python projects/secret/glass-ranger-377322-28be46dc3b01.json", scope
)  # Your json file here

gc = gspread.authorize(credentials)

wks = gc.open_by_key("1tQi6RkOLgI4V-NFU9cAXnYosY5xlUaWRUTqnVtxpQUM")
cinema1_sheet = wks.worksheet("Cinema1")
cinema2_sheet = wks.worksheet("Cinema2")

breezeshowtimeurl="https://www.movieshowtime.net/breeze/"
driver.get(f'{breezeshowtimeurl}')

today_date=datetime.now()
tomorrow_date=datetime.now() + timedelta(1)

date_header_today=str(today_date.strftime("%A %b %d"))
date_header_tomorrow=(tomorrow_date.strftime("%A %b %d"))
movie_today=str(today_date.strftime("%Y-%m-%d"))
movie_tomorrow=str(tomorrow_date.strftime("%Y-%m-%d"))

print(movie_today)
print(movie_tomorrow)


def clear_sheet():
        wks.values_clear("Cinema1!A1:B60")
        time.sleep(2)
        wks.values_clear("Cinema2!A1:B60")

def movie_data(movie_date,sheettype,header_date):
    exrow=1
    sheettype.update(f'A{exrow}', f'The Breeze Cinema 8 ({header_date})')
    exrow+=3
    breezeshowtimeurl="https://www.movieshowtime.net/breeze/"
    driver.get(f'{breezeshowtimeurl}')
    time.sleep(2)
    driver.find_element(By.XPATH, f'//a[@data-date="{movie_date}"]').click()
    time.sleep(2)
    source1 = driver.page_source
    soup = BeautifulSoup(source1, 'lxml')
    time.sleep(2)
    for movie_list in soup.find_all('div',{'id':'movie-list'}):
        for movie_card in movie_list.find_all('div',{'class':'movie'}):
            times=[]

            for movie_info in movie_card.find_all('div',{'class':'movie-info'}):        
                for title in movie_info.find_all('a',{'class':'movie-link'}):
                    movie_title=title.text
            
                for rating in movie_info.find_all('p',{'class':'duration-rating'}):    
                    movie_rating=rating.text

                # for director in movie_info.find_all('div',{'class':'director mobile-hide'}):    
                #     movie_director=director.text

                # for actor in movie_info.find_all('div',{'class':'actors mobile-hide'}):    
                #     movie_actor=actor.text

            for time_card in movie_card.find_all('div',{'class':'movie-times'}):
                for showing in time_card.find_all('a'):
                    times.append(showing.text)
            
            # movie_header=f'{movie_title} \n {movie_rating} \n {movie_director} \n {movie_actor}'
            showtimes=','.join(times)
            movie_header=f'{movie_title}'  

            sheettype.update(f'A{exrow}', f'{movie_header} - ({movie_rating})')
            exrow+=1
            time.sleep(2)
            #sheettype.update(f'B{exrow}', f'{movie_rating}')
            #exrow+=1
            time.sleep(2)
            sheettype.update(f'B{exrow}', f'Showtimes: {showtimes}')
            exrow+=1
            #exrow+=1
            time.sleep(1)
            
            print(f'{movie_header}')
            print(f'Showtimes: {showtimes}')
            del times
            showtimes=''
            movie_title=''
            movie_rating=''
            movie_header=''
            movie_director=''
            movie_actor=''
    #return exrow
clear_sheet()
# main_sheet.update(f'A1{exrow}', f'The Breeze Cinema 8 -Showtimes for {date_header_today}\n')
# exrow+=1
movie_data(movie_today,cinema1_sheet,date_header_today)
#main_sheet.update(f'A{exrow}', f'\n Showtimes for {date_header_tomorrow}\n')
#exrow+=1
movie_data(movie_tomorrow,cinema2_sheet,date_header_tomorrow)

timestamp=datetime.now()
tlog=timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
cinema1_sheet.update(f'A2', f'last updated: {tlog}')
cinema2_sheet.update(f'A2', f'last updated: {tlog}')
driver.quit()
logger.info('The Breeze Cinema Script Complete \n \n')