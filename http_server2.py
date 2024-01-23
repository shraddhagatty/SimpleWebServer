import socket
import os
import sys
import select

if len(sys.argv) != 2:
    print(" provide port number")
    sys.exit(1)

port= int(sys.argv[1])

server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server_socket.bind(("",port))

server_socket.listen(5) 
print(f'Listening on port {port}...')

# Initialize the list of open connections to empty
#readlist
open_connections = [server_socket]

#Multiple connections using select

while True:

    # Make a list of sockets to wait for reading (read list)
    read_list = open_connections

    # Use select to wait for activity on any socket
    readable, writable, exceptional = select.select(read_list,[],[])

    for sock in readable:
        if sock is server_socket:
            #New Connection
            client_connection, client_address = server_socket.accept()
            open_connections.append(client_connection)
        else:
            #Existing Connection
            request = sock.recv(1024).decode('utf-8')
            filename = request.split()[1].split('/')[1]

            if os.path.isfile(filename) and (filename.endswith(".html") or filename.endswith(".htm")):
                with open(filename, "rb") as f:
                    content = f.read().decode('utf-8')
        
                response = "HTTP/1.0 200 OK\r\n\r\n" + content

                sock.sendall(response.encode("utf-8"))
            else:
                if os.path.exists(filename):
                    response = "HTTP/1.0 403 Forbidden\r\n\r\n"
                else:
                    response = "HTTP/1.0 404 Not Found\r\n\r\n"

                sock.sendall(response.encode("utf-8"))

            sock.close()
            open_connections.remove(sock)

            








