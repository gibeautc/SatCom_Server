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
import filelock
import logging
import os
logging.basicConfig(filename="/home/pi/logs/web_service.log",level=logging.DEBUG)

pidFile="/home/pi/logs/"+os.path.basename(__file__)+".pid"
f=open(pidFile, "w")
f.close()

lock=filelock.FileLock(pidFile)
lock.timeout=1
lock.acquire()

db=MySQLdb.connect('localhost','root','aq12ws','gm')
curs=db.cursor()

locdb=MySQLdb.connect('localhost','root','aq12ws','local')
locCurs=locdb.cursor()

def db_connect():
	global db,curs
	db=MySQLdb.connect('localhost','root','aq12ws','gm')
	curs=db.cursor()

def loc_db_connect():
	global locdb,locCurs
	locdb=MySQLdb.connect('localhost','root','aq12ws','local')
	locCurs=locdb.cursor()


#could add make a gm class to contain these variables
#group ID
group_id=['1523559','27306241','29079593']
#        [    Crew ,bot test ,   boat   ,]

sec_id='0111eaa305c26110dd21040a0a'
sec_test_id='6156eb1065fb54295ea8ae138d'
ariana_id='481baace72a55ebbb9488e296e'


def add_signup(person,event,item):
	db_connect()
	logging.info("Adding to Signup for person: "+person+":"+event+":"+item)
	db_out=[str(person),str(event),str(item)]
	q='insert into signup(person,event,item) values(%s,%s,%s)'
	try:
		curs.execute(q,db_out)
		db.commit()
		#log.debug("entry added for location: "+location)
	except:
		db.rollback()
		logging.error("Error Adding DB entry")
		logging.error(sys.exc_info())
		
		
def add_event(name,date):
	db_connect()
	logging.info("Adding to Event List: "+name+":"+date)
	db_out=[str(name),str(date)]
	q='insert into events(name,ddate) values(%s,%s)'
	try:
		curs.execute(q,db_out)
		db.commit()
	except:
		db.rollback()
		logging.error("Error Adding DB entry")
		logging.error(sys.exc_info())
		
				
def get_event_list():
	q="select name from events"
	curs.execute(q)
	data=curs.fetchall()
	return data
def get_event(event):
	q="select name,ddate,ttime,location from events where id=%s"
	curs.execute(q,(event,))
	data=curs.fetchall()
	return data
def get_signup_for_event(event):
	db.commit()
	q="select person,item from signup where event=%s"
	curs.execute(q,(event,))
	data=curs.fetchall()
	return data
	 

def send_gm(message,bot):
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	logging.debug(f.read())


def Sec_Start(ID,name,message,group):
	logging.debug("In Secretary Mode")
	if group==group_id[0]:
		bot_id=sec_id
	else:
		bot_id=sec_test_id
	if message[0]=='%':
		logging.debug("Got the %")
		if len(message)==1:
			#send the help info
			out="Hello "+name+"\nSend %E to see list of events"
			#out="hello"
			send_gm(out,bot_id)
			return
		if message[1]=="E":
			if len(message)==2:
				events=get_event_list()
				msg=""
				cnt=1
				if events is None:
						send_gm("No Events at this time",bot_id)
						return
				for e in events:
					msg=msg+"("+str(cnt)+")"+str(e[0])+"\n"
					cnt=cnt+1
				logging.debug(msg)
				send_gm(msg,bot_id)
				
				#get list of events
				#give them to user 
				#(1) Name Date
				#(2) Name
				#then say
			elif len(message)==3:
				try:
					event=message[2]
					data=get_event(event)
					#name,ddate,ttime,location
					e=data[0]
					msg=e[0]+" Will be on "+str(e[1])+"\n"
					signlist=get_signup_for_event(event)
					for s in signlist:
						msg=msg+str(s[0])+":"+str(s[1])+"\n"
					#will also need to get signup info and add that
					send_gm(msg,bot_id)
				except:
					logging.warning("Cant get Event info from message")
					send_gm("Cant Get Event Info From Database",bot_id) 
			else:
				#adding to sign up
				try:
					event=message[2]
					what=message[4:]
					logging.info(str(ID)+":"+str(event)+":"+str(what))
					add_signup(name,event,what)
					send_gm("Thanks! you are signed up for:" +what,bot_id)
				except:
					logging.error("Error adding to sign up")
					send_gm("Error Adding to sign up",bot_id)
					logging.error(sys.exc_info())
		if message[1]=='A':
			#adding an event
			if len(message)==2:
				send_gm("To Add event type %A EventName,2017-1-1",bot_id)
				return
			else:
				data=message.split(",")
				name=data[0].split(" ")
				name=name[1]
				date=data[1]
				try:
					add_event(name,date)
					send_gm("Event added:"+name,bot_id)
				except:
					send_gm("Error Adding Event",bot_id)	
def gm_message_rx(request):
	try:
		data=request.json
		logging.debug(data)
		name=data['name']
		ID=data['user_id']
		message=data['text']
		message=str(message)
		groupID=data['group_id']
		name=str(name)
		sender=data['sender_type']
		if sender!='bot':
			logging.debug("Message is: "+message)
			logging.debug("Message from: "+name)
			logging.debug("In Group: "+groupID)
		else:
			return
		if group_id.index(groupID)<2:
			Sec_Start(ID,name,message,groupID)
			return "done",200
		if message[0]=="$":
			logging.debug("got a $")
			if "Chad" in name:
				logging.debug("and its from me")
				#send message to sat
				IMEI='300234064380130'
				NAME="gibeautc@oregonstate.edu"
				PASSWORD='aq12ws'
				DATA=message[1:]
				params=urllib.urlencode({'imei':IMEI,'username':NAME,'password':PASSWORD,'data':DATA.encode("hex")})
				f=urllib.urlopen("https://core.rock7.com/rockblock/MT",params)
				print(f.read())
				logging.debug(str(f.read()))
				#send_gm('Thanks Chad, your message of: "'+DATA+'" has been sent to the que')
			else:
				#not authorized
				try:
					name=name.split(" ")
					name=name[0]
				except:
					name=name
				#send_gm("Sorry "+name+" , you are not authorized to send messages at this time.....please fuck off")
		#print("GM Message from: "+str(name)+" ----:"+str(message))
	except:
		logging.debug("Process GM message Failed")
		logging.debug(request.json)
		logging.error(sys.exc_info())
		
def processApp(request):
    if request.method=="POST":
        logging.debug("Got a POST request from App")
        logging.debug(request.data)
    if request.method=="GET":
        logging.debug("Got a GET request from app")
        logging.debug(request.data)


def processLoc(request):
        jsonData={}
	if request.method=="POST":
		logging.debug("Got a POST request from Local Client: "+str(request.remote_addr))
		#add an ID field and check that against database, use it for how to proceed
		try:
			logging.debug(request.data)
			logging.debug(type(request.data))
			jsonData=json.loads(request.data.replace("'",'"'))
                        #jsonData=request.data
			logging.debug(jsonData)
		
		except:
			logging.error("Getting JSON from local connection failed")
			logging.error(sys.exc_info())
			return
                try:
                    ID=jsonData['ID']

                except:
                    logging.warning("No Id field from Client")
                    return
		stat=jsonData['STATUS']
		if stat=="OFF":
			stat="0"
		if stat=="ON":
			stat="1"
		db_out=[str(jsonData['tempOutSide']),str(jsonData['tempInSide']),str(jsonData['hsTemp']),str(jsonData['SET']),stat]
		q='insert into officeTemp(rec_date,outside,inside,hs,setpoint,status) values(Now(),%s,%s,%s,%s,%s)'
		try:
			logging.debug("Adding Office Temp Entry")
			locCurs.execute(q,db_out)
			locdb.commit()
		except:
			locdb.rollback()
			logging.error("Error Adding DB entry")
			logging.error(sys.exc_info())	
		
		
	if request.method=="GET":
		logging.debug("Got a GET request from Local Client")
		logging.debug(request.data)


					
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
	
