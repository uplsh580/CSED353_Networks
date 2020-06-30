import argparse
from socket import *
import sys
import os
from cmd import Cmd
import subprocess
import sys
import time

#Check paramiko package
try:
    import paramiko
except ImportError as e:
    os.system('clear')
    package_install("paramiko")

# #Connect Info valuable
# connect_username = None
# connect_hostname = None
# connect_hostport = None

#Parser
parser = argparse.ArgumentParser()
parser.add_argument("server", help="connect server ip : 'username@addrhostnameess'", type=str)
parser.add_argument("-p", "--port", help="connect server port, default is 22", type=int, default=22)

def package_install(package):
    while (1):
        print("This program needs [{}] package.".format(package))
        reply = input("Is it okay to install [{}] package? (y/n) : ".format(package))
        if reply == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            time.sleep(1)
            return True
        elif reply == 'n':
            print("Quit program.")
            exit()

def abs_path(cur_path, input_path = ""):
    if len(input_path) == 0:
        return os.path.abspath(cur_path)
    elif input_path[0] == '/' or input_path[0] == '~':
        return os.path.abspath(input_path)
    else:
        return os.path.abspath(cur_path + "/" + input_path)

def parse(args):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, args.split()))

class Prompt_sftp(Cmd):
    intro = "Welcome! sftp connect success~!!"
    prompt = 'custom_sftp> '

    def __init__(self, connect_hostname, connect_username, connect_hostport, passwd):
        super().__init__() 
        self.ssh = paramiko.SSHClient()

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("Hello~!. sftp excute.")
        print_connect_info(connect_hostname, connect_username, connect_hostport)
        try:
            self.ssh.connect(connect_hostname, username=connect_username, password=passwd, port=connect_hostport)
        except :
            print("Connect Fail!")
            exit()
        
        #set local_path
        self.cur_local_path = os.path.abspath('./')

        #set remote_path
        stdin, stdout, stderr = self.ssh.exec_command("pwd")
        temp_remote_path = stdout.readlines()[0]
        self.cur_remote_path = temp_remote_path[:temp_remote_path.find('\n')]

    def do_test(self, args):
        stdin, stdout, stderr = self.ssh.exec_command("pwd")
        print(self.cur_remote_path)

    def do_ls(self, args):
        flag = ''
        path = self.cur_remote_path
        for arg in parse(args):
            if arg[0] == '-':
                flag = arg
            elif arg[0] == '/' or arg[0] == '~': 
                path = arg
            else : 
                path = self.cur_remote_path + '/' + arg

        stdin, stdout, stderr = self.ssh.exec_command("ls {} {}".format(flag, path))

        line_flag_list = "lgno1"
        if len(set(line_flag_list) - set(flag)) == len(set(line_flag_list)):
            for e in stdout.readlines():
                print(e[:e.find("\n")], end=' ')
            print()
        else :
            for e in stdout.readlines():
                print(e[:e.find("\n")])

        for e in stderr.readlines():
            print(e[:e.find("\n")])

    def help_ls(self):
        print("ls [-1afhlnrSt] [path] : Display remote directory listing")

    def do_cd(self, arg):
        path = self.cur_remote_path
        if arg[0] == '/' or arg[0] == '~': 
            path = arg
        else : 
            path = self.cur_remote_path + '/' + arg

        stdin, stdout, stderr = self.ssh.exec_command("cd {} && pwd".format(path))
        update_path = stdout.readlines()[0]
        update_path = update_path[:update_path.find('\n')]
        self.cur_remote_path = update_path

    def help_cd(self):
        print("cd path : Change remote directory to 'path'")

    def do_pwd(self, args):
        print(self.cur_remote_path)

    def help_pwd(self):
        print("pwd : Display remote working directory")

    def do_lls(self, args=''):
        flag = ''
        path = abs_path(self.cur_local_path)
        for arg in parse(args):
            if arg[0] == '-':
                flag = arg
            else :
                path = abs_path(self.cur_local_path, arg)
        os.system("ls {} {}".format(flag, path))
    
    def help_lls(self):
        print("lls [-1afhlnrSt] [path] : Display local directory listing")

    def do_lcd(self, arg):
        self.cur_local_path = abs_path(self.cur_local_path, arg)
        
    def help_lcd(self):
        print("lcd path : Change local directory to 'path'")
    
    def do_lpwd(self, arg):
        print(self.cur_local_path)
        
    def help_lpwd(self):
        print("lpwd : Print local working directory")

    def do_exit(self, inp):
        print("Quit sftp")
        self.ssh.close()
        return True

    def help_exit(self):
        print("exit : Quit sftp")

def server_arg_check(server_str):
    if "@" not in server_str:
        print("[Custom_Error_35300] : '{}' is wrong argument({}) pattern.".format(server_str, "server"))
        print("You should type 'user@host' format.")
        exit()
    else:
        connect_id, connect_address = tuple(server_str.split("@"))
        return connect_id, connect_address
    
def print_connect_info(connect_username, connect_hostname, connect_hostport):
    print("-----------Connect Info-----------")
    print("Connect User Name | {}".format(connect_username))
    print("Connect Host Name | {}".format(connect_hostname))
    print("Connect Host Port | {}".format(connect_hostport))
    print("----------------------------------")


if __name__ == "__main__":


    #Start Program
    os.system('clear')
    arges = parser.parse_args()
    connect_username, connect_hostname = server_arg_check(arges.server)
    connect_hostport = arges.port
    passwd = "12345"

    Prompt_sftp(connect_hostname, connect_username, connect_hostport, passwd).cmdloop()
