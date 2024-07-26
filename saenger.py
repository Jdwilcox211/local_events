import time
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


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
#chromedriver_autoinstaller.install()
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
main_sheet = wks.worksheet("Saenger")

def clear_sheet():
        wks.values_clear("Saenger!A1:B60")
        time.sleep(2)
        wks.values_clear("Saenger!D1:E60")
        time.sleep(2)
        
def event_data(sheettype):
    event_subtitle=''
    exrow=1
    exrowcon=1
    sheettype.update_acell(f'A{exrow}', f'Saenger Theater - Upcoming Events')
    sheettype.update_acell(f'D{exrow}', f'Saenger Theater - Upcoming Events - continued')
    exrow+=3
    exrowcon+=3
    saengerurl="https://www.pensacolasaenger.com/events"
    driver.get(f'{saengerurl}')
    event_subtitle=''
    time.sleep(2)

    source1 = driver.page_source
    soup = BeautifulSoup(source1, 'lxml')


    for event_card in soup.find_all('li',{'class':'event'}):
        for title in event_card.find_all('h3',{'class':'h4'}):        
            event_title=title.text
            #print(event_title)
        for subtitle in event_card.find_all('span',{'class':'event-category'}):    
            rawevent_subtitle=subtitle.text
            event_subtitle=f'{rawevent_subtitle} - '
            #print(event_subtitle)
        for showdate_month in event_card.find_all('span',{'class':'abv'}):
                eventmonth=showdate_month.text
                #print(eventmonth)
        for showdate_day in event_card.find_all('span',{'class':'cal__day'}):
                eventday=showdate_day.text
                #print(eventday)

        
        event_header=f'{eventmonth} {eventday} - {event_subtitle}{event_title}'
        
        print(event_header)
        if exrow <= 29:
            sheettype.update_acell(f'A{exrow}', event_header)
            exrow+=1

        else:
            sheettype.update_acell(f'D{exrowcon}', event_header)
            exrowcon+=1
        
        time.sleep(1)

        print(f'{event_header}')
        event_title=''
        event_subtitle=''
        eventday=''
        eventmonth=''


    #return exrow
clear_sheet()
event_data(main_sheet)


timestamp=datetime.now()
tlog=timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
main_sheet.update_acell(f'A2', f'last updated: {tlog}')
main_sheet.update_acell(f'D2', f'last updated: {tlog}')

driver.quit()
logger.info('Saenger Script Complete \n \n')