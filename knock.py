#!/usr/bin/env python

import socket
import sys
import time

ports=[]
for x in range(10):
	ports.append(8000+x)

order=[7,6,2,4]

for x in order:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("10.0.0.149",ports[x]))
	time.sleep(.5)
	sock.close()
