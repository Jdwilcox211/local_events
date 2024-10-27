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
import pandas as pd
import requests

pd.set_option('display.max_columns', None)

# service=Service(executable_path=r'/home/kitchentv/python_scripts/chromedriver')

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
logger = logging.getLogger("NBAStandings")
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
roster_sheet = wks.worksheet("NBA_roster_data")



def clear_team_sheet():
    wks.values_clear("NBA_roster_data!B2:J32")
    time.sleep(10)

def event_data_team_standard(sheettype): 
    exrow=2
    
    roster_url = 'https://www.cbssports.com/nba/teams/MIA/miami-heat/roster/'
    driver.get(f'{roster_url}')
    time.sleep(2)

    source1 = driver.page_source
    soup = BeautifulSoup(source1, 'lxml')

    for team_card in soup.find_all('tr',{'class':'TableBase-bodyTr'}):
        excol=3
        for name in team_card.find_all('span',{'class':'CellPlayerName--long'}):
            for tag in name.find_all('a'):
                playername=tag.text.strip()
                logger.info(playername)
                sheettype.update_cell(exrow, 2, playername)
                time.sleep(6)
        for team_data in team_card.find_all('td',{'class':'TableBase-bodyTd'}):
            datapoint=team_data.text.strip()
            logger.info(datapoint)
            sheettype.update_cell(exrow, excol, datapoint)
            time.sleep(6)
            excol+=1 
        exrow+=1

clear_team_sheet()
event_data_team_standard(roster_sheet)

timestamp=datetime.now()
tlog=timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
roster_sheet.update_acell(f'A1', f'last updated: {tlog}')

driver.quit()
logger.info('NBA Script Complete \n \n')                