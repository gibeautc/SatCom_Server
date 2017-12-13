#!/usr/bin/env python
import BaseHTTPServer,SimpleHTTPServer
import ssl
import os
os.chdir("/var/www/html")
httpd=BaseHTTPServer.HTTPServer(('10.0.0.149',4443),SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket=ssl.wrap_socket (httpd.socket,certfile='/home/pi/SatCom_Server/server.pem',server_side=True)
httpd.serve_forever()

