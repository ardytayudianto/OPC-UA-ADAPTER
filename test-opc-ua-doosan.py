import select
import socket
import os
import sys

import logging
import asyncio
from asyncua import Client
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from asyncua.crypto.security_policies import SecurityPolicyBasic256

async def main():
    opcurl = "opc.tcp://admin:admin@10.18.228.10:4841/OpcUaServer_1901"
    print(opcurl)
    
    client = Client(url=opcurl)
    print(client)
    cert = f"certificates\peer-certificate-example-3.der"
    private_key = f"certificates\peer-certificate-example-3.der"
    
    server_cert = f"uaservercpp.der"
    
    #await client.set_security(
    #    SecurityPolicyBasic256,
    #    certificate=cert,
    #    private_key=private_key,
    #    server_certificate= server_cert
    #)
    #client.application_uri = "urn:LAPTOP-V2NQ6PL3:Mitsubishi:MX OPC Server UA"
    client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
    
    client.session_timeout = 2000
    #client = Client("opc.tcp://localhost:53530/OPCUA/SimulationServer/")
    #client.load_client_certificate(cert)
    #client.load_private_key(private_key)
    await client.set_security_string("Basic256,Sign,certificate/certificate-example.der,certificate/private-key-example.pem")
    """
        Set SecureConnection mode.
        :param string: Mode format ``Policy,Mode,certificate,private_key[,server_private_key]``
        where:
        - ``Policy`` is ``Basic128Rsa15``, ``Basic256`` or ``Basic256Sha256``
        - ``Mode`` is ``Sign`` or ``SignAndEncrypt``
        - ``certificate`` and ``server_private_key`` are paths to ``.pem`` or ``.der`` files
        - ``private_key`` may be a path to a ``.pem`` or ``.der`` file or a conjunction of ``path``::``password`` where
          ``password`` is the private key password.
        Call this before connect()
    """   
    async with client:
        tag = 'ns=2;s=P0BBF01GH001||XQ21'               

        node = client.get_node(tag)
        value = await node.read_value()
        print(tag)
        print(value)
        #root = client.nodes.root
        #objects = client.nodes.objects
        #while True:
        #    print("childs og objects are: ", await objects.get_children())
        #   await asyncio.sleep(1)



if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    asyncio.run(main())
