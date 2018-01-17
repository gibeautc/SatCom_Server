#!/usr/bin/env python
import time
import socket
import sys

class soc:
    
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def tx(self, msg):
		totalsent = 0
		while totalsent < len(msg):
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent = totalsent + sent
		#print(totalsent)

    def rx(self,MSGLEN):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)

def connect():
	try:
		con=soc()
		con.connect("10.0.0.149",5050)
		s=con.tx(str(ID))
		s=con.rx(4)
		print("Got new Port number: "+str(s))
		newcon=soc()
	except:
		print("Server Not Reachable")
		time.sleep(5)
		return None
	while True:
		try:
			#time.sleep(2)
			newcon.connect("10.0.0.149",int(s))
			break
		except:
			print("Connection ERROR")
			return None
	return newcon


if len(sys.argv)<2:
	print("Need an ID to start client.....")
	exit()
ID=sys.argv[1]
print("I am client: "+str(ID))


c=connect()
while True:
	while c is None:
		c=None
		c=connect()
	try:
		#print("Client: "+str(ID)+" running")
		c.tx("{'ID':"+str(ID)+"}\n")
		time.sleep(10)
	except:
		c=connect()
	



