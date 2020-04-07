# Import socket module
from socket import * 
import sys # In order to terminate the program

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)

serverSocket = socket(AF_INET, SOCK_STREAM) ### Write your code

# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
serverSocket.bind((gethostname(),serverPort)) ### Write your code

# Listen to at most 1 connection at a time
serverSocket.listen(1) ### Write your code

# Server should be up and running and listening to the incoming connections

while True:
	print('The server is ready to receive')

	# Set up a new connection from the client
	connectionSocket, addr = serverSocket.accept() ### Write your code

	# If an exception occurs during the execution of try clause
	# the rest of the clause is skipped
	# If the exception type matches the word after except
	# the except clause is executed
	try:
		# Receives the request message from the client
		message = connectionSocket.recv(1024).decode() ### Write your code
		# Extract the path of the requested object from the message
		# The path is the second part of HTTP header, identified by [1]
		filename = message.split()[1]### Write your code
		# Because the extracted path of the HTTP request includes 
		# a character '\', we read the path from the second character 
		print("Request file name :", filename)
		f = open(filename[1:])
		# Store the entire content of the requested file in a temporary buffer
		outputdata = f.read()
		# Send the HTTP response header line to the connection socket
		### Write your code
		response_hd = "HTTP/1.1 200 OK\r\n\r\n"
		print(response_hd)
		connectionSocket.send(response_hd)
		# Send the content of the requested file to the connection socket
		for i in range(0, len(outputdata)):  
			connectionSocket.send(outputdata[i])### Write your code
		# Send "\r\n" to the connection socket.
		connectionSocket.send("\r\n") ### Write your code
		# Close the client connection socket
		connectionSocket.close() ### Write your code
		
	except IOError:
		print("IOError")
		# Send HTTP response message for file not found
		connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n")
		connectionSocket.send("HTTP 404 Not Found\r\n")
		### Write your code
		# Close the client connection socket
		connectionSocket.close() ### Write your code

# Close the server socket
serverSocket.close()
sys.exit() #Terminate the program after sending the corresponding data
