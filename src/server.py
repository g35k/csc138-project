#Gianni Dumitru
#csc 138 summer 25 
#final project 
#-------------------

import sys
import socket
import threading

clients = []

def join(cli_sock, addr, name):
	with threading.Lock():
		for user, sock, ad, in clients:
			if user == name:
				if sock is cli_sock:
					cli_sock.send((f"{name} alreday joined\n").encode())
				else:
					cli_sock.send((f"{name} alreday taken by another user\n").encode())
				return None
		if len(clients) >= 10:
			cli_sock.send((f"Too many users, closing socket\n").encode())
			cli_sock.close()
			return None
		clients.append((name, cli_sock, addr))
	cli_sock.send((f"{name} joined!\n").encode())
	with threading.Lock():
		for u, sock, ad in clients:
			if u != name:
				sock.send((f"{name} joined!\n").encode())
	return name

def list(cli_sock, addr, user):
	if not user:
		cli_sock.send(("unregistered user type: JOIN <username>\n").encode())
		return
	with threading.Lock():
		user_list = ",".join([u for u, _, _ in clients])
	cli_sock.send((user_list + "\n").encode())

def mesg(cli_sock, addr, user, target, msg):
	if not user:
		cli_sock.send(("unregistered user typr: JOIN <username>\n").encode())
		return
	target_sock = None
	with threading.Lock():
		for u, sock, ad in clients:
			if u == target:
				target_sock = sock
				break
	if not target_sock:
		cli_sock.send(("Recipient not found\n").encode())
		return
	target_sock.send((f"{user}: {msg}\n").encode())
	cli_sock.send((f"{user}: {msg}\n").encode())

def bcst(cli_sock, addr, user, msg):
	if not user:
		cli_sock.send(("unregistered user, type: JOIN <username>\n").encode())
		return
	with threading.Lock():
		for u, sock, ad in clients:
			if u != user:
				sock.send((f"{user}: {msg}\n").encode())

def quit(cli_sock, addr, user):
	with threading.Lock():
		if user:
			for i, (u, sock, ad) in enumerate(clients):
				if u == user:
					clients.pop(i)
					break
			for u, sock, ad in clients:
				sock.send((f"{user} left\n").encode())
	cli_sock.send(("Goodbye\n").encode())
	cli_sock.close()

def threaded(cli_sock, addr):
	user = None
	try:
		while True:
			data = cli_sock.recv(1024)
			if not data:
				print("No data received, disconnecting")
				break
			req_line = data.decode().strip()
			req_parts = req_line.split(' ', 2)
			req = req_parts[0].upper()
			if req == 'JOIN' and len(req_parts) > 1:
				user = join(cli_sock, addr, req_parts[1])
			elif req == 'LIST':
				list(cli_sock, addr,  user)
			elif len(req_parts) > 2 and req == 'MESG':
				message = req_line[len(req) + 1:]
				mesg(cli_sock, addr, user, req_parts[1], message)
			elif req == 'BCST' and len(req_parts) > 1:
				message = req_line[len(req) + 1:]
				bcst(cli_sock, addr, user, message)
			elif req == 'QUIT':
				quit(cli_sock, addr, user)
				break
			else:
				cli_sock.send(("unknown message\n").encode())
	except Exception as e:
		print(f"error in thread: {e}")
	finally:
		if user:
			with threading.Lock():
				for i, (u, sock, ad) in enumerate(clients):
					if u == user:
						clients.pop(i)
						break
		cli_sock.close()
		print(f"connection closed for {addr}")

def main():
	if len(sys.argv) != 2:
		print(f"Usage: python3 server.py <svr_port>")
		sys.exit(1)
	try:
		port =  int(sys.argv[1])
	except ValueError:
		print(f"port must be integer")
		sys.exit(1)
	try:
		serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv_sock.bind(("", port))
		serv_sock.listen()
	except Exception as e:
		print(f"failed to bind or listen: {e}")
		sys.exit(1)
	print(f"Listening on port {port}")
	try:
		while True:
			cli_sock, addr = serv_sock.accept()
			print(f"Accepted connect from {addr}")
			t = threading.Thread(target=threaded, args=(cli_sock, addr))
			t.start()
	except KeyboardInterrupt:
		print("server shutting down")
	finally:
		serv_sock.close()

if __name__ == "__main__":
	main()
