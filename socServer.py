#!/usr/bin/env python
import socket
import time
from threading import Thread, Lock
from multiprocessing import Queue
import select
import sys

mainPipe=Queue(100)

mainLock=Lock() #used to lock mainPipe if needed
sockListLock=Lock()
sockList=[]
portList=[]
portListLock=Lock()
originPortList=[]
for x in range(100):
	portList.append(5051+x)
	originPortList.append(5051+x)
class client(Thread):
	def __init__(self,ID,q):
		Thread.__init__(self)
		self.soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setblocking(0)
		self.ID=ID
		self.port=0
		self.daemon=True
		self.ownPipe=Queue(10)
		self.mainPipe=q
		self.lastMsg=time.time()
		self.log="(client:"+self.ID+")"
	def prt(self,msg):
		print(self.log+str(msg))
	def checkMsg(self,buf):
		#self.prt("Mesage Received")
		#print(''.join(buf))
		self.mainPipe.put(''.join(buf))
		
	def run(self):
		self.prt("Connected to Own Socket Now")
		rxBuf=[]
		self.prt("Connected to OWN socket")
		while True:
			#try:
			rxBuf.append(self.soc.recv(1))
			#except:
			#	continue
			if len(rxBuf)==0:
				self.prt("HERE")
				continue
			if "\n" in rxBuf:
				self.checkMsg(rxBuf)
				del rxBuf[:]
				self.lastMsg=time.time()
		
	
def rxThread(p):
	def log(msg):
		print("(rxThread)"+str(msg))
	global sockList	
	log("Starting")
	while True:
		if len(sockList)==0:
			time.sleep(5)
			continue
		if not p.empty():
			log(p.get())
		#this seems to improve cpu usegae, but trying to track down a timing problem
		#else:
		#	time.sleep(1)
		for s in sockList:
			if time.time()-s.lastMsg>20:
				log("Closing Thread with id: "+str(s.ID))
				portListLock.acquire()
				log("Got Port Lock")
				portList.append(s.port)
				portListLock.release()
				log("Release Port Lock")
				sockListLock.acquire()
				log("Got sock Lock")
				sockList.remove(s)
				sockListLock.release()
				log("Release Sock Lock")
				
				
		#check for sockets to read from
		#make sure to aquire lock before messing with socklist


def clientSet(clientsoc):
	def log(msg):
		print("(clientSetThread)"+str(msg))
	global sockList,sockListLock
	log("Got new Client:")
	#send them new socket number, let them close this socket.
	#setup new socket, wait for connect, then return new socket 
	singSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	for x in portList:
		try:
			p=x
			log("Tring Port: "+str(p))
			#time.sleep(.1)
			portListLock.acquire()
			singSock.bind(("10.0.0.149", p))
			log("Binding Successfull")
			portList.remove(x)
			portListLock.release()
			break		
		except:
			log("Port "+str(p)+" in use (or other error)")
			portListLock.release()
			continue
	
	try:
		#incase p wasnt assigned to anything
		dump=p
	except:
		return
	tmpId=clientsoc.recv(5)
	log("ID recv from client: "+str(tmpId))
	clientsoc.send(str(p))
	clientsoc.close()
	singSock.listen(1)
	(cl,addr)=singSock.accept()
	log("Address:"+str(addr))
	tmpClient=client(tmpId,mainPipe)
	tmpClient.port=p
	tmpClient.soc=cl
	tmpClient.start()
	log("Got Lock, adding to list")
	sockListLock.acquire()
	sockList.append(tmpClient)
	sockListLock.release()
	log("Releasing Lock")
	
	return

def mon():
	while True:
		f=open("SocServerMon","a")
		idlist=[]
		usedPorts=[]
		for s in sockList:
			idlist.append(int(s.ID))
			usedPorts.append(s.port)
		idlist.sort()
		usedPorts.sort()
		portListLock.acquire()
		tmp=0
		try:
			del portList[:]
			for p in originPortList:
				portList.append(p)
			for p in usedPorts:
				tmp=p
				portList.remove(p)
		except:
			f.write("Failed to reset PortList: "+str(tmp)+"\n")
			f.write(str(sys.exc_info()))
			f.write("\n")
		portList.sort()
		portListLock.release()
		
		f.write("Active Clients: "+str(len(sockList))+"\n")
		f.write("Ports Left    : "+str(len(portList))+"\n")
		f.write("ID's\n")
		f.write(str(idlist))
		f.write("\n")
		f.write("Used ports\n")
		f.write(str(usedPorts))
		f.write("\n")
		f.write("Free ports\n")
		f.write(str(portList))
		f.write("\n")
		
		f.close()
		time.sleep(5)


mon=Thread(target=mon)
mon.daemon=True
mon.start()

while True:
	try:
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind(("10.0.0.149", 5050))
		print("Init Socket Setup")
		serversocket.listen(5)
		rx=Thread(target=rxThread,args=(mainPipe,))
		#rx thread is what will check clients for input and deal with passing it around
		rx.daemon=True
		rx.start()
		break
	except:
		serversocket.close()
		print("Port Busy....")
		time.sleep(5)

#main loop only listens for new connections, launch thread to connect new client
while 1:
	print("Listening for clients")
	(clientsocket, address) = serversocket.accept()
	t=Thread(target=clientSet,args=(clientsocket,))
	t.daemon=True
	t.start()
    
    
    
    
    
