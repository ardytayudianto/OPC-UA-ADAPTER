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

def sendToMaximo(opcDataList,config):
    print ("Send Tag to Maximo Start")
    maximo_url = config['maximo_url']
    enable_maximo = config["enable_maximo"]
    headers_maximo = config['headers_maximo']
    siteid = config['siteid']
    batchtime = datetime.now()
    batchtime = batchtime.strftime("%Y-%m-%dT%H:%M:%S")
    count=0
    for opcData in opcDataList:
        count=count+1
        name = opcData[0]
        value = opcData[1]
        batch = {   
                    'type' : 'OPC',
                    'batch' : batchtime        
                }
        ploadMaximo = {
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
    print ("Send Tag to Maximo End")

#Set Logger
path = os. getcwd()
#print("Current path:" + path)
logger = init_logging(log_name='logs', log_directory=path)
#read Config File
with open(path + '\\config.json') as config_file:
    config = json.load(config_file)

#interval  = config["interval"]
taglist = getTag(config)
opcDataList = asyncio.run(readTag(taglist))
sendToMaximo(opcDataList,config)