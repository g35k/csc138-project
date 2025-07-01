import sys
import socket
import threading
#list stores 3-tuple of each client that joins
clients = []
#lock variable to ensure no other thread runs while a client is using a function
clientLock = threading.Lock()
#join function
def join(cli_sock, addr, name):
	#lock thread to avoid data being modified durig join process
	with clientLock:
		#loop through all the 3-tuples to check if any user matches the clients name
		for user, sock, ad, in clients:
			if user == name:
				#if the client already joined with that user tell the client
				if sock is cli_sock:
					print(f"{name} attempted to join again")
					cli_sock.send((f"{name} already joined\n").encode())
				#if another client joined with that name tell them that its already taken
				else:
					print(f"{name} taken by another client")
					cli_sock.send((f"{name} already taken by another user\n").encode())
				return name
		#if the length of the client list is or exceeds 10 notify the client and close the socket
		if len(clients) >= 10:
			print(f"Too many users, rejecting connection from {addr}")
			cli_sock.send((f"Too many users, closing socket\n").encode())
			cli_sock.close()
			return None
		#if none of the conditions apply to the name of the client add to the list
		clients.append((name, cli_sock, addr))
		print(f"{name} Joined")
	#let the client know they joined
	cli_sock.send((f"{name} joined!\n").encode())
	#lock the thread to ensure no client leaves while looping through the list notifying them of the client joining
	with clientLock:
		for u, sock, ad in clients:
			if u != name:
				sock.send((f"{name} joined!\n").encode())
	return name
#list function of all users
def list(cli_sock, addr, user):
	#checks if client has joined
	if not user:
		cli_sock.send(("unregistered user, type: JOIN <username>\n").encode())
		return
	print(f"LIST request from {user}")
	#Locks thread to ensure nothing is changed while it loops through the client list
	with clientLock:
		#loops through client list grabbing only the client names of the tuples, joining them together separated by a comma storing them in the user_list variable
		user_list = ",".join([u for u, _, _ in clients])
	#send the usser list back to the client
	cli_sock.send((user_list + "\n").encode())

#direct message function
def mesg(cli_sock, addr, user, target, msg):
	#checks if user has joined exits if they are not and lets them know
	if not user:
		cli_sock.send(("unregistered user, type: JOIN <username>\n").encode())
		return
	print(f"MESG request from {user} to {target}: {msg}")
	#intialized variable to store target users socket
	target_sock = None
	#locks thread as it loops the list for the user that matches the target saving their socket
	with clientLock:
		for u, sock, ad in clients:
			if u == target:
				target_sock = sock
				break
	#if the  taarget isn't found leave the function and tell the client
	if not target_sock:
		print(f"Unknown user {target} requested by {user}")
		cli_sock.send(("Recipient not found\n").encode())
		return
	#send message to the target client and to the sender clientt
	target_sock.send((f"{user}: {msg}\n").encode())
	print(f"Sent message to {target} from {user}")
	cli_sock.send((f"{user}: {msg}\n").encode())

#broadcast function
def bcst(cli_sock, addr, user, msg):
	print(f"Broadcast request from {user}")
	#checks if clientt has joined
	if not user:
		cli_sock.send(("unregistered user, type: JOIN <username>\n").encode())
		return
	#lock thread loops list sending message to all users except user
	with clientLock:
		for u, sock, ad in clients:
			if u != user:
				sock.send((f"{user}: {msg}\n").encode())
		#notify user the message has been sent
		print(f"Broadcast sent by {user} to all clients")
		cli_sock.send(f"Broadcast sent\n".encode())

#quit server
def quit(cli_sock, addr, user):
	print(f"{user} is quitting the server")
	#locks thread while it checks if user has a valid value
	with clientLock:
		if user:
			#loops through list finding the index and 3-tuple by checking the user and pops it from the list
			for i, (u, sock, ad) in enumerate(clients):
				if u == user:
					clients.pop(i)
					break
			#notifies all clients of the leaving client
			for u, sock, ad in clients:
				sock.send((f"{user} left\n").encode())
	print(f"{user} left the server")
	#sends goodbye message to leaving client and closes socket
	cli_sock.send(("Goodbye\n").encode())
	cli_sock.close()

#pre thread
def threaded(cli_sock, addr):
	#intialize user variable
	user = None
	try:
		#loops forever unless stopped by force
		while True:
			#receives data from client
			data = cli_sock.recv(1024)
			#if data is emptty break loop and tell the server
			if not data:
				print("No data received, disconnecting")
				break
			#decodes data into a string, strips any whitspaces,splits string into 3 max, and ensures the first elemnt (command) is uppercase
			req_line = data.decode().strip()
			req_parts = req_line.split(' ', 2)
			req = req_parts[0].upper()
			#if req is JOIN and the lemgth of req_parts is more than 1, call join() and assign it to user so the loop knows he joined
			if req == 'JOIN' and len(req_parts) > 1:
				user = join(cli_sock, addr, req_parts[1])
			#if req is LIST call list()
			elif req == 'LIST':
				list(cli_sock, addr,  user)
			#if the amount of parts in the command is more than 2 and req is MESG, grab the whole message and put it in the mesg() call  parameter
			elif len(req_parts) > 2 and req == 'MESG':
				message = req_line[len(req) + 1:]
				mesg(cli_sock, addr, user, req_parts[1], message)
			#iif req is BCST and the command is more than 1  grab the whole message and  place it in bcst() call parameters
			elif req == 'BCST' and len(req_parts) > 1:
				message = req_line[len(req) + 1:]
				bcst(cli_sock, addr, user, message)
			#if req is QUIT call quit() and break the loop
			elif req == 'QUIT':
				quit(cli_sock, addr, user)
				break
			#notify client the command is not understood
			else:
				cli_sock.send(("unknown message\n").encode())
	#catch all exception for the thread
	except Exception as e:
		print(f"error in thread: {e}")
	#enter once exiting try
	finally:
		print(f"{user} left unexpectedly")
		#only if user is present
		if user:
			#lock thread and loop through the list to find the index of the client that unexpectidly terminated removing thier tuple 
			with clientLock:
				for i, (u, sock, ad) in enumerate(clients):
					if u == user:
						clients.pop(i)
						break
		#close clients socket and notify the serveer
		cli_sock.close()
		print(f"connection closed for {addr}")

def main():
	#checks if command to start server  has 2 arguments
	if len(sys.argv) != 2:
		print(f"Usage: python3 server.py <svr_port>")
		sys.exit(1)
	#ttempts to assign to port the second elemnt of the argument
	try:
		port =  int(sys.argv[1])
	except ValueError:
		print(f"port must be integer")
		sys.exit(1)
	#starts socket, binds ip and port to the server socket, and begins to listen for incoming traffic
	try:
		serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv_sock.bind(("", port))
		serv_sock.listen()
	except Exception as e:
		print(f"failed to bind or listen: {e}")
		sys.exit(1)
	print("Server has started")
	print(f"Listening on port {port}")
	try:
		#infinite loop that accepts and assigns incoming client sockets and addresses starst 
		while True:
			cli_sock, addr = serv_sock.accept()
			print(f"Accepted connection from {addr}")
			#start new thread with its target destination threaded() and passing the socket and addr
			t = threading.Thread(target=threaded, args=(cli_sock, addr))
			t.start()
	#stop if ^C
	except KeyboardInterrupt:
		print("server shutting down")
	#close server socket
	finally:
		serv_sock.close()

if __name__ == "__main__":
	main()
