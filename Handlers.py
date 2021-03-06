#!/usr/bin/env python

import logging as log
import urllib
import MySQLdb
import sys
import struct
import binascii
from WeatherAPI import *

dbb=None
cur=None

def dbConnect():
	global dbb,cur
	dbb=MySQLdb.connect('localhost','root','aq12ws','satCom')
	cur=dbb.cursor()
dbConnect()

def send_gm(message):
	#bot='0111eaa305c26110dd21040a0a'	#crew
	bot='b3e83fd81cfbe44a7ea8a22030'	#SatCom
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	try:
		log.debug(f.read())
	except:
		print(f.read())

def sat_message_rx(request,FakeMsg=None):
	#Message coming from sat. Could be an hourly update with or without attached message, or it could be priority message (location should be attached to that as well)
	#assuming message has its own lat/lon   we will use that for groupme. If it doesnt, use the iridium cords but somehow show that its not accurate. 
	#for now will be pushing all messages to groupme, but keep in mind we will want to add support to be able to send messages to another group (emergancy) or even to other platforms
	#facebook, twitter, whatever
	#For hourly/normal updates, once we have the location, we need to pull weather(hourly/daily) for this location, package up the data and send it back out to the sat
	#have hook on SatCom Groupme, any message that starts with a a $ and then is less then 50 char will be sent. For now no restriction, but may want to think about that in the future. 
	try:
		data=request.form['data']
		log.info("Type of Data")
		log.info(type(data))
		msg=data.decode('hex')
		log.info(type(msg))
		momsn=request.form['momsn']
		transmit_time=request.form['transmit_time']
		iridium_lat=request.form['iridium_latitude']
		iridium_lon=request.form['iridium_longitude']
		ir_cep=request.form['iridium_cep']
		log.info("Message Number: "+str(momsn))
		log.info("Lat: "+str(iridium_lat))
		log.info("Lon: "+str(iridium_lon))
		log.info("Accuracy: "+str(ir_cep))
		log.info("Time: "+str(transmit_time))
		log.info("Message: "+str(data))
		log.info("Message Length: "+str(len(data)))
	except:
		log.error("Sat Header Failed")
		log.error(sys.exc_info())
	q="insert into message(id,msg,irLat,irLon,ts,status,troubled) values(%s,%s,%s,%s,now(),0,0)"
	cnt=0
	while cnt<5:	
		try:
			cur.execute(q,[str(momsn),str(data),str(iridium_lat),str(iridium_lon)])
			dbb.commit()
			break
		except:
			log.error("Error Adding DB entry(Message from box)")
			log.error(sys.exc_info())
			cnt=cnt+1
			try:
				dbb.rollback()
			except:
				dbConnect()
				break
			dbConnect()
	#first 4 bytes is lat, next 4 is lon then a byte of warnings and a byte of criticles 
	#This is 10 bytes, if the messge is longer then everthing else is actual text
	if len(msg)<10:
		#This could be because a blank message is send when checking rx, or a bad message
		log.warning("Data is too short:"+str(len(msg))+" : "+msg)
		return	
	else:
		procPayLoad(msg)
	
def procPayLoad(msg):
	log.info("Made it to procPayLload")
	#msg=msg.decode('hex')
	try:
		latData=msg[:4]
		lonData=msg[4:8]
		gpsLat=struct.unpack('f', latData)[0]
		gpsLon=struct.unpack('f', lonData)[0]
		tmsg="Message Received from SatCom: "
		if len(msg)>10:
			tmsg=tmsg+str(msg[10:])
		send_gm(tmsg)		
		if abs(gpsLat)>180 or abs(gpsLon)>180:
			send_gm("Bad GPS Location: "+str(gpsLat)+"  Lon: "+str(gpsLon))
		else:
			send_gm("Actual Location:  Lat: "+str(gpsLat)+"  Lon: "+str(gpsLon))
			try:	
				mapUrl="https://www.google.com/maps/place/"+str(gpsLat)+","+str(gpsLon)
				send_gm(mapUrl)
			except:
				pass
			sat_tx(getData(gpsLat,gpsLon))
		warn=msg[8]
		crit=msg[9]
		if warn>0:
			log.debug("Warning Code:")
			log.debug(str(warn))
			send_gm("Warning Code: "+str(warn))
		if crit>0:
			log.debug("Critical Code:")
			log.debug(str(crit))
			send_gm("Critial Code: "+str(crit))
	except:
		log.error("Failed to process message")
		log.error(sys.exc_info())
		gm_St="Server Failed to Process Message:"+str(msg)
		send_gm(gm_St)

def sat_tx(msg):
	try:
		f=open('satPW','r')
	except:
		log.error("Failed to open Sat Password File")
		return ""	
	fl=f.read().split("\n")
	NAME=fl[0]
	PASSWORD=fl[1]
	IMEI=fl[2]
	params=urllib.urlencode({'imei':IMEI,'username':NAME,'password':PASSWORD,'data':msg})
	f=urllib.urlopen("https://core.rock7.com/rockblock/MT",params)
	resp=f.read()
	return resp

def gm_message_rx(request):
	try:
		data=request.json
		log.debug(data)
		name=data['name']
		ID=data['user_id']
		message=data['text']
		message=str(message)
		groupID=data['group_id']
		name=str(name)
		sender=data['sender_type']
		if sender!='bot':
			log.debug("Message is: "+message)
			log.debug("Message from: "+name)
		else:
			return
		if message[0]=="$":
			logging.debug("got a $")
			logging.debug("and its from me")
			resp=sat_tx(msg[1:].encode('hex'))
			if "OK" in resp:
				send_gm('Thanks '+name+', your message of: "'+DATA+'" has been sent to the queue')
			else:
				logging.eror("Failed to send message")
				logging.error(resp)
				send_gm('Sorry '+name+', there seems to be a problem delivering your message:'+str(resp))
			
	except:
		log.debug("Process GM message Failed")
		log.debug(request.json)
		log.error(sys.exc_info())
		
if __name__=="__main__":
	print("Testing Handlers")
	procPayLoad("a47632428225f6c2800068656c6c6f2077652061726520676f6f64")
