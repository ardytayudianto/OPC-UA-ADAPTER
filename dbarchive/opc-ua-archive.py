import os
import pandas as pd
import sqlite3
import requests
import json
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning

#read_config_file
path = os.getcwd()
print("Current path:" + path)
configpath = f'{path}/config.json'
with open(configpath) as config_file:
    config = json.load(config_file)

#get opc configuration
maximo_url = config["maximo_url"]
headers_maximo = config["headers_maximo"]
opc_servername = config["opc_servername"]
datakeepdays = config["datakeepdays"]

pagesize = 1000000
data=[]
backupSuccess = False

#Create SQLite DB
try:
    start = datetime.now()
    starttime = start.strftime("%Y-%m-%dT%H:%M:%S")
    datestr = start.strftime("%Y-%m-%d")
    print("start : " + starttime)
    
    dbname  = f'opcdata-{datestr}.db'
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS opcdata (opcdataid integer,description text, tag text, datetime text,  value number, orgid text, siteid text, servername text)')
    conn.commit()
except Exception as e:
    print("Create SQLLite DB Error")
    print(e)
 
#Get Maximo Data to Backup 
try:
    nowtime = datetime.now()
    deletetime = nowtime - timedelta(days=datakeepdays)
    deletetime = deletetime.strftime("%Y-%m-%dT%H:%M:%S")
    opcdata_url = f'{maximo_url}/oslc/os/opcdata?lean=1&oslc.pageSize={pagesize}&oslc.select=*&oslc.where=datetime<"{deletetime}"'
    print(f'url : {opcdata_url}')
    
    r = requests.get(opcdata_url,headers=headers_maximo)
    results = r.json()
    data = results["member"]
    print(f'Data fetched : {len(data)} rows')
    backupSuccess = True;
except Exception as e:
    print("Request Error")
    print(e)

#Backup Data to SQLite
try:
    print('start backup to SQLite')
    df = pd.DataFrame(data, columns= ['opcdataid','description','tag','datetime','value','orgid', 'siteid','servername'])
    print(df)
    df.to_sql('opcdata', conn, if_exists='replace', index = False)
    print('end backup to SQLite')
    end = datetime.now()
    endtime = end.strftime("%Y-%m-%dT%H:%M:%S")
    duration = end - start
    print(f'end :  {endtime}')
    print(f'duration : {duration}' )
    
except Exception as e:
    print("Convert to SQLLite Error")
    print(e)

#Delete Maximo Data
try:
    if(backupSuccess):
        opcdatadel_url = f'{maximo_url}/oslc/script/deleteopcdata?days={datakeepdays}'
        r = requests.get(opcdatadel_url,headers=headers_maximo)
        print(r.text)
        print("Delete Success")
    else:
        print("Backup and delete data failed")
except Exception as e:
    print("Delete Error")
    print(e)
