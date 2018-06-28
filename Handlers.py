#!/usr/bin/env python

import logging
import urllib
import MySQLdb
dbb=MySQLdb.connect('localhost','root','aq12ws','satCom')
cur=dbb.cursor()

def send_gm(message):
	bot='0111eaa305c26110dd21040a0a'	#real
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	log.debug(f.read())

def sat_message_rx(request):
	#Message coming from sat. Could be an hourly update with or without attached message, or it could be priority message (location should be attached to that as well)
	#assuming message has its own lat/lon   we will use that for groupme. If it doesnt, use the iridium cords but somehow show that its not accurate. 
	#for now will be pushing all messages to groupme, but keep in mind we will want to add support to be able to send messages to another group (emergancy) or even to other platforms
	#facebook, twitter, whatever

	#For hourly/normal updates, once we have the location, we need to pull weather(hourly/daily) for this location, package up the data and send it back out to the sat
	#have hook on SatCom Groupme, any message that starts with a a $ and then is less then 50 char will be sent. For now no restriction, but may want to think about that in the future. 
	try:
		data=request.form['data']
		logging.info("Type of Data")
		logging.info(type(data))
		msg=data.decode('hex')
		logging.info(type(msg))
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
		q="insert into messages(id,msg,irLat,irLon,ts,status,troubled) values(%s,%s,%s,%s,now(),0,0)"
		try:
			cur.execute(q,[str(momsn),str(msg),str(iridium_lat),str(iridium_lon)])
			dbb.commit()
			#log.debug("entry added for location: "+location)
		except:
			dbb.rollback()
			logging.error("Error Adding DB entry(Forecast)")
			logging.error(sys.exc_info())
		#first 4 bytes is lat, next 4 is lon then a byte of warnings and a byte of criticles 
		#This is 10 bytes, if the messge is longer then everthing else is actual text
		if len(msg)<10:
			#This could be because a blank message is send when checking rx, or a bad message
			logging.warning("Data is too short")
			return	
		else:
			locData=msg[:10]
			locData=bytearray.fromhex(locData)
			gpsLat=struct.unpack('f', locData[:4])
			gpsLon=struct.unpack('f', locData[4:8])
			warn=locData[8]
			crit=locData[9]
			tmsg="Message Received from SatCom: "
			if len(msg)>10:
				tmsg=tmsg+str(msg[10:])
			send_gm(tmsg)		
			send_gm("Estimated Location:  Lat: "+str(iridium_lat)+"  Lon: "+str(iridium_lon))
			send_gm("Actual Location:  Lat: "+str(gpsLat)+"  Lon: "+str(gpsLon))
	except:
		logging.error("POST Failed")
		logging.error(sys.exc_info())

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
				send_gm('Thanks Chad, your message of: "'+DATA+'" has been sent to the que')
			else:
				try:
					name=name.split(" ")
					name=name[0]
				except:
					name=name
				send_gm("Sorry "+name+" , you are not authorized to send messages at this time.....please fuck off")
	except:
		logging.debug("Process GM message Failed")
		logging.debug(request.json)
		logging.error(sys.exc_info())
		
if __name__=="__main__":
	print("Testing Handlers")
