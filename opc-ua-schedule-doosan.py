import os
import sys
import time
import asyncio
from asyncua import Client
import logging
import requests
import json
#from autopylogger import init_logging
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

import pandas as pd

from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from asyncua.crypto.security_policies import SecurityPolicyBasic128Rsa15
from asyncua.crypto.security_policies import SecurityPolicyBasic256

logging.basicConfig(level=logging.ERROR)
_logger = logging.getLogger("asyncua")

import schedule

def getTag(config):
    _logger.info("Get Tag Start")
    headers_maximo = config["headers_maximo"]
    #print(headers_maximo)
    opc_servername = config["opc_servername"]
    maximo_url=config["maximo_url"]
    taglist_url = maximo_url + f'/oslc/os/OPCSERVER?lean=1&oslc.where=servername="{opc_servername}"&oslc.select=*'
    _logger.info(taglist_url)
    taglist=config["taglist"]
    opcconfig={}
    # try:        
        # r = requests.get(taglist_url,headers=headers_maximo,timeout=5)
        # results = r.json()
        # #print (results)
        # #get data from OPCSERVER Object
        # for result in results["member"]:
            # siteid = (result.get("siteid")) 
            # servername = (result.get("servername"))
            # serverurl = (result.get("serverurl"))
            # interval = (result.get("interval"))
            # user = (result.get("user"))
            # password = (result.get("password"))
            # securitymode = (result.get("securitymode"))
            # securitypolicy = (result.get("securitypolicy"))
            
            # opcconfig = {
                # 'servername' : servername,
                # 'serverurl' : serverurl,
                # 'user' : user,
                # 'password' : password,
                # 'siteid' : siteid,
                # 'interval':interval,
                # 'securitymode':securitymode,
                # 'securitypolicy':securitypolicy
            # }
            # #get data from OPCTAG Object
            # for opctag in result["opctag"]:
                # tag = (opctag.get("tag"))
                # taglist.append(tag)
        # print(taglist,opcconfig)
    # except Exception as e:
        # _logger.info("Get Tag List Error")
        # _logger.info(e)
    # _logger.info("Get Tag End")
    return taglist,opcconfig
 
async def readTag(taglist,opcconfig):
    _logger.info ("Read Tag Start")
    # opc_server_url = opcconfig["serverurl"]
    # user = opcconfig["user"]
    # if(user is not None):
        # opc_server_url = opc_server_url.replace('//','//' + user + '@')
    opcDataList = []
    #_logger.info("opc server url: " + opc_server_url)
    
    opc_server_url = "opc.tcp://admin:admin@10.18.228.10:4841/OpcUaServer_1901"
    user = "admin:admin"
    securityMode = "Sign"
    securityPolicy = "Basic256"
    interval = 10 
    
    client = Client(url=opc_server_url,timeout=10)
        
    try:
        client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        
        certificate = f'certificate/mycertificate.der'
        privateKey = f'certificate/myprivatekey.pem'
        
        #certificate = f'certificate/UaBrowserCert.der'
        #privateKey = f'certificate/UaBrowserPrivateKey.pem'
        
        
        # securityMode = opcconfig["securitymode"]
        # securityPolicy = opcconfig["securitypolicy"]
        # securityString = f"{securityPolicy},{securityMode},{certificate},{privateKey}"
        # #print(securityString)
        
        # if (securityMode!='None'):
            # await client.set_security_string(securityString)
            
        await client.set_security_string("Basic256,Sign,certificate/certificate-example.der,certificate/private-key-example.pem")
    
        # cert_idx = 3
        # cert = f"certificate/peer-certificate-example-{cert_idx}.der"
        # private_key = f"certificate/peer-private-key-example-{cert_idx}.pem"
        
        # await client.set_security(
            # SecurityPolicyBasic256Sha256,
            # certificate=cert,
            # private_key=private_key,
            # server_certificate=f"certificate/certificate-example.der"
        # )        
        
        async with client:
            # Do something with client
            for tag in taglist:
                node = client.get_node(tag)
                value = await node.read_value()
                opcData = []
                opcData.append(tag)
                opcData.append(value)
                opcDataList.append(opcData)
        _logger.info("read result:")
        _logger.info(opcDataList)
        _logger.info("Read Tag End")
    except Exception as e:
        _logger.info("Read Tag Error")
        _logger.info(e) 
    return opcDataList

def sendToMaximo(opcDataList,config,opcconfig):
    _logger.info ("Send Tag to Maximo Start\n")
    maximo_url = config['maximo_url']
    opcdata_url = maximo_url + '/oslc/os/opcdata?lean=1'
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
        #print(name)
        #print(value)
        if(value== True):
            value = 1
        elif(value== False):
            value = 0
        value = value * 1.0
        batch = {   
                    'type' : 'OPC',
                    'batch' : batchtime        
                }
        ploadMaximo = {
                        "servername":servername,
                        #"description": str(batch),
                        "tag": name,
                        "datetime":batchtime,
                        "value": value,
                        "siteid":siteid
                        }
        #print(ploadMaximo)
        try:
            r = requests.post(opcdata_url,data = json.dumps(ploadMaximo),headers=headers_maximo,timeout=5)
            print("===================================================")
            print(str(count)+"#"+r.text)
                
        except Exception as e:
            print("Connection Error")
            print(e)                
    print("Send Tag to Maximo End \n")

def runjob(config,taglist,opcconfig):
    start = datetime.now()
    starttime = start.strftime("%Y-%m-%dT%H:%M:%S")
    opcDataList = asyncio.run(readTag(taglist,opcconfig))
    df = pd.DataFrame(opcDataList,columns=['TAG','VALUE'])
    print(df)
    #print(opcDataList)
    #sendToMaximo(opcDataList,config,opcconfig)
    end = datetime.now()
    endtime = end.strftime("%Y-%m-%dT%H:%M:%S")
    print("count : " + str(len(opcDataList)))
    print("start : " + starttime)
    print("end : " + endtime)
    print("----------------------------------------------------\n")

#Set Logger
path = os. getcwd()
#print("Current path:" + path)
#logger = init_logging(log_name='logs', log_directory=path)
#read Config File
my_os=sys.platform
print("OS in my system : ",my_os)
configpath = f'{path}/configdoosan.json'
with open(configpath) as config_file:
    config = json.load(config_file)

taglist,opcconfig = getTag(config)
#interval = opcconfig["interval"]
interval=10
runjob(config,taglist,opcconfig)
schedule.every(interval).seconds.do(runjob,config,taglist,opcconfig)

while True:
    schedule.run_pending()
    time.sleep(1)
