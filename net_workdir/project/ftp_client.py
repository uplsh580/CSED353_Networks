import argparse
from socket import *
import sys
import os
from cmd import Cmd
import subprocess
import sys
import time
import getpass

#TODO : Set yout RSA KEY
key_file = "./id_rsa"

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
try:
    import paramiko
except ImportError as e:
    os.system('clear')
    package_install("paramiko")
    import paramiko
    

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

    def __init__(self, connect_hostname, connect_username, connect_hostport, passwd, keyfilepath):
        super().__init__() 
        self.host = connect_hostname
        self.user = connect_username
        self.port = connect_hostport
        self.passwd = passwd
        self.key_filename = keyfilepath

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("Hello~!. sftp excute.")
        print_connect_info(connect_hostname, connect_username, connect_hostport)

        try:
            self.ssh.connect(self.host , username=self.user , password=passwd, port=self.port)
            self.channel = self.ssh.invoke_shell()
            self.channel.send("mssg_00_connect")
            print("[{}:{}] {}".format(self.host, self.port, self.channel.recv(65535).decode("utf-8")))
        except :
            print("Connect Fail!")
            exit()

        # set local_path
        self.cur_local_path = os.path.abspath('./')

        # set remote_path
        self.channel.send("mssg_01_init_pwd")
        recv_mssg = self.channel.recv(65535).decode("utf-8")
        self.cur_remote_path = recv_mssg

        self.init_remote_path = self.cur_remote_path

    def do_put(self, args):
        self.channel.send("mssg_04_pg")
        recv_mssg = self.channel.recv(65535).decode("utf-8")
        p = int(recv_mssg.replace('mssg_05_', ''))
        
        f_ssh = paramiko.SSHClient()
        f_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        f_ssh.connect(self.host, username=self.user, password=self.passwd, port=p, key_filename=self.key_filename)
        self.channel = self.ssh.invoke_shell()
        sftp = f_ssh.open_sftp()
        time_s = time.time()
        print("Start Transfer Time: {}".format(time_s))
        try:
            args_list = list(parse(args))
            flag = ''
            if args_list[0][0] == "-":
                flag = args_list[0]
                file_name = args_list[1].split('/')[-1]
                src_path = abs_path(self.cur_local_path, input_path = args_list[1])

                if len(args_list) == 3:
                    if args_list[2][0] == '/' or args_list[2][0] == '~': 
                        dst_path = args_list[2] + '/' + file_name
                    else : 
                        dst_path = self.cur_remote_path + '/' + args_list[2]
                        if dst_path[-1] == '/':
                            dst_path += file_name
                        else: 
                            dst_path += '/' + file_name
                else:
                    dst_path = self.cur_remote_path
                    if dst_path[-1] == '/':
                        dst_path += file_name
                    else: 
                        dst_path += '/' + file_name
            else :
                file_name = args_list[0].split('/')[-1]
                src_path = abs_path(self.cur_local_path, input_path = args_list[0])

                if len(args_list) == 2:
                    if args_list[1][0] == '/' or args_list[1][0] == '~': 
                        dst_path = args_list[1] + '/' + file_name
                    else : 
                        dst_path = self.cur_remote_path
                        if dst_path[-1] == '/':
                            dst_path += args_list[1]
                        else: 
                            dst_path += '/' + args_list[1]
                        if dst_path[-1] == '/':
                            dst_path += file_name
                        else: 
                            dst_path += '/' + file_name
                else:
                    dst_path = self.cur_remote_path
                    if dst_path[-1] == '/':
                        dst_path += file_name
                    else: 
                        dst_path += '/' + file_name
                        
            if dst_path[:len(self.init_remote_path)] == self.init_remote_path:
                if dst_path[len(self.init_remote_path)] == '/':
                    dst_path = '.' + dst_path[len(self.init_remote_path):]
                else:
                    dst_path = './' + dst_path[len(self.init_remote_path):]
            print("[Local] {} -> [Remote] {}".format(src_path, dst_path))
            try:
                sftp.put(src_path, remotepath=dst_path)
            except FileNotFoundError:
                print("No such file")
            except OSError:
                print("No such file")
            sftp.close()
            f_ssh.close()
        except:
            print("Something Wrong")

        
        self.ssh.connect(self.host , username=self.user , password=self.passwd, port=self.port)
        self.channel = self.ssh.invoke_shell()
        time_e = time.time()
        print("End Transfer Time: {}".format(time_e))
        print("TIME : {}".format(time_e-time_s))
        
    def help_put(self):
        print("put [-afPpRr] local [remote] : Upload file")

    def do_get(self, args):
        self.channel.send("mssg_04_pg")
        recv_mssg = self.channel.recv(65535).decode("utf-8")
        p = int(recv_mssg.replace('mssg_05_', ''))
        
        f_ssh = paramiko.SSHClient()
        f_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        f_ssh.connect(self.host, username=self.user, password=self.passwd, port=p, key_filename=self.key_filename)
        self.channel = self.ssh.invoke_shell()
        sftp = f_ssh.open_sftp()
        time_s = time.time()
        print("Start Transfer Time: {}".format(time_s))
        args_list = list(parse(args))
        try:
            flag = ''
            if args_list[0][0] == "-":
                flag = args_list[0]
                file_name = args_list[1].split('/')[-1]
                src_path = self.cur_remote_path 
                if args_list[1][0] == '/' or args_list[1][0] == '~': 
                    src_path = args_list[1]
                else : 
                    if src_path[-1] == '/':
                        src_path += args_list[1]
                    else:
                        src_path += '/' + args_list[1]
                

                if len(args_list) == 3:
                    dst_path = abs_path(self.cur_local_path, input_path = args_list[2]+ file_name)
                else:
                    dst_path = abs_path(self.cur_local_path, input_path = file_name)
            else :
                file_name = args_list[0].split('/')[-1]
                src_path = self.cur_remote_path 
                if args_list[0][0] == '/' or args_list[0][0] == '~': 
                    src_path = args_list[0]
                else : 
                    if src_path[-1] == '/':
                        src_path += args_list[0]
                    else:
                        src_path += '/' + args_list[0]
                

                if len(args_list) == 2:
                    dst_path = abs_path(self.cur_local_path, input_path = args_list[1]+ '/'+ file_name)
                else:
                    dst_path = abs_path(self.cur_local_path, input_path = file_name)
                        
            # dst_path = '/root/test.txt'
            if src_path[:len(self.init_remote_path)] == self.init_remote_path:
                if src_path[len(self.init_remote_path)] == '/':
                    src_path = '.' + src_path[len(self.init_remote_path):]
                else:
                    src_path = './' + src_path[len(self.init_remote_path):]
            print("[Remote] {} -> [Local] {}".format(src_path, dst_path))
            try:
                sftp.get(src_path, dst_path)
            except FileNotFoundError:
                print("No such file")
            except OSError:
                print("No such file")
            sftp.close()
            f_ssh.close()
        except:
            print("Something Wrong")

        self.ssh.connect(self.host , username=self.user , password=self.passwd, port=self.port)
        self.channel = self.ssh.invoke_shell()
        time_e = time.time()
        print("End Transfer Time: {}".format(time_e))
        print("TIME : {}".format(time_e-time_s))

    def help_get(self):
        print("get [-afPpRr] remote [local] : Download file")

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

        self.channel.send("mssg_02_ls {} {}".format(path, flag))
        recv_mssg = self.channel.recv(65535).decode("utf-8")
        if recv_mssg[:5] == "ERROR" :
            print(recv_mssg)
        else:
            line_flag_list = "lgno1"
            if len(set(line_flag_list) - set(flag)) == len(set(line_flag_list)):
                recv_mssg = recv_mssg.replace('\n', ' ')
                print(recv_mssg)
            else :
                print(recv_mssg)

    def help_ls(self):
        print("ls [-1afhlnrSt] [path] : Display remote directory listing")

    def do_cd(self, arg):
        path = self.cur_remote_path
        if arg == '':
            path = ''
        elif arg[0] == '/' or arg[0] == '~': 
            path = arg
        else : 
            path = self.cur_remote_path + '/' + arg

        # stdin, stdout, stderr = self.ssh.exec_command("cd {} && pwd".format(path))
        # update_path = stdout.readlines()[0]

        self.channel.send("mssg_03_cd {}".format(path))
        recv_mssg = self.channel.recv(65535).decode("utf-8")
        if recv_mssg[:5] == "ERROR" :
            print(recv_mssg)
        else:
            self.cur_remote_path = recv_mssg.replace('\n', ' ')

    def help_cd(self):
        print("cd path : Change remote directory to 'path'")

    def do_pwd(self, args):
        print("[Remote]",self.cur_remote_path)

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
        print("[Local]",self.cur_local_path)
        
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
    passwd = getpass.getpass()
    os.system('clear')
    arges = parser.parse_args()
    connect_username, connect_hostname = server_arg_check(arges.server)
    connect_hostport = arges.port

    Prompt_sftp(connect_hostname, connect_username, connect_hostport, passwd, key_file).cmdloop()
