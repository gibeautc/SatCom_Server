#!/usr/bin/env python

import logging
import MySQLdb
import time

locdb=MySQLdb.connect('localhost','root','aq12ws','local')
locCurs=locdb.cursor()

wxdb=MySQLdb.connect('localhost','root','aq12ws','weather')
wxCurs=wxdb.cursor()

def findLocation():
	#need a valid loction ID from database, we have lat and long
	#in request data. Pull all locations, check if there is one that has
	#an acceptable distance   say 5 Miles?
	#if we have one return the ID, if not we need to add it in (with rec of 1)
	# and return new ID

def loc_db_connect():
	global locdb,locCurs
	locdb=MySQLdb.connect('localhost','root','aq12ws','local')
	locCurs=locdb.cursor()


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

def processWxReq(request):
	if request.method=="POST":
		logging.debug(request.data)
		#data={
	if request.method=="GET":
		logging.debug(request.data)
		#this should contain location information
	time.sleep(10)
	return "{hi:1}",200
		

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
