from java.util import HashMap,Calendar
from com.ibm.json.java import JSONObject
from psdi.util.logging import MXLoggerFactory
from java.text import SimpleDateFormat
from psdi.iface.router import HTTPHandler
from java.lang import String

logger = MXLoggerFactory.getLogger("maximo.autoscript")

#time format"2022-08-12T11:20:11.110000+07:00"


def sendHttp(body,headers,url):
    handler = HTTPHandler()
    map = HashMap()
    map.put("URL",url)
    map.put("HEADERS",headers)
    map.put("HTTPMETHOD","POST")
    
    responseBytes = handler.invoke(map,body)
    response = String(responseBytes,"utf-8")
    #logger.info("response: " + str(response))
    return response

map = HashMap()

#getData
servername = mbo.getString('SERVERNAME')
serverurl = mbo.getString('OPCTAG.OPCSERVER.SERVERURL')
tag = mbo.getString('TAG')
tagdescription = mbo.getString('OPCTAG.DESCRIPTION')
value = mbo.getDouble('VALUE')
timestamp = mbo.getDate('DATETIME')
format_timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(timestamp)
format_timestamp = format_timestamp.replace(' ','T')+"+07:00"

bodyPayload = {
    "servername": servername,
    "serverurl": serverurl,
    "tag": tag,
    "description" : tagdescription,
    "value": value,
    "timestamp": format_timestamp
}

body = JSONObject()
body.put("servername",servername)
body.put("serverurl",serverurl)
body.put("tag",tag)
body.put("description",tagdescription)
body.put("value",value)
body.put("timestamp",format_timestamp)
bodyStr = body.serialize(True)
logger.info(str(bodyPayload))
logger.info(bodyStr)


headers = "Authorization:Basic ZWxhc3RpYzpCMFBWbUNwcllsUnZ5SHh6RzdzNw==,Content-Type:application/json"
url="https://147.139.132.238:9200/opcdata/_doc/"


try:
    #response=service.invokeEndpoint("ELASTICHTTP",map,str(bodyPayload))
    #body = JSONObject.parse(response)
    #logger.info(str(body))
    response = sendHttp(bodyStr,headers,url)
    logger.info(response)
    
except Exception as e:
    logger.info('Error Send To Elastic')
    logger.info(e)