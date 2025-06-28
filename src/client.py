#kayla garibay 
#csc 138 summer 25 
#final project 
#-------------------

# draft/basic structure

import socket
import sys 

def main():
    if len(sys.argv) != 3: #checking for 2 args from user 
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: #using TCP
        try:
            sock.connect((host,port)) #try to connect 
            print("Connected to server")
        except Exception as e: #handles errors 
            print(f"Connection failed: {e}")
            sys.exit(1)
        
        while True: #inf. loop so client can keep sending commands 
            msg = input(">> ") #prompts user to type a command 
            if not msg:
                continue
            sock.sendall(msg.encode())

            if msg.strip().upper() == "QUIT": #if user typed QUIT, exits loop
                break

            response = sock.recv(4096).decode()
            print(response) #bye response 

if __name__ == "__main__": #main funct. called when script is run 
    main()