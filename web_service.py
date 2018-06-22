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
import MySQLdb 
import filelock
import logging
import os
from GM import *
from Handlers import *


if os.path.isdir("/home/pi"):
	system="pi"
else:
	system="chadg"
logfile="/home/"+system+"/logs/web_service.log"
logging.basicConfig(filename=logfile,level=logging.DEBUG)

pidFile="/home/"+system+"/logs/"+os.path.basename(__file__)+".pid"
f=open(pidFile, "w")
f.close()

lock=filelock.FileLock(pidFile)
lock.timeout=1
lock.acquire()


app=Flask(__name__)
@app.route('/gmbot1',methods=['GET','POST'])
def gm1():
	logging.debug("GM Bot 1")
	gm_message_rx(request)
	return "done",200
	
@app.route('/gmbot2',methods=['GET','POST'])
def gm2():
	logging.debug("GM Bot 2")
	gm_message_rx(request)
	return "done",200

@app.route('/gmbot3',methods=['GET','POST'])
def gm3():
	logging.debug("GM Bot 3")
	gm_message_rx(request)
	return "done",200

@app.route('/sat',methods=['GET','POST'])
#Message coming from sat. Could be an hourly update with or without attached message, or it could be priority message (location should be attached to that as well)
#assuming message has its own lat/lon   we will use that for groupme. If it doesnt, use the iridium cords but somehow show that its not accurate. 
#for now will be pushing all messages to groupme, but keep in mind we will want to add support to be able to send messages to another group (emergancy) or even to other platforms
#facebook, twitter, whatever

#For hourly/normal updates, once we have the location, we need to pull weather(hourly/daily) for this location, package up the data and send it back out to the sat
#have hook on SatCom Groupme, any message that starts with a a $ and then is less then 50 char will be sent. For now no restriction, but may want to think about that in the future. 
def sat():
	if request.method=='POST':
		logging.debug("got a post at /sat")
		try:
			data=request.form['data']
			data=data.decode('hex')
			momsn=request.form['momsn']
			transmit_time=request.form['transmit_time']
			iridium_lat=request.form['iridium_latitude']
			iridium_lon=request.form['iridium_longitude']
			ir_cep=request.form['iridium_cep']
			logging.info("Message Number: "+str(momsn))
			logging.info("Lat: "+str(iridium_lat))
			logging.info("Lon: "+str(iridium_lon))
			logging.info("Accuracy: "+str(ir_cep))
			logging.info("Time: "+str(transmit_time))
			logging.info("Message: "+str(data))
			if str(data).startswith("$"):
				data=data[1:]#strip off the leading $
				dset=data.split(",")
				Lat=dset[0]
				Lon=dset[1]
				Voltage=dset[2]
				Status=dset[3]
				#need to add bot info to these calls
				#send_gm("Update:\rLat: "+str(Lat)+"\rLon: "+str(Lon)+"\rVoltage: "+str(Voltage)+"\rStatus: "+str(Status))
				#send_gm("http://maps.google.com/maps?q="+str(Lat)+","+str(Lon))
			elif str(data)=="":
				#I think a blank message is sent when tring to retreve a message
				#either way, no need to send a blank message to groupme
				return "done",200	
			else:
				#need to add bot info to these calls
				pass
				#send_gm("Message Received from SatCom: "+str(data))		
				#send_gm("Estimated Location:  Lat: "+str(iridium_lat)+"  Lon: "+str(iridium_lon))
		except:
			logging.error("POST Failed")
		return "done",200


@app.route('/',methods=['GET','POST'])
def index():
		return "done",200
if __name__ == '__main__':
	app.run(debug=False,use_reloader=False, host='0.0.0.0')
	
