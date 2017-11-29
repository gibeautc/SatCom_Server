#!/usr/bin/env python


#port knock listener

import socket
import time

socks=[]
ports =[]
for x in range(10):
	ports.append(8000+x)

for x in range(10):

	socks.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
	socks[x].bind(("10.0.0.149",ports[x]))
	socks[x].setblocking(0)
	socks[x].listen(1)
	print("Listening on: "+str(ports[x]))
	
order=[7,6,2,4]
index=0

ip_list=[]
cur_ip=""
while True:
	#print("Waiting...")
	for x in range(10):
		if index>0:
			if time.time()-t>5:
				print("Timeout")
				cur_ip=""
				index=0
		try:
			# not timeout yet
			connection, client_address = socks[x].accept()
			if connection is None:
				continue
			#print("Got Connection")
			if ports[x]==ports[order[index]]:
				t=time.time()
				#print("Good So far")
				if index==0:
					cur_ip=client_address[0]
					print(client_address[0])
				else:
					if client_address[0]!=cur_ip:
						print("IP changed... Abort")
						cur_ip=""
						index=0
						continue
				index=index+1
				if index==4:
					print("unlock:"+cur_ip)
					cur_ip=""
					index=0
			else:
				print("nope")
				cur_ip=""
				index=0		
		except:
			continue
	
	

