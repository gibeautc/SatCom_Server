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


import logging
logging.basicConfig(filename="/home/pi/logs/locServer.log",level=logging.DEBUG)



db=MySQLdb.connect('localhost','root','aq12ws','local')
curs=db.cursor()


def db_connect():
	global db,curs
	db=MySQLdb.connect('localhost','root','aq12ws','local')
	curs=db.cursor()

					
app=Flask(__name__)
#@app.route('/gmbot1',methods=['GET','POST'])
#def gm1():
#	logging.debug("GM Bot 1")
#	gm_message_rx(request)
#	return "done",200
	

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        logging.debug("got a POST")
	try:
	    logging.debug(request.json)
	except:
	    logging.debug("Cant process POST JSON")
    if request.method=='GET':
        logging.debug("got a GET")
        try:
            logging.debug(request.json)
        except:
            logging.debug("Cant process GET JSON")
    return "done",200

if __name__ == '__main__':
	app.run(debug=False,use_reloader=True, host='0.0.0.0',port=5050)
	
