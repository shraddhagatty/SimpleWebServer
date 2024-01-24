import socket
import sys
import os

if len(sys.argv) != 2:
    sys.stderr.write("Provide port number")
    sys.exit(1)

port= int(sys.argv[1])

#Create a TCP socket on which to listen for new connections. 
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#Bind that socket to the port provided on the command line. 
sock.bind(("",port))

#Listen on the accept socket. 
#Using backlog of 5
sock.listen(5) 
#print(f'Listening on port {port}...')

while True:
    #a. Accept a new connection on the accept socket.
    client_connection, client_address = sock.accept()

    #sys.stderr.write(f"Connected by {client_address}")

    try:

        #b. Read the HTTP request from the connection socket and parse it. 
        #print(f"Client connection : {client_connection}")
        request = client_connection.recv(1024).decode('utf-8')
        filename = request.split()[1].split('/')[-1]
        
        #Check to see if the requested file requested exists (and ends with ".htm" or ".html").

        if os.path.isfile(filename) and (filename.endswith(".html") or filename.endswith(".htm")):

            #d. If the file exists, construct the appropriate HTTP response write the HTTP header to the connection socket
            
            with open(filename, "rb") as f:
                content = f.read().decode('utf-8')
            
            content_type = "text/html"
            content_length = len(content)
            #print(content_length)

            response = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{content}"
        else:
            #e. If the file doesn’t exist, construct a HTTP error response (404 Not Found) and write it to the connection socket. If the file does exist, but does not end with ".htm" or "html", then write a "403 Forbidden" error response.

            if os.path.exists(filename):
                response = "HTTP/1.0 403 Forbidden\r\n\r\n"
            else:
                response = "HTTP/1.0 404 Not Found\r\n\r\n"
                

        client_connection.sendall(response.encode("utf-8"))
    except Exception as e:
        print(f"Error processing request: {e}")
    finally:
        #f. Close the connection socket.
        client_connection.close()

sock.close()



