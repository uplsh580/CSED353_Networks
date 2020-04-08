from __future__ import print_function
from socket import *
import datetime

bind = '' #listen on any
port = 12345

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((bind, port))
print("Host: ",bind , " Port: ", port)

while True:
    message, address = serverSocket.recvfrom(2048)
    print(datetime.datetime.now())
    print("Receive from", address, message.decode())
    serverSocket.sendto("pong".encode(), address)