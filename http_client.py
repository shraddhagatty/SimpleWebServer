import sys
import socket
import re

def main():
    curl_clone(sys.argv[1])


def curl_clone(hostname, retry = 0): 

    #default port
    port = 80 

    if retry >= 10: 
        sys.stderr.write("Number of retries on redirect reached max of 10\n")
        sys.exit(10)
    
    endpoint = "/"
    if not hostname.startswith("http://"): 
        sys.stderr.write("Url does not begin with 'http://'\n")
        sys.exit(2)
    else: 
        hostname = hostname[7:]
        endpoint_index = hostname.find("/")
        if endpoint_index != -1:
            if re.search(":\d", hostname): 
                port = int(hostname[re.search(":\d", hostname).start()+1: endpoint_index])
                hostname = hostname[:re.search(":\d", hostname).start()] + hostname[endpoint_index:]
                endpoint_index = -1
            endpoint = hostname[endpoint_index:]
            hostname = hostname[:endpoint_index]
        # if hostname[:4] == "www.": 
        #     hostname = hostname[4:]
        
    #create socket and TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = socket.gethostbyname(hostname)    
    
    #sys.stderr.write(f"Connecting to host {hostname} at address {host_ip} on port {port}\n")
    s.connect((host_ip, port))


    #send request
    request = f"GET {endpoint} HTTP/1.0\r\nHost: {hostname}\r\n\r\n"
    s.sendall(request.encode())

    header = s.recv(1024)
    if header == "": 
        sys.stderr.write("Response is empty\n")
        sys.exit(1)
    
    header = header.decode()
    content_length = re.search("Content-Length:", header)

    #part of response retrieved in header call
    response_so_far = sys.getsizeof(header[header.find("<"):])

    if content_length == None: 
        response = b""
        while True: 
            part_response = s.recv(pow(10, 5))
            if part_response == b"": 
                break
            response += part_response

    else:
        buff = int(header[content_length.end():].split("\n")[0].strip()) - response_so_far
        response = b""
        while len(response) < buff:
            part_response = s.recv(1048576)
            response += part_response

    if response == "": 
        sys.stderr.write("Response is empty\n")
        sys.exit(1)
    #check response and status code
    response = response.decode()
    body = header[header.find("<"):] + response

    status_range = re.search("\d{3}", header)
    status_code = int(header[status_range.start():status_range.end()])
    
    if status_code == 200:
        content_type = re.search("Content-Type: text/html", header)

        if content_type == None:  #check content type is text/html
            sys.stderr.write("Content type is not text/html\n")
            sys.exit(5)

        sys.stdout.write(body)
        sys.exit(0)
    elif status_code == 301 or status_code == 302:
        #url is after location in header
        location = re.search("Location:", header) or re.search("location:", header)
        new_url = header[location.end():].split("\n")[0]

        sys.stderr.write(f"Redirected to: {new_url.strip()}\n")
        print("RESPONSE\n", header)
        curl_clone(new_url.strip(), retry=retry+1)
    elif status_code >= 400: 
        sys.stdout.write(body)
        sys.stderr.write("Error code >= 400\n")
        sys.exit(4)

    s.close()

if __name__ == "__main__": 
    main()