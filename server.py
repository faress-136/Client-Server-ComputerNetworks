# echo-server.py

import socket
import re
import threading
import time

# HOST = socket.gethostbyname(socket.gethostname())
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
ADDR = (HOST, PORT)
DISCONNECT = 'Disconnect'
FORMAT = 'utf-8'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDR)


def connect(Hosts, Ports):
    global s_2
    HOST_2 = socket.gethostbyname(Hosts)
    PORT_2 = int(Ports)
    ADDR_2 = (HOST_2, PORT_2)
    s_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_2.connect(ADDR_2)


def handle_client(conn: object, addr):
    print(f"[NEW CONNECTION] {addr} connected\n")
    connected = True
    PresistantTime = 0
    No_Commands = 0
    while connected:

        msg = conn.recv(1024).decode(FORMAT)

        if msg:
            No_Commands = No_Commands + 1
            PresistantTime = time.time()
            if msg == DISCONNECT:
                print("I found a disconnect")
                break
            print(f"[{addr}] \n{msg}\n")
            ClientThread = threading.Thread(target=check, args=(msg, conn))
            ClientThread.start()
            # print(f"[This Clients Threads>>>>] {threading.active_count() - 2}")
        if (time.time() - PresistantTime) > 5 * No_Commands:
            print("Time Has Ran Out")
            print(time.time() - PresistantTime)
            connected = False
            break
    conn.close()
    print("\n\n Connection Closed>>>>>>>>>Time Out \n\n")


def check(sent, conn):
    AllSent = re.split('\r\n', sent)
    Command = AllSent[0].split(" ")
    print(Command)
    # Webs=AllSent[1].split(":")
    # Web = Webs[1].replace(" ", "")
    if Command[2] == "127.0.0.1":
        print("[SERVER] Local Searching........")
        if Command[0] == "POST":
            print("[SERVER] I am here in POST condition......")
            Filename = "Server_" + Command[1]
            f = open(Filename, mode='w', encoding='utf-8')
            f.write(AllSent[1])
            f.close()
            resp = "[SERVER] 200\ok........."
            conn.send(resp.encode(FORMAT))
            print("[SERVER] Done\n")
        elif Command[0] == "GET":
            print("[SERVER] I am here in GET condition......")
            try:
                file_name = Command[1].replace("/", "")
                if ".png" in file_name:
                    f = open(file_name, mode='rb')
                    data_read = f.read()
                    data = data_read
                    # print(data)
                    conn.send(data)
                    print("[SERVER] Done\n")
                    f.close()
                else:
                    f = open(file_name, mode='r', encoding='utf-8')
                    data_read = f.read()
                    data = data_read.encode(FORMAT)
                    conn.send(data)
                    print("[SERVER] Done\n")
                    f.close()
            except:
                print("[SERVER] Error 404 Not Found ")
                conn.send("[SERVER] Error 404 Not Found ")
                return

    elif Command[2] != "127.0.0.1":
        print("[SERVER] Global Searching........")
        try:
            PORT = Command[3]
        except:
            PORT = 80
        connect(Command[2], PORT)
        messages = f"{Command[0]} {Command[1]} HTTP/1.1\r\nHost: {Command[2]}:{PORT}\r\n\r\n"

        if Command[0] == "POST":
            print(f"[SERVER] I am here in POST condition......")
            data = send_file(Command)
            message = messages + data
            s_2.send(message.encode())
            response = s_2.recv(1024).decode(FORMAT)
            print(response)
            conn.send(response)
            print("[SERVER] Done\n")
        elif Command[0] == "GET":
            message = messages.encode(FORMAT)
            s_2.send(message)
            print(f"[SERVER] I am here in GET condition......")
            data = s_2.recv(4096).decode(FORMAT)
            data_2 = data.encode(FORMAT)
            conn.send(data_2)
            print("[SERVER] Done\n")


def send_file(client_send):
    try:
        file_name = client_send[1]
        f = open(file_name, mode='r', encoding='utf-8')
        data_read = f.read()
        f.close()
        return data_read
    except:
        print("[SERVER] Error 404 Not Found ")
        return


def start():
    s.listen()
    print(f"[LISTENING] server is listening on {HOST}\n\n")
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")


print("[STARTING] server is  starting .......")
start()
