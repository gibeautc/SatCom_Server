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
def send_gm(message):
	at="68ea42109ec80134adf205b7f1deccdf"
	test_ID='27306241'
	url_send='https://api.groupme.com/v3/groups/'+test_ID+'/messages?token='+at
	#message='Fuck+off+jason'
	url='https://api.groupme.com/v3/bots/post?bot_id=481baace72a55ebbb9488e296e&text='+message
	print(url)
	r=requests.post(url)
	print(r)
 
app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def index():
	if request.method=='POST':
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
				send_gm("Update:\rLat: "+str(Lat)+"\rLon: "+str(Lon)+"\rVoltage: "+str(Voltage)+"\rStatus: "+str(Status))
				send_gm("http://maps.google.com/maps?q="+str(Lat)+","+str(Lon))
			elif str(data)=="":
				#I think a blank message is sent when tring to retreve a message
				#either way, no need to send a blank message to groupme
				return "done",200	
			else:
				send_gm("Message Received from SatCom: "+str(data))		
				send_gm("Estimated Location:  Lat: "+str(iridium_lat)+"  Lon: "+str(iridium_lon))
		except:
			try:
				o=open('/home/pi/SatCom_Server/WS_out','w')
				data=request.json
				name=data['name']
				message=data['text']
				name=str(name)
				message=str(message)
				if message[0]=="$":
					o.write("got a $\n")
					if "Chad" in name:
						o.write("and its from me\n")
						#send message to sat
						IMEI='300234064380130'
						NAME="gibeautc@oregonstate.edu"
						PASSWORD='aq12ws'
						DATA=message[1:]
						params=urllib.urlencode({'imei':IMEI,'username':NAME,'password':PASSWORD,'data':DATA.encode("hex")})
						f=urllib.urlopen("https://core.rock7.com/rockblock/MT",params)
						print(f.read())
						o.write(str(f.read()))
						send_gm('Thanks Chad, your message of: "'+DATA+'" has been sent to the que')
					else:
						#not authorized
						try:
							name=name.split(" ")
							name=name[0]
						except:
							name=name
						send_gm("Sorry "+name+" , you are not authorized to send messages at this time.....please fuck off")
				#print("GM Message from: "+str(name)+" ----:"+str(message))
				o.close()
			except:
				o.write("Failed 1")
				o.close()
		
		return "done",200
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
