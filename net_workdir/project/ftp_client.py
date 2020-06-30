import argparse
from socket import *
import sys
import os
from cmd import Cmd

#Connect Info valuable
connect_username = None
connect_hostname = None
connect_hostport = None

#Local path info
local_cur_location = os.path.abspath('./')

#Parser
parser = argparse.ArgumentParser()
parser.add_argument("server", help="connect server ip : 'username@addrhostnameess'", type=str)
parser.add_argument("-p", "--port", help="connect server port, default is 22", type=int, default=22)

def abs_path(input_path = ""):
    global local_cur_location
    if len(input_path) == 0:
        return os.path.abspath(local_cur_location)
    elif input_path[0] == '/' or input_path[0] == '~':
        return os.path.abspath(input_path)
    else:
        return os.path.abspath(local_cur_location + "/" + input_path)

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, arg.split()))

class Prompt_sftp(Cmd):
    intro = "Welcome! sftp!"
    prompt = 'custom_sftp> '

    
    def do_lls(self, args=""):
        flag = ""
        path = abs_path()
        for arg in parse(args):
            if arg[0] == '-':
                flag = arg
            else :
                path = abs_path(arg)
        os.system("ls {} {}".format(flag, path))
    
    def help_lls(self):
        print("lls [-1afhlnrSt] [path] : Display local directory listing")

    def do_lcd(self, arg):
        global local_cur_location
        local_cur_location = abs_path(arg)
        
    def help_lcd(self):
        print("lcd path : Change local directory to 'path'")
    
    def do_lpwd(self, arg):
        global local_cur_location
        print(local_cur_location)
        
    def help_lpwd(self):
        print("lpwd : Print local working directory")

    def do_exit(self, inp):
        print("Quit sftp")
        return True

    def help_exit(self):
        print("exit : Quit sftp")

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
    arges = parser.parse_args()
    #Update connect info from parser
    connect_username, connect_hostname = server_arg_check(arges.server)
    connect_hostport = arges.port
    #print connect info
    print("Hello~!. sftp excute.")
    print_connect_info()

    # Establish a TCP connection with a server 
    # try:
    #     clientSocket = socket(AF_INET, SOCK_STREAM)
    #     clientSocket.connect((connect_hostname, connect_hostport))

    # except :
    #     print("[Custom_Error_35301] : {}:{} Connect Failed".format(connect_hostname, connect_hostport))
    Prompt_sftp().cmdloop()
