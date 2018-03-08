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
from Handler import *
logging.basicConfig(filename="/home/pi/logs/web_service.log",level=logging.DEBUG)

pidFile="/home/pi/logs/"+os.path.basename(__file__)+".pid"
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

@app.route('/app',methods=['GET','POST'])
def APP():
    logging.debug("Message from App")
    processApp(request)
    return "done",200


@app.route('/loc',methods=['GET','POST'])
def loc():
	logging.debug("Message from Local Client")
	processLoc(request)
	
		
	return "done",200

@app.route('/wx',methods=['GET','POST'])
def wx():
	logging.debug("Message from Local Client")
	return processWxReq(request)
	return "done",200


@app.route('/',methods=['GET','POST'])
def index():
	if request.method=='POST':
		logging.debug("got a post")
		#try:
		#	logging.debug(request.json)
		#except:
		#	logging.debug("Cant Print Request Json")
		try:
			data=request.form['data']
			data=data.decode('hex')
			momsn=request.form['momsn']
			transmit_time=request.form['transmit_time']
			iridium_lat=request.form['iridium_latitude']
			iridium_lon=request.form['iridium_longitude']
			ir_cep=request.form['iridium_cep']
			print("Message Number: "+str(momsn))
			print("Lat: "+str(iridium_lat))
			print("Lon: "+str(iridium_lon))
			print("Accuracy: "+str(ir_cep))
			print("Time: "+str(transmit_time))
			print("Message: "+str(data))
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
if __name__ == '__main__':
	app.run(debug=False,use_reloader=False, host='0.0.0.0')
	
