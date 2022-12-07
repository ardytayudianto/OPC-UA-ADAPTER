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
        r = requests.get(taglist_url,headers=headers_maximo)
        results = r.json()
        #print (results)
        #get data from OPCSERVER Object
        for result in results["member"]:
            siteid = (result.get("siteid")) 
            servername = (result.get("servername")) 
            interval = (result.get("interval")) 
            opcconfig = {
            'servername' : servername,
            'siteid' : siteid,
            'interval':interval                    
            }
            #get data from OPCTAG Object
            for opctag in result["opctag"]:
                tag = (opctag.get("tag"))
                taglist.append(tag)
        print(taglist,opcconfig)
    except:
        print("Get Tag List Error")
    print ("Get Tag End",'\n')
    return taglist,opcconfig
 
async def readTag(taglist):
    print ("Read Tag Start")
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
    print ("Read Tag End",'\n')
    return opcDataList

def sendToMaximo(opcDataList,config,opcconfig):
    print ("Send Tag to Maximo Start\n")
    maximo_url = config['maximo_url']
    enable_maximo = config["enable_maximo"]
    headers_maximo = config['headers_maximo']
    batchtime = datetime.now()
    batchtime = batchtime.strftime("%Y-%m-%dT%H:%M:%S")
    count=0
    siteid = opcconfig["siteid"]
    servername = opcconfig["servername"]
    for opcData in opcDataList:
        count=count+1
        name = opcData[0]
        value = opcData[1]
        #Convert Boolean to Decimal
        if(value== True):
            value = 1
        elif(value== False):
            value = 0
        batch = {   
                    'type' : 'OPC',
                    'batch' : batchtime        
                }
        ploadMaximo = {
                        "servername":servername,
                        "description": str(batch),
                        "tag": name,
                        "datetime":batchtime,
                        "value": value,
                        "siteid":siteid
                        }
        if(enable_maximo):
            try:
                #Send to DEV
                r = requests.post(maximo_url,data = json.dumps(ploadMaximo),headers=headers_maximo)
                logger.info(str(count)+"#"+r.text)
            except:
                logger.info("Connection error")
        else:
            logger.info(ploadMaximo)
    print ("Send Tag to Maximo End \n")

def runjob(config,taglist,opcconfig):
    start = datetime.now()
    starttime = start.strftime("%Y-%m-%dT%H:%M:%S")
    opcDataList = asyncio.run(readTag(taglist))
    #print(opcDataList)
    sendToMaximo(opcDataList,config,opcconfig)
    end = datetime.now()
    endtime = end.strftime("%Y-%m-%dT%H:%M:%S")
    print("count : " + str(len(opcDataList)))
    print("start : " + starttime)
    print("end : " + endtime)
    print("----------------------------------------------------\n")

#Set Logger
path = os. getcwd()
#print("Current path:" + path)
logger = init_logging(log_name='logs', log_directory=path)
#read Config File
with open(path + '\\config.json') as config_file:
    config = json.load(config_file)

taglist,opcconfig = getTag(config)
interval = opcconfig["interval"]
runjob(config,taglist,opcconfig)
schedule.every(interval).seconds.do(runjob,config,taglist,opcconfig)

while True:
    schedule.run_pending()
    time.sleep(1)
