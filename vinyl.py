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
from icecream import ic


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

ic.disable()

#setup logging
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
logging.basicConfig(filename="app.log", filemode="a")
logger = logging.getLogger("Vinyl Music Hall")
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
main_sheet = wks.worksheet("Vinyl")

def clear_sheet():
        wks.values_clear("Vinyl!A1:B60")
        time.sleep(2)
        wks.values_clear("Vinyl!D1:E60")
        time.sleep(2)

def event_data(sheettype):
    event_title=''
    #event_subtitle=''
    eventdate=''
    eventdoortime=''
    eventtime=''
    eventage=''
    eventprice=''
    eventanddoortime=''
    exrow=1
    exrowcon=1
    sheettype.update_acell(f'A{exrow}', f'Vinyl Music Hall - Upcoming Events')
    sheettype.update_acell(f'D{exrow}', f'Vinyl Music Hall - Upcoming Events - continued')
    exrow+=3
    exrowcon+=3
    vinylurl="http://vinylmusichall.com/"
    driver.get(f'{vinylurl}')
    ic(f'loaded {vinylurl}')
    event_subtitle=''
    time.sleep(2)

    source1 = driver.page_source
    soup = BeautifulSoup(source1, 'lxml')
    ic('grabbed soup')


    
    for title_header in soup.find_all('div',{'class':'event-info-block'}):
        ic('found a title header')
        for title in title_header.find_all('p',{'class':'fs-12 headliners'}):
            rawevent_title=title.text
            event_title=rawevent_title
            ic(event_title)
        for subtitle in title_header .find_all('p',{'class':'fs-12 subtitle'}):
            rawevent_subtitle=subtitle.text
            if rawevent_subtitle != '':
                event_subtitle=f' - {rawevent_subtitle}'
            else:
                event_subtitle=''
            ic(event_subtitle)
        for showdate in title_header.find_all('p',{'class':'fs-18 bold mt-1r date'}):
            eventdate=showdate.text
            ic(eventdate)
        for doortime in title_header.find_all('p',{'class':'fs-12 doortime-showtime'}):
            eventanddoortime=doortime.text
            ic(eventanddoortime)
        ## old pull door and show time
        # for doortime in title_header.find_all('span',{'class':'see-doortime '}):
        #         eventdoortime=doortime.text
        #         ic(eventdoortime)
        # for showtime in title_header.find_all('span',{'class':'see-showtime '}):
        #         eventtime=showtime.text
        #         ic(eventtime)
        for showage in title_header.find_all('span',{'class':'ages'}):
                raweventage=showage.text
                eventage=f'{raweventage} | '
                ic(eventage)
        for showprice in title_header.find_all('span',{'class':'price'}):
                eventprice=showprice.text
                ic(eventprice)
                
        
        event_header=f'{eventdate} - {event_title}{event_subtitle}'
        showtimes=f'{eventage}{eventprice} - {eventanddoortime}'
        ic(event_header)
        
        if exrow <= 29:
            sheettype.update_acell(f'A{exrow}', event_header)
            exrow+=1
            time.sleep(2)
            sheettype.update_acell(f'B{exrow}', showtimes)
            exrow+=1

        else:
            sheettype.update_acell(f'D{exrowcon}', event_header)
            exrowcon+=1
            time.sleep(1)
            sheettype.update_acell(f'E{exrowcon}', showtimes)
            exrowcon+=1

            time.sleep(1)


            print(f'{event_header}')
            print(f'{showtimes}')
            event_title=''
            event_subtitle=''
            eventdate=''
            eventdoortime=''
            eventtime=''
            eventage=''
            eventprice=''
            eventanddoortime=''

    #return exrow
clear_sheet()
event_data(main_sheet)


timestamp=datetime.now()
tlog=timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
main_sheet.update_acell(f'A2', f'last updated: {tlog}')
main_sheet.update_acell(f'D2', f'last updated: {tlog}')

driver.quit()
logger.info('Vinyl Script Complete \n \n')