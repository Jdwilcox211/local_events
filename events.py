import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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

time.sleep(3)
print('checking values')
cinema1val = wks.worksheet("Cinema1").acell('C2').value
cinema2val = wks.worksheet("Cinema2").acell('C2').value
print(f'val one is {cinema1val} and val 2 is {cinema2val}')
time.sleep(5)
if cinema1val != "TRUE" or cinema2val != "TRUE":
    import breezecinema
del cinema1val
del cinema2val   
time.sleep(10)

clubla1val = wks.worksheet("ClubLA").acell('C2').value
clubla2val = wks.worksheet("ClubLA").acell('F2').value
print(f'val one is {clubla1val} and val 2 is {clubla2val}')
time.sleep(5)
if clubla1val != "TRUE" or clubla2val != "TRUE":    
    import clubla
del clubla1val
del clubla2val      
time.sleep(10)

saenger1val = wks.worksheet("Saenger").acell('C2').value
saenger2val = wks.worksheet("Saenger").acell('F2').value
print(f'val one is {saenger1val} and val 2 is {saenger2val}')
time.sleep(5)
if saenger1val != "TRUE" or saenger2val != "TRUE":
    import saenger
del saenger1val
del saenger2val    
time.sleep(10)

vinyl1val = wks.worksheet("Vinyl").acell('C2').value
vinyl2val = wks.worksheet("Vinyl").acell('F2').value
print(f'val one is {vinyl1val} and val 2 is {vinyl2val}')
time.sleep(5)
if vinyl1val != "TRUE" or vinyl2val != "TRUE":
    import vinyl    
del vinyl1val
del vinyl2val    
time.sleep(10)

print('all events have been ran')