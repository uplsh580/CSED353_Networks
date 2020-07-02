import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback

import paramiko
from paramiko.py3compat import b, u, decodebytes


# setup logging
paramiko.util.log_to_file("demo_server.log")

host_key = paramiko.RSAKey(filename="id_rsa")
# host_key = paramiko.DSSKey(filename='test_dss.key')

print("Read key: " + u(hexlify(host_key.get_fingerprint())))


class Server(paramiko.ServerInterface):
    good_pub_key = paramiko.RSAKey(filename=sys.argv[1])

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == "root") and (password == "1234"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        if (username == "root") and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        """
        .. note::
            We are just checking in `AuthHandler` that the given user is a
            valid krb5 principal! We don't check if the krb5 principal is
            allowed to log in on the server, because there is no way to do that
            in python. So if you develop your own SSH server with paramiko for
            a certain platform like Linux, you should call ``krb5_kuserok()`` in
            your local kerberos library to make sure that the krb5_principal
            has an account on the server and is allowed to log in as a user.
        .. seealso::
            `krb5_kuserok() man page
            <http://www.unix.com/man-page/all/3/krb5_kuserok/>`_
        """
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

def request_handler(recv_mssg):
    if recv_mssg == 'pwd\n':
        return os.path.abspath('./')
    elif recv_mssg == 'Connect!':
        return 'Good!Good!'
    elif recv_mssg == 'test2!':
        return "wow2"
    else :
        return "wow"

def main():
    DoGSSAPIKeyExchange = True

    # now connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 2200))
        sock.listen(100)
        print("Listening for connection ...")
    except Exception as e:
        print("*** Bind failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    while True:
        try:
            client, addr = sock.accept()
        except Exception as e:
            print("*** Listen/accept failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)

        print("Got a connection!")

        try:
            t = paramiko.Transport(client, gss_kex=DoGSSAPIKeyExchange)
            t.set_gss_host(socket.getfqdn(""))
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
                        # sys.exit(1)
                    
                    recv_mssg = chan.recv(65535).decode("utf-8")
                    print(recv_mssg)
                    reply_mssg = request_handler(recv_mssg)
                    print(reply_mssg)
                    chan.send(reply_mssg)
                except OSError:
                    print("Socket is closed")
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


if __name__ == "__main__":
    main()