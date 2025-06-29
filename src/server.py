import sys
import socket
import threading

clients = []

def join(cli_sock, addr, name):
	with threading.lock():
		for user, (sock, ad), in clients:
			if user == name:
				if sock is cli_sock
					cli_sock.send(f"{name} alreday joined\n")
					return name
				cli_sock.send(f"{name} alreday taken by another user\n")
				return None
		if len(clients) >= 10:
			cli_sock.send(f"Too many users, closing socket\n")
			cli_sock.close()
			return None
		clients.append((name, (cli_sock, addr)))
	cli_sock.send(f"{name} joined!\n".encode())
	with threading.lock():
		for u, (sock, ad) in clients:
			if u != name:
				sock.send(f"{name} joined!\n".encode())
	return name

def list(cli_sock, user)
	if not user:
		cli_sock.send("unregistered user\n")
		return
	with threading.lock():
		user_list = ",".join([u for u, _ in clients])
	cli_sock.send((user_list + "\n").encode())

def mesg(cli_sock, user, target, msg):
	if not user:
		cli_sock.send("User hasen't joined\n")
		return
	target_sock = None
	with threading.lock():
		for u, (sock, ad) in clients:
			if u == target
				target_sock = sock
				break
	if not target_sock
		cli_sock.send("Recipient not found\n")
		return
	target_sock.send(f"{user}: {msg}\n".encode())
	cli_sock.send(f"{user}: {msg}\n".encode())

def bcst(cli_sock, user, msg)
	if not user:
		cli_sock.send("User hasen't joined\n")
		return
	with threading.lock():
		for u, (sock, ad) in clients:
			if u != user:
				sock.send(f"{user}: {msg}\n".encode())

def quit(cli_sock, user)
	if user:
		with threading.lock():
			for i, (u, (sock, ad)) in enumerate(clients):
				if u = user:
					clients.pop(i)
					break
			for u, (sock, ad) in clients:
				sock.send(f"{user} left\n".encode())
		cli_sock.send("Goodbye\n")
	cli_sock.close()

def threaded(cli_sock, addr):
	user = None
	try:
		while True:
			data cli_sock.recv(1024)
			if not data:
				print("No data received, disconnecting")
				break
			req_line = data.decode().strip()
			req_parts = req_line.split(' ', 2)
			req = req_parts[0].upper()
			if req == 'LIST':
				list(cli_sock, user)
			elif req == 'QUIT':
				quit(cli_sock, user)
				break
			elif len(req_parts) > 1:
				if req == 'JOIN':
					user = join(cli_sock, addr, req_parts[1])
				elif req == 'BCST':
					bcst(cli_sock, user, req_parts[1])
			elif len(req_parts) > 2 and req == 'MESG':
				mesg(cli_sock, user, req_parts[1], req_parts[2]
			else:
				cli_sock.send("unknown message\n")
				print(f"[to {addr}] Unknown Message")
				print(f"Unknown command from {addr}: '{req_line}'")
	except Exception as e:
		print(f"error in thread: {e}")
	finally:
		if user:
			with threading.lock()
				clients.pop(user, None)
		cli_sock.close()
		print(f"connection closed for {addr}")

def main():
	if len(sys.argv) != 2:
		print(f"Usage: python3 server.py <svr_port>")
		sys.exit(1)

	port =  int(sys.argv[1])
	serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serv_sock.bind(("", port))
	serv_sock.listen()
	print(f"Listening on port {port}")
	while True:
		cli_sock, addr = serv_sock.accept()
		print(f"Accepted connect from {addr}")
		threading.Thread(target=threaded, args(cli_sock, addr)).start()
