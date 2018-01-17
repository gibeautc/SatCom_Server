#!/usr/bin/env python
import socket
import time
from threading import Thread, Lock
from multiprocessing import Queue
import select

mainPipe=Queue(100)

mainLock=Lock() #used to lock mainPipe if needed
sockListLock=Lock()
sockList=[]
portList=[]
portListLock=Lock()

for x in range(50):
	portList.append(5051+x)

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
			log("No Active Sockets")
			time.sleep(5)
			continue
		if not p.empty():
			log(p.get())
		for s in sockList:
			if time.time()-s.lastMsg>20:
				log("Closing Thread with id: "+str(s.ID))
				portListLock.acquire()
				portList.append(s.port)
				portListLock.release()
				sockListLock.acquire()
				sockList.remove(s)
				sockListLock.release()
				
				
		#check for sockets to read from
		#make sure to aquire lock before messing with socklist


def clientSet(clientsoc):
	global sockList,sockListLock
	print("Got new Client:")
	#send them new socket number, let them close this socket.
	#setup new socket, wait for connect, then return new socket 
	singSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	portListLock.acquire()
	for x in portList:
		try:
			p=x
			print("Tring Port: "+str(p))
			#time.sleep(.1)
			singSock.bind(("10.0.0.149", p))
			print("Binding Successfull")
			portList.remove(x)
			break		
		except:
			print("Port "+str(p)+" in use (or other error)")
			continue
	portListLock.release()
	tmpId=clientsoc.recv(5)
	print("ID recv from client: "+str(tmpId))
	clientsoc.send(str(p))
	clientsoc.close()
	singSock.listen(1)
	(cl,addr)=singSock.accept()
	print("Address:"+str(addr))
	tmpClient=client(tmpId,mainPipe)
	tmpClient.port=p
	tmpClient.soc=cl
	tmpClient.start()
	print("Got Lock, adding to list")
	sockListLock.acquire()
	sockList.append(tmpClient)
	sockListLock.release()
	
	return


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
    
    
    
    
    
