#!/usr/bin/env python
import requests
import logging as log
import json
from Crypto.PublicKey import RSA

print("Starting Client")

log.basicConfig(filename="/home/pi/logs/locClient.log",level=log.DEBUG)

def loadPub(filename):
    k=RSA.importKey(open(filename).read())
    return k

def post_data(ID,names,values,key):
    if len(names)!=len(values):
        log.error("Names and values are not the same length for post request")
        log.info(names)
        log.info(values)
        return
    jsonData={}
    jsonData["ID"]=ID
    for n in range(len(names)):
        jsonData[names[n]]=values[n]
    encData=key.encrypt(str(jsonData),32)
    log.debug("Trying to send:")
    log.debug(jsonData)
    log.debug("with Length: "+str(len(encData)))
    
    r=requests.post("http://10.0.0.149:5050",encData[0])
    if r.status_code==200:
        log.debug("Post-200")

def get_data(key):
    encData=key.encrypt("MYID",32)
    r=requests.get("http://10.0.0.149:5050",data=encData[0])
    log.debug(r.text)


k=loadPub("RSA_Key_pub.pem")
#post_data("001",["data1","data2"],[1,2],k)
get_data(k)
