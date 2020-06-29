import argparse
from socket import *
import sys
import os

#Connect Info valuable
connect_username = None
connect_hostname = None
connect_hostport = None

#Parser
parser = argparse.ArgumentParser()
parser.add_argument("server", help="connect server ip : 'username@addrhostnameess'", type=str)
parser.add_argument("-p", "--port", help="connect server port, default is 22", type=int, default=22)

def server_arg_check(server_str):
    if "@" not in server_str:
        print("[Custom_Error_35300] : '{}' is wrong argument({}) pattern.".format(server_str, "server"))
        print("You should type 'id@address' format.")
        exit()
    else:
        connect_id, connect_address = tuple(server_str.split("@"))
        return connect_id, connect_address
    
def print_connect_info():
    print("-----------Connect Info-----------")
    print("Connect User Name | {}".format(connect_username))
    print("Connect Host Name | {}".format(connect_hostname))
    print("Connect Host Port | {}".format(connect_hostport))
    print("----------------------------------")

if __name__ == "__main__":
    #Start sftp
    os.system('clear')
    print("Hello~!. sftp excute.")
    arges = parser.parse_args()
        #Update connect info from parser
    connect_username, connect_hostname = server_arg_check(arges.server)
    connect_hostport = arges.port
        #print connect info
    print_connect_info()

    # Establish a TCP connection with a server 
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((connect_hostname, connect_hostport))
    except :
        print("[Custom_Error_35301] : {}:{} Connect Failed".format(connect_hostname, connect_hostport))