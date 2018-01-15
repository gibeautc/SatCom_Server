#!/usr/bin/env python
import socket
import time
from threading import Thread, Lock
from multiprocessing import Pipe
import select

mainPipe=Pipe()
mainLock=Lock() #used to lock mainPipe if needed
sockListLock=Lock()
sockList=[]

class client(Thread):
	def __init__(self,ID,q):
		Thread.__init__(self)
		self.soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ID=ID
		self.daemon=True
		self.ownPipe=Pipe()
		self.mainPipe=q
		self.log="(client:"+self.ID+")"
	def prt(self,msg):
		print(self.log+str(msg))
	def checkMsg(buf):
		self.prt("Mesage Received")
		print(''.join(buf))
		
	def run(self):
		socket_list=[]
		socket_list.append(self.soc)
		self.soc.listen(1)
		rxBuf=[]
		(cl,addr)=self.soc.accept()
		self.prt("Connected to OWN socket")
		while True:
			self.prt("Hello!")
			read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [],1)
			if read_sockets is None:
				self.prt("Nothing to Read")
			for s in read_sockets:
				rxBuf.append(s.recv(1))
				self.prt("Buffer: "+str(rxBuf))
			if len(rxBuf)==0:
				continue
			if rxBuf[len(rxBuf)-1]=="}":
				self.checkMsg(rxBuf)
				del rxBuf[:]
		
	
def rxThread():
	def log(msg):
		print("(rxThread)"+msg)
	global sockList	
	log("Starting")
	while True:
		time.sleep(5)
		if len(sockList)==0:
			log("No Active Sockets")
			continue
		log("Checking")
		#check for sockets to read from
		#make sure to aquire lock before messing with socklist


def clientSet(clientsoc):
	global sockList,sockListLock
	print("Got new Client:")
	#send them new socket number, let them close this socket.
	#setup new socket, wait for connect, then return new socket 
	singSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	for x in range(5):
		try:
			p=5051+x
			print("Tring Port: "+str(p))
			time.sleep(2)
			singSock.bind(("10.0.0.149", p))
			print("Binding Successfull")
			break		
		except:
			print("Port "+str(p)+" in use (or other error)")
			continue
	tmpId=clientsoc.recv(5)
	print("ID recv from client: "+str(tmpId))
	clientsoc.send(str(p))
	clientsoc.close()
	tmpClient=client(tmpId,mainPipe)
	tmpClient.soc=singSock
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
		rx=Thread(target=rxThread)
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
    
    
    
    
    
