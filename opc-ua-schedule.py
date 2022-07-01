import select
import socket
import os
import sys
import time
#import OpenOPC
import asyncio
from asyncua import Client

import requests
import json
import pywintypes
import win32timezone
from autopylogger import init_logging
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

import schedule

def getTag(config):
    print ("Get Tag Start")
    headers_maximo = config["headers_maximo"]
    #print(headers_maximo)
    taglist=[]
    try:
        taglist_url = config["taglist_url"]
        #print(taglist_url)
        r = requests.get(taglist_url,headers=headers_maximo)
        results = r.json()
        #print (results)
        for result in results["rdfs:member"]:
            tag = (result.get("spi:tag"))
            taglist.append(tag)
        print(taglist)
    except:
        print("Get Tag List Error")
    print ("Get Tag End")
    return taglist
 
async def readTag(taglist):
    opc_server_url = config["opc_server_url"]
    opcDataList = []
    async with Client(url=opc_server_url) as client:
        # Do something with client
        for tag in taglist:
            node = client.get_node(tag)
            value = await node.read_value()
            opcData = []
            opcData.append(tag)
            opcData.append(value)
            opcDataList.append(opcData)
    print(opcDataList)
    return opcDataList

#Set Logger
path = os. getcwd()
#print("Current path:" + path)
logger = init_logging(log_name='logs', log_directory=path)
#read Config File
with open(path + '\\config.json') as config_file:
    config = json.load(config_file)

#interval  = config["interval"]
taglist = getTag(config)
asyncio.run(readTag(taglist))
'''   
runjob(config,opcconfig,taglist)
schedule.every(interval).minutes.do(runjob,config,opcconfig,taglist)
#runjob(config)

while True:
    schedule.run_pending()
    time.sleep(1)
'''