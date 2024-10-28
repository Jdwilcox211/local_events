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
logger = logging.getLogger("NBASTATS")
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
current_season_sheet = wks.worksheet("NBA")
season_leader_sheet = wks.worksheet("NBA_Players")

#pull_current_season

currentseasoncode = current_season_sheet.acell('S8').value
logger.info(currentseasoncode)
#api URLS
pointsapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=PTS'
reboundsapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=REB'
assistsapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=AST'
blocksapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=BLK'
stealsapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=STL'
fgpapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=FG_PCT'
tpmapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=FG3M'
tppapiurl = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season={currentseasoncode}&SeasonType=Regular%20Season&StatCategory=FG3_PCT'

#dfheaderlists
pointsheaders = ['RANK','PLAYER','TEAM','PTS']
reboundsheaders = ['RANK','PLAYER','TEAM','REB']
assistsheaders = ['RANK','PLAYER','TEAM','AST']
blocksheaders = ['RANK','PLAYER','TEAM','BLK']
stealsheaders = ['RANK','PLAYER','TEAM','STL']
fgpheaders = ['RANK','PLAYER','TEAM','FG_PCT']
tpmheaders = ['RANK','PLAYER','TEAM','FG3M']
tppheaders = ['RANK','PLAYER','TEAM','FG3_PCT']

def clear_stat_sheet():
    wks.values_clear("NBA_Players!A4:J8")
    time.sleep(10)
    wks.values_clear("NBA_Players!A11:J15")
    time.sleep(10)
    wks.values_clear("NBA_Players!A18:J22")
    time.sleep(10)
    wks.values_clear("NBA_Players!A25:J29")
    time.sleep(10)
    wks.values_clear("NBA_Players!A35:J38")
    time.sleep(10)
    wks.values_clear("NBA_Players!A42:J45")
    time.sleep(10)
    wks.values_clear("NBA_Players!A49:J52")
    time.sleep(10)
    wks.values_clear("NBA_Players!A56:J59")
    time.sleep(10)

def even_data_season_lead(sheettype,dfheaderlist,rowstart,statexcol,apiurl):
    pd.set_option('display.max_columns', None)
    headers  = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'x-nba-stats-token': 'true',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-nba-stats-origin': 'stats',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://stats.nba.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    # logger.info(dfheaderlist)
    headerstring = ', '.join(dfheaderlist)
    # logger.info(headerstring)
    # timeout set to 2 hours 60sec x 60min x 2hours 
    r = requests.get(url=apiurl, headers=headers, timeout=(60*60*2)).json()
    table_headers = r['resultSet']['headers']
    statpergamedf = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
    
    statpergameleague=statpergamedf
    lgstatlead = statpergameleague[dfheaderlist].head()
    statpergamemiami=statpergamedf[statpergamedf['TEAM'] == 'MIA']
    miastatlead = statpergamemiami[dfheaderlist].head()
    
    
    for dfheader in dfheaderlist:
        logger.info(dfheader)
        # logger.info(f'column = {statexcol}')
        
        for statrowincrement in range(0,5):
            statexrow_A=(rowstart+statrowincrement)
            statexrow_B=(statexrow_A+31)
            # logger.info(f'exrow A = {statexrow_A}')
            # logger.info(f'exrow B = {statexrow_B}')
            
            dfitem=statrowincrement
            # logger.info(f'dfitemnumber = {dfitem}')
            try:
                league_entry = lgstatlead[dfheader].iloc[dfitem]
                logger.info(f'league entry = {league_entry}')
                # logger.info(miastatlead[dfheader])
                # logger.info(miastatlead[dfheader].shape)
                miami_entry = miastatlead[dfheader].iloc[dfitem]
                logger.info(f'miami_entry {miami_entry} \n\n')
            
                sheettype.update_cell(statexrow_A, statexcol, str(league_entry))
                time.sleep(5)
                sheettype.update_cell(statexrow_B, statexcol, str(miami_entry))
                time.sleep(5)
            except Exception as e:
                logger.warning(f'Error: {e}\n\n')
        statexcol+=1

clear_stat_sheet()
even_data_season_lead(season_leader_sheet,pointsheaders,4,1,pointsapiurl)
even_data_season_lead(season_leader_sheet,reboundsheaders,4,6,reboundsapiurl)
even_data_season_lead(season_leader_sheet,assistsheaders,11,1,assistsapiurl)
even_data_season_lead(season_leader_sheet,blocksheaders,11,6,blocksapiurl)
even_data_season_lead(season_leader_sheet,stealsheaders,18,1,stealsapiurl)
even_data_season_lead(season_leader_sheet,fgpheaders,18,6,fgpapiurl)
even_data_season_lead(season_leader_sheet,tpmheaders,25,1,tpmapiurl)
even_data_season_lead(season_leader_sheet,tppheaders,25,6,tppapiurl)

timestamp=datetime.now()
tlog=timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
season_leader_sheet.update_acell(f'K1', f'last updated: {tlog}')

driver.quit()
logger.info('NBA Script Complete \n \n')