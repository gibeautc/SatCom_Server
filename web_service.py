#!/usr/bin/env python
import subprocess
import time
from flask import Flask
from flask import request
import requests
import re
import sys
import json
import urllib
import filelock
import logging
import os
from Handlers import *
from WeatherAPI import *

logfile="/root/logs/web_service.log"
logging.basicConfig(filename=logfile,level=logging.DEBUG)

pidFile="/root/logs/"+os.path.basename(__file__)+".pid"
f=open(pidFile, "w")
f.close()

lock=filelock.FileLock(pidFile)
lock.timeout=1
lock.acquire()


app=Flask(__name__)
@app.route('/gmbot',methods=['GET','POST'])
def gm1():
	logging.debug("GM Bot 1")
	gm_message_rx(request)
	return "done",200
	
@app.route('/sat',methods=['GET','POST'])
def sat():
	if request.method=='POST':
		logging.debug("got a post at /sat")
		sat_message_rx(request)
		return "done",200


@app.route('/',methods=['GET','POST'])
def index():
		return "done",200
if __name__ == '__main__':
	app.run(debug=False,use_reloader=False, host='0.0.0.0')
	
