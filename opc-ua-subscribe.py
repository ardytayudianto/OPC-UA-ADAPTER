import asyncio
import logging
from datetime import datetime
import json
import requests
import os

from asyncua import Client

from requests.packages.urllib3.exceptions import InsecureRequestWarning

logging.basicConfig(level=logging.ERROR)
_logger = logging.getLogger('asyncua')

requests.adapters.DEFAULT_RETRIES = 5 # increase retries number
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
#s = requests.session()
#s.keep_alive = False # disable keep alive

def sendToMaximo(tag,value,tagtime):
    #Convert Boolean to Decimal
    if(value== True):
        value = 1
    elif(value== False):
        value = 0
    ploadMaximo = { "tag": str(tag),
                    "value": value,
                    "datetime": tagtime,
                    "siteid": siteid,
                    "servername":servername
                  }
    try:
    #send to MX
        maximo_url = config['maximo_url']
        opcdata_url = maximo_url + '/oslc/os/opcdata?lean=1'
        #print(opcdata_url)
        #print(str(ploadMaximo))
        r = requests.post(opcdata_url,data = json.dumps(ploadMaximo),headers=headers_maximo ,verify=False,timeout=5)
        #print(str(r.text))
        print(r.text)
    except Exception as e:
        print(e)
        #_logger.error(str(e))

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def datachange_notification(self, node, val, data):
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        print(now)
        print("======================================")
        print("New data change event", now, str(node), val )
        sendToMaximo(node,val,now)

    def event_notification(self, event):
        print("New event", event)


async def main():
    opc_server_url = opcconfig["serverurl"]
    user = opcconfig["user"]
    if(user is not None):
        opc_server_url = opc_server_url.replace('//','//' + user + '@')
    print(opc_server_url)
    client = Client(url=opc_server_url,timeout=10)
    
    
    client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        
    certificate = f'certificate/mycertificate.der'
    privateKey = f'certificate/myprivatekey.pem'
    
    interval = opcconfig["interval"]
    
    securityMode = opcconfig["securitymode"]
    securityPolicy = opcconfig["securitypolicy"]
    securityString = f"{securityPolicy},{securityMode},{certificate},{privateKey}"
        
    if (securityMode!='None'):
            await client.set_security_string(securityString)
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
        #print("Root node is: %r", client.nodes.root)
        #print("Objects node is: %r", client.nodes.objects)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        #print("Children of root are: %r", await client.nodes.root.get_children())
        
        # subscribing to a variable node
        handler = SubHandler()
        sub = await client.create_subscription(1000*interval, handler)
        for tag in taglist:
            node = client.get_node(tag)
            handle = await sub.subscribe_data_change(node)
        await asyncio.sleep(0.1)

        # we can also subscribe to events from server
        await sub.subscribe_events()
        # await sub.unsubscribe(handle)
        # await sub.delete()

        # calling a method on server
        #res = await obj.call_method("2:multiply", 3, "klk")
        #print("method result is: %r", res)
        while True:
            await asyncio.sleep(1)

#read_config_file
path = os. getcwd()
print("Current path:" + path)
configpath = f'{path}/config.json'
with open(configpath) as config_file:
    config = json.load(config_file)


#get opc configuration
maximo_url = config["maximo_url"]
headers_maximo = config["headers_maximo"]
opc_servername = config["opc_servername"]
maximo_url=config["maximo_url"]

taglist_url = maximo_url + f'/oslc/os/OPCSERVER?lean=1&oslc.where=servername="{opc_servername}"&oslc.select=*'
print("OPC Tag List :")
print(taglist_url)

taglist = []
try:
    #get taglist from maximo
    r = requests.get(taglist_url,headers=headers_maximo)
    results = r.json()
    #print (results)
    #get data from OPCSERVER Object
    for result in results["member"]:
        siteid = (result.get("siteid")) 
        servername = (result.get("servername"))
        serverurl = (result.get("serverurl"))
        interval = (result.get("interval"))
        user = (result.get("user"))
        password = (result.get("password"))
        securitymode = (result.get("securitymode"))
        securitypolicy = (result.get("securitypolicy"))            
        opcconfig = {
            'servername' : servername,
            'serverurl' : serverurl,
            'user' : user,
            'password' : password,
            'siteid' : siteid,
            'interval':interval,
            'securitymode':securitymode,
            'securitypolicy':securitypolicy
            }
        #get data from OPCTAG Object
        for opctag in result["opctag"]:
            tag = (opctag.get("tag"))
            taglist.append(tag)
    print(taglist)
    print("OPC Server Configuration :")
    print(opcconfig)

except Exception as e:
    print("Get Tag List Error")
    print(e)
#end of read_config_file

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main())