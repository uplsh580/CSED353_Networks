import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
from threading import Thread
import subprocess
import random as rd
import time

#TODO: Set your INFO
BIND_PORT = 2200
CUSTOM_USER_NAME = 'root'
CUSTOM_PASSWD = '1234'
key_filename = "id_rsa"

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

#Check paramiko package
try:
    import paramiko
    from paramiko.py3compat import b, u, decodebytes
    from paramiko import ServerInterface, SFTPServerInterface, SFTPServer, SFTPAttributes, \
    SFTPHandle, SFTP_OK, AUTH_SUCCESSFUL, OPEN_SUCCEEDED
except ImportError as e:
    os.system('clear')
    package_install("paramiko")
    import paramiko
    from paramiko.py3compat import b, u, decodebytes
    from paramiko import ServerInterface, SFTPServerInterface, SFTPServer, SFTPAttributes, \
    SFTPHandle, SFTP_OK, AUTH_SUCCESSFUL, OPEN_SUCCEEDED

try : 
    host_key = paramiko.RSAKey(filename=key_filename)
except:
    print('[Error] ({}) is wrong key path.'.format(key_filename))
    exit()

def new_port():
    retry = 1000
    while retry:
        p = rd.randint(40000, 50000)
        # print(p)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", p))
        if result:
            return p
        retry -= 1


class StubServer (ServerInterface):
    def check_auth_password(self, username, password):
        # all are allowed
        return AUTH_SUCCESSFUL
        
    def check_auth_publickey(self, username, key):
        # all are allowed
        return AUTH_SUCCESSFUL
        
    def check_channel_request(self, kind, chanid):
        return OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        """List availble auth mechanisms."""
        return "password,publickey"


class StubSFTPHandle (SFTPHandle):
    def stat(self):
        try:
            return SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def chattr(self, attr):
        # python doesn't have equivalents to fchown or fchmod, so we have to
        # use the stored filename
        try:
            SFTPServer.set_file_attr(self.filename, attr)
            return SFTP_OK
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)


class StubSFTPServer (SFTPServerInterface):
    ROOT = os.getcwd()
        
    def _realpath(self, path):
        return self.ROOT + self.canonicalize(path)

    def list_folder(self, path):
        path = self._realpath(path)
        try:
            out = [ ]
            flist = os.listdir(path)
            for fname in flist:
                attr = SFTPAttributes.from_stat(os.stat(os.path.join(path, fname)))
                attr.filename = fname
                out.append(attr)
            return out
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def stat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(os.stat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def lstat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(os.lstat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def open(self, path, flags, attr):
        path = self._realpath(path)
        try:
            binary_flag = getattr(os, 'O_BINARY',  0)
            flags |= binary_flag
            mode = getattr(attr, 'st_mode', None)
            if mode is not None:
                fd = os.open(path, flags, mode)
            else:
                # os.open() defaults to 0777 which is
                # an odd default mode for files
                fd = os.open(path, flags, 0o666)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            SFTPServer.set_file_attr(path, attr)
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                fstr = 'ab'
            else:
                fstr = 'wb'
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                fstr = 'a+b'
            else:
                fstr = 'r+b'
        else:
            # O_RDONLY (== 0)
            fstr = 'rb'
        try:
            f = os.fdopen(fd, fstr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        fobj = StubSFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        return fobj

    def remove(self, path):
        path = self._realpath(path)
        try:
            os.remove(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rename(self, oldpath, newpath):
        oldpath = self._realpath(oldpath)
        newpath = self._realpath(newpath)
        try:
            os.rename(oldpath, newpath)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def mkdir(self, path, attr):
        path = self._realpath(path)
        try:
            os.mkdir(path)
            if attr is not None:
                SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rmdir(self, path):
        path = self._realpath(path)
        try:
            os.rmdir(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def chattr(self, path, attr):
        path = self._realpath(path)
        try:
            SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def symlink(self, target_path, path):
        path = self._realpath(path)
        if (len(target_path) > 0) and (target_path[0] == '/'):
            # absolute symlink
            target_path = os.path.join(self.ROOT, target_path[1:])
            if target_path[:2] == '//':
                # bug in os.path.join
                target_path = target_path[1:]
        else:
            # compute relative to path
            abspath = os.path.join(os.path.dirname(path), target_path)
            if abspath[:len(self.ROOT)] != self.ROOT:
                # this symlink isn't going to work anyway -- just break it immediately
                target_path = '<error>'
        try:
            os.symlink(target_path, path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def readlink(self, path):
        path = self._realpath(path)
        try:
            symlink = os.readlink(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        # if it's absolute, remove the root
        if os.path.isabs(symlink):
            if symlink[:len(self.ROOT)] == self.ROOT:
                symlink = symlink[len(self.ROOT):]
                if (len(symlink) == 0) or (symlink[0] != '/'):
                    symlink = '/' + symlink
            else:
                symlink = '<error>'
        return symlink


class Server(paramiko.ServerInterface):
    good_pub_key = paramiko.RSAKey(filename=key_filename)

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == CUSTOM_USER_NAME) and (password == CUSTOM_PASSWD):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        if (username == CUSTOM_USER_NAME) and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return True

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

def sftp_server(chan, host, port, keyfile, level='INFO'):
    paramiko_level = getattr(paramiko.common, level)
    paramiko.common.logging.basicConfig(level=paramiko_level)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.bind((host, port))
    server_socket.listen(200)
    chan.send("mssg_05_{}".format(port))

    conn, addr = server_socket.accept()

    host_key = paramiko.RSAKey.from_private_key_file(keyfile)
    transport = paramiko.Transport(conn)
    transport.add_server_key(host_key)
    transport.set_subsystem_handler(
        'sftp', paramiko.SFTPServer, StubSFTPServer)

    server = StubServer()
    transport.start_server(server=server)

    channel = transport.accept()
    while transport.is_active():
        time.sleep(1)

def request_handler(chan, host, port, keyfile, recv_mssg):
    print("[{}:{}] {}".format(host, port, recv_mssg))
    if recv_mssg == 'mssg_00_connect':
        chan.send('Successful connection')
    
    elif recv_mssg == 'mssg_01_init_pwd':
        chan.send(os.path.abspath('./'))

    elif recv_mssg[:8] == 'mssg_02_':
        try:
            commands = recv_mssg[8:].split()
            reply = subprocess.check_output(commands)
            if len(reply) == 0:
                chan.send(" ")
            else:
                chan.send(reply)
        except:
            chan.send("ERROR: No path")

    elif recv_mssg[:8] == 'mssg_03_':
        try :
            reply = os.path.abspath(recv_mssg[11:])
            subprocess.check_output(['ls', reply]) 
            chan.send(reply)
        except:
            chan.send("ERROR: No path")
    
    elif recv_mssg == 'mssg_04_pg':
        # try :
        p = new_port()
        new_SFTP = SFTP_Thread(host, p, chan, keyfile)
        new_SFTP.start()
        
    else :
        chan.send("wow")

class SFTP_Thread(Thread):
    def __init__(self, host, port, chan, keyfile):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.chan = chan
        self.keyfile=keyfile

    def run(self):
        sftp_server(self.chan, self.host, self.port, self.keyfile, level='INFO')


class Client_Thread(Thread):
    def __init__(self, host, port, sock):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = sock
        print ("(Check the new thread) "+host+":"+str(port))

    def run(self):
        try:
            t = paramiko.Transport(self.sock, gss_kex=True)
            t.set_gss_host(socket.getfqdn(""))
            print("Got a connection!")
            try:
                t.load_server_moduli()
            except:
                print("(Failed to load moduli -- gex will be unsupported.)")
                raise
            t.add_server_key(host_key)
            server = Server()
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                print("*** SSH negotiation failed.")
                sys.exit(1)

            # wait for auth
            chan = t.accept(20)
            if chan is None:
                print("*** No channel.")
                sys.exit(1)
            print("Authenticated!")

            while True:
                try:
                    server.event.wait(1)
                    if not server.event.is_set():
                        print("*** Client never asked for a shell.")
                        break
                    
                    recv_mssg = chan.recv(65535).decode("utf-8")
                    reply_mssg = request_handler(chan, self.host, self.port, key_filename, recv_mssg)
                except OSError:
                    print("[{}:{}] Socket is closed".format(self.host, self.port))
                    break
            chan.close()

        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass
            sys.exit(1)

def main():

    # now connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", BIND_PORT))
        sock.listen(200)
        print("Listening for connection ...")
    except Exception as e:
        print("*** Bind failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    threads = []

    while True:
        try:
            (client_sock, (host, port)) = sock.accept()
        except Exception as e:
            print("*** Listen/accept failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)
        new_thread = Client_Thread(host, port, client_sock)
        new_thread.start()
        threads.append(new_thread)

if __name__ == "__main__":
    main()