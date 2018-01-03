#!/usr/bin/env python
import requests
import logging as log
import json
print("Starting Client")

log.basicConfig(filename="/home/pi/logs/locClient.log",level=log.DEBUG)

def post_data(ID,names,values):
    if len(names)!=len(values):
        log.error("Names and values are not the same length for post request")
        log.info(names)
        log.info(values)
        return
    jsonData={}
    jsonData["ID"]=ID
    for n in range(len(names)):
        jsonData[names[n]]=values[n]
    jsonData=json.dumps(jsonData)
    r=requests.post("http://10.0.0.149:5050",json=jsonData)
    if r.status_code==200:
        log.debug("Post-200")


post_data("001",["data1","data2"],[1,2])

