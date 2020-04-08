from __future__ import print_function
from socket import *
import datetime

bind = '' #listen on any
port = 12345

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((bind, port))

while True:
    message, address = serverSocket.recvfrom(2048)
    print(datetime.datetime.now(), address, message)
    serverSocket.sendto(message, address)