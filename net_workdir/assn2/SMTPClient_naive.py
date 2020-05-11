import ssl
from socket import *
import base64

username = 'your_postech_id@postech.ac.kr'
password = 'your_password'              # IMPORTANT NOTE!!!!!!!!!!: PLEASE REMOVE THIS FIELD WHEN YOU SUBMIT!!!!!

subject = 'Computer Network Assignment2 - Email Client'
from_ = 'your_postech_id@postech.ac.kr'
to_ = 'your_postech_id_or_your_friend\'s@postech.ac.kr'
content = 'It is so hard for me!!!'

# Message to send
endmsg = '\r\n.\r\n'

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = 'smtp.office365.com'
port = 587

# 1. Establish a TCP connection with a mail server [2pt]
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, port))

# 2. Dialogue with the mail server using the SMTP protocol. [2pt]
recv = clientSocket.recv(1024)
recv = recv.decode()
print("Message after connection request:" + recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

heloCommand = 'HELO {}\r\n'.format(mailserver)
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024)
recv1 = recv1.decode()
print("Message after HELO command:" + recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# 3. Login using SMTP authentication using your postech account. [5pt]
# HINT: Send STARTTLS
starttlsCommand = 'STARTTLS\r\n'
clientSocket.send(starttlsCommand.encode())
recv2 = clientSocket.recv(1024)
recv2 = recv2.decode()
print("Message after STARTTLS command:" + recv2)
if recv2[:3] != '220':
    print('220 reply not received from server.')

# HINT: Wrap socket using ssl.PROTOCOL_SSLv23
# HINT: Use base64.b64encode for the username and password
# HINT: Send EHLO
context = ssl.create_default_context()
with context.wrap_socket(clientSocket, server_hostname=mailserver) as clientSocketSSL:
    print(clientSocketSSL.version())

    ehloCommand = 'EHLO {}\r\n'.format(mailserver)
    clientSocketSSL.send(ehloCommand.encode())
    recv3 = clientSocketSSL.recv(1024)
    recv3 = recv3.decode()
    print("Message after EHLO command:" + recv3)
    if recv3[:3] != '250':
        print('250 reply not received from server.')
    
    authCommand = 'AUTH LOGIN\r\n'
    clientSocketSSL.send(authCommand.encode())
    recv4 = clientSocketSSL.recv(1024)
    recv4 = recv4.decode()
    print("Message after AUTH command:" + recv4)
    if recv4[:3] != '334':
        print('334 reply not received from server.')

    usernameB64 = base64.b64encode(username.encode("UTF-8")) + "\r\n".encode()
    clientSocketSSL.send(usernameB64)
    recv5 = clientSocketSSL.recv(1024)
    recv5 = recv5.decode()
    print("Message after Username send:" + recv5)
    if recv5[:3] != '334':
        print('334 reply not received from server.')

    passwordB64 = base64.b64encode(password.encode("UTF-8")) + "\r\n".encode()
    clientSocketSSL.send(passwordB64)
    recv6 = clientSocketSSL.recv(1024)
    recv6 = recv6.decode()
    print("Message after Passwd send:" + recv6)
    if recv6[:3] != '235':
        print('235 reply not received from server.')

# 4. Send a e-mail to your POSTECH mailbox. [5pt]
    mailFrom = "MAIL FROM:<{}>\r\n".format(from_)
    clientSocketSSL.send(mailFrom.encode())
    recv7 = clientSocketSSL.recv(1024)
    recv7 = recv7.decode()
    print("After MAIL FROM command: "+recv7)

    rcptTo = "RCPT TO:<{}>\r\n".format(to_)
    clientSocketSSL.send(rcptTo.encode())
    recv8 = clientSocketSSL.recv(1024)
    recv8 = recv8.decode()
    print("After RCPT TO command: "+recv8)

    data = "DATA\r\n"
    clientSocketSSL.send(data.encode())
    recv9 = clientSocketSSL.recv(1024)
    recv9 = recv9.decode()
    print("After DATA command: "+recv9)

    #Header
    from_msg = "From: {}\r\n".format(from_)
    to_msg = "To: {}\r\n".format(to_)
    subject_msg = "Subject: {}\r\n\r\n".format(subject)
    clientSocketSSL.send(from_msg.encode())
    clientSocketSSL.send(to_msg.encode())
    clientSocketSSL.send(subject_msg.encode())

    #Body
    clientSocketSSL.send(content.encode())

    #End
    clientSocketSSL.send(endmsg.encode())
    recv_msg = clientSocketSSL.recv(1024)
    print("Response after sending message body:"+recv_msg.decode())

# 5. Destroy the TCP connection [2pt]
    quit = "QUIT\r\n"
    clientSocketSSL.send(quit.encode())
    recv10 = clientSocketSSL.recv(1024)
    print(recv10.decode())
    clientSocketSSL.close()