#!/usr/bin/env python
import MySQLdb
import subprocess
import time
from flask import Flask
from flask import request
import requests
import re
import sys
import json
import urllib
import MySQLdb 
from Crypto.PublicKey import RSA
import filelock
import logging
import os

logging.basicConfig(filename="/home/pi/logs/locServer.log",level=logging.DEBUG)

pidFile="/home/pi/logs/"+os.path.basename(__file__)+".pid"
f=open(pidFile,"w")
f.close()
lock=filelock.FileLock(pidFile)
lock.timeout=1
lock.acquire()

db=MySQLdb.connect('localhost','root','aq12ws','local')
curs=db.cursor()

def keyGen():
    key=RSA.generate(1024)
    encrypted_key=key.exportKey(passphrase="")
    f=open("RSA_Key.bin","wb")
    f.write(encrypted_key)
    f.close()
    f=open("RSA_Key_pub.pem",'wb')
    f.write(key.publickey().exportKey())
    f.close()

def loadPrivate(filename):
    f=open(filename,"rb")
    key=RSA.importKey(f.read(),passphrase="")
    return key

def db_connect():
	global db,curs
	db=MySQLdb.connect('localhost','root','aq12ws','local')
	curs=db.cursor()
def decText(data):
    k=loadPrivate("RSA_Key.bin")
    text=k.decrypt(data)
    return text
			
def processPost(data,ip):
    pass

def processGet(data,ip):
    logging.debug("GET from :"+str(ip)+" with data "+str(data))
    return "yep"


def isKnown(ID,IP):
    pass
    #check database for ID,IP combo, if found return true, else return false
    #need to write this
    return True
    #hard coded True will let the whole auth process pass for now

def auth():
    pass
    #need to write this
    #check if data contains the passphrase
    #if not, send specific error code, which will make client send passphrase


app=Flask(__name__)
#@app.route('/gmbot1',methods=['GET','POST'])
#def gm1():
#	logging.debug("GM Bot 1")
#	gm_message_rx(request)
#	return "done",200
	

@app.route('/',methods=['GET','POST'])
def index():
    try:
        data=decText(request.data)
        data=json.loads(data)
    except:
        log.error("Error Decoding Request Data")
        return "Enc Error",401
    try:
        reqId=data['id']
    except:
        log.error("Request does not contain id field")
    if not isKnown(reqId,request.remote_addr):
        auth()
    if request.method=='POST':
        logging.debug("got a POST")
	try:
            processPost(data,request.remote_addr)
	except:
	    logging.debug("Cant process POST")
    if request.method=='GET':
        logging.debug("got a GET")
        try:
            res=processGet(data,request.remote_addr)
            return res
        except:
            logging.debug("Cant process GET JSON")
    return "done",200

if __name__ == '__main__':
       # keyGen()
	app.run(debug=False,use_reloader=False, host='0.0.0.0',port=5050)
	
