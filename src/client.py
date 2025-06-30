#kayla garibay 
#csc 138 summer 25 
#final project 
#-------------------

import socket  #for TCP/IP connection
import sys     #for command-line args and exit()

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

        #receive server response
        try:
            sock.settimeout(1.0)  #short timeout to receive multiple join messages
            while True:
                try:
                    response = sock.recv(4096).decode()
                    if response:
                        print(response.strip())  #print server message
                    else:
                        break
                except socket.timeout:
                    break
            sock.settimeout(None)  #reset timeout
        except Exception as e:
            print(f"Error receiving JOIN responses: {e}")

        #main loop to send and receive messages
        while True:
            try:
                msg = input()  #get user command
                if not msg:
                    continue
                sock.sendall(msg.encode())  #send to server

                if msg.strip().upper() == "QUIT":  #quit command
                    break

                response = sock.recv(4096).decode()
                if response:
                    print(response.strip())  #show response

            except KeyboardInterrupt:  #ctrl+c to exit 
                print("\nDisconnecting from server.")
                break
            except Exception as e:  #general error
                print(f"Error: {e}")
                break

if __name__ == "__main__":  #run main() if script is executed
    main()
