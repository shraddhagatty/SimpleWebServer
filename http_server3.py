import sys 
import socket 
import json 
import re

def main():

    if len(sys.argv) != 2: 
        sys.stderr.write("Must give port number\n")
        sys.exit(1)
    
    try: 
        port = int(sys.argv[1])
    except ValueError: 
        sys.stderr.write("Must give a valid number\n")
        sys.exit(1)

    server(port)

def server(port): 

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    host = ""

    #bind socket
    s.bind((host,port))

    #'open' socket to connections
    s.listen() 
    print(f'Listening on port {port}...')

    while True:

        #accept connections
        client_connection, client_address = s.accept()

        print(f"Connected by {client_address}")

        #receive request 
        request = b""
        while True: 
            part_request = client_connection.recv(1024)
            request += part_request
            if re.search(b"\r\n\r\n", request) != None: 
                break
        request = request.decode('utf-8').strip()

        response = None
        if not request.startswith("GET "):
            response = "HTTP/1.0 400 Bad Request\r\n\r\n"
        elif not request[4:].startswith("/product"): 
            response = "HTTP/1.0 404 Not Found\r\n\r\n"
        else: 
            try: #check that params are formatted correctly 
                params_list = request[12:].split("?")[1].split("&")   
            except: 
                sys.stderr.write("Params are not in proper format\n")
                response = "HTTP/1.0 400 Bad Request\r\n\r\n"
            else:
                if len(params_list) < 2: #make sure there are at least two params
                    response = "HTTP/1.0 400 Bad Request\r\n\r\n"
                else:
                    operands = []
                    result = 1
                    for param in params_list: 
                        num = param[param.find("=")+1:]

                        try: #check if input is a number
                            result *= float(num)
                        except: 
                            sys.stderr.write(f"{num} was not a number\n")
                            response = "HTTP/1.0 400 Bad Request\r\n\r\n"
                            break
                        else: #if it is a number, append it to the list
                            if num == "inf" or num == "-inf":
                                operands.append("inf")
                            elif float(num).is_integer():  
                                operands.append(int(num)) 
                            else:
                                operands.append(float(num)) 

                     
                    if not response: #check that a bad request has not been detected previously       

                        #all input was valid, now send response
                        if result == float("inf"):
                            result = "inf"
                        elif result == float("-inf"):
                            result = "-inf"
                        elif result.is_integer():
                            result = int(result)

                        body = {'operation': 'product', 'operands': operands, 'result': result}
                        
                        response = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(body) + "\r\n\r\n"

        #send response and close connection
        client_connection.sendall(response.encode("utf-8"))
        client_connection.close()

if __name__ == "__main__": 
    main()