#!/usr/bin/env python
import socket
import time
from threading import Thread, Lock


sockListLock=Lock()
sockList=[]
for x in range(50):
	portNum=5001+x
	portList.append(portNum)

class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None):
		self.ID=None
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)


	

def rxThread():
	print("RX-Threading Starting")
	while True:
		print("Checking")
		#check for sockets to read from
		#make sure to aquire lock before messing with socklist
		time.sleep(5)


def clientSet(soc):
	global sockList,sockListLock
	print("Switching Client off main socket")
	#send them new socket number, let them close this socket.
	#setup new socket, wait for connect, then return new socket 
	for x in range(100):
		try:
			p=5001+x
			print("Tring Port: "+str(p))
			soc.mysend(str(p))
			singSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			singSock.bind(("10.0.0.149", p))
			singSock.listen(1)
			(cl,addr)=singSock.accept()
			print(str(addr)+" Connected to OWN socket")
			sockListLock.aquire()
			print("Got Lock, adding to list")
			sockList.append(singSock)
			sockListLock.release()
			return



serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("10.0.0.149", 5050))
print("Init Socket Setup")
serversocket.listen(5)
rx=Thread(target=rxThread)
rx.daemon=True
rx.start()

while 1:
	print("Listening for clients")
	#this blocks, so need to launch thread for interacting with open sockets
	(clientsocket, address) = serversocket.accept()
	print("Got one")
	t=Thread(target=clientSet,args=(clientsocket,))
	t.daemon=True
	t.start()
    
    
    
    
    
