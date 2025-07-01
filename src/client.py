#kayla garibay 
#csc 138 summer 25 
#final project 
#-------------------

import socket  #for TCP/IP connection
import sys     #for command-line args and exit()
import threading #for multi-threading 

#constantly receives server messages on a separate thread
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode() #receive from server
            if data:
                print(data.strip()) #show incoming msg right away 
            else:
                break #server disconnected 
        except:
            break #error occurred or socket closed 


def main():
    if len(sys.argv) != 3:  #check for hostname and port args 
        print("usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  #create TCP socket
        try:
            sock.connect((host, port))  #try to connect to server
            print("Connected to server!")  #success msg
        except Exception as e:  #handle connection error
            print(f"Connection failed: {e}")
            sys.exit(1)

        #ask user to JOIN with a username
        while True:
            join_input = input("Enter JOIN followed by your username: ").strip()
            if join_input.upper().startswith("JOIN") and len(join_input.split()) == 2:
                sock.sendall(join_input.encode())  #send JOIN command
                break
            else:
                print("Invalid input. Example: JOIN Mike")  #wrong format :( 
        
        #start new thread to receive server msgs in real time 
        receive_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
        receive_thread.start()

        #main loop to send and receive messages
        while True:
            try:
                msg = input()  #get user command
                if not msg:
                    continue
                sock.sendall(msg.encode())  #send to server

                if msg.strip().upper() == "QUIT":  #quit command
                    break

            except KeyboardInterrupt:  #ctrl+c to exit 
                print("\nDisconnecting from server.")
                break
            except Exception as e:  #general error
                print(f"Error: {e}")
                break

if __name__ == "__main__":  #run main() if script is executed
    main()
