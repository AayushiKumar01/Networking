from socket import *
import sys
from pathlib import Path
from urllib.parse import urlparse 

## to check length of the argument to ensure port is passed
if len(sys.argv) <= 1:
    print ('Please pass the port number as an argument')
    sys.exit(2)


## Port Value for 10000 + (your student ID) % 2022 = 11921
proxy_port = int(sys.argv[1]) 
proxy_socket = socket(AF_INET, SOCK_STREAM)

# Binding proxy server socket
proxy_socket.bind(('', proxy_port))
proxy_socket.listen(1)

#method to retrieve client request
def get_hostname_and_file(fileName):
    
    split_values = fileName.split("/")
    hostName = split_values[2]
    file = split_values[3] + "/" + split_values[4]
    mainfolder = split_values[3] 
    mainfile = split_values[4] 
    return(hostName, file, mainfolder,mainfile)

#copy content in cache and send message to client when status = 200
def response_file_from_server(result):
    cache_path = Path(mainfolder).resolve()
    cache_path.mkdir(parents=True, exist_ok=True)
    (cache_path / mainfile).write_text(result)
    print('\n\nResponse received from server and the status is 200. Saving file in cache. Sending server\'s response to client.')
    response = result.splitlines()[0] +"\nCache hit 0\r\n" + result.splitlines()[-1]
    client_socket.send(response.encode())

#do not cache content and send message to client when status != 200
def no_responsefile_from_server(result,status):
    if status == '404':
        print("\nResponse receieved from server but status is not 200. File is not cahched. sending appropriate response to client")
        message = result.splitlines()[0]+ "\nCache hit 0\r\n" + "404 File not Found"

    elif status not in validStatus:
        print("\nResponse receieved from server but status is not 200. File is not cahched. sending appropriate response to client")
        message =result.splitlines()[0]+ "\nCache hit 0\r\n" + "Unsupported Error"

    client_socket.send(message.encode())

while True:
    # Proxy ready to receive request from client
    print ('\nProxy server is ready to serve.\n\n')
    client_socket, client_addr = proxy_socket.accept()
    print ('Received a connection from: ', client_addr)
    client_message = client_socket.recv(1024).decode()
    print('Client\'s message is:'+ client_message)
    
    # validating request url
    headers = urlparse(client_message).path.split()
    if len(headers) <3:
        print("Invalid request(malformed url)")
        message = "Cache hit 0\r\n" + "500 Unsupported Error.\nPlease check your request url."
        
        client_socket.send(message.encode())
        client_socket.close()
        sys.exit(2)

    #Parsing request after validating url length
    method = headers[0]
    filename = headers[1]
    requesttype = headers[2]
    
    
    #validating method and request type
    if method.lower() != 'get'  or requesttype != 'HTTP/1.0':
        print("Invalid request(malformed url)")
        message = "Cache hit 0\r\n" + "500 Unsupported Error.\nPlease validate the url"
        client_socket.send(message.encode())
        client_socket.close()


    else:
        hostn, filenametouse, mainfolder, mainfile = get_hostname_and_file(filename)
        
        #checking if hostname or filename is empty
        if(hostn == '' or filenametouse == ''):
            message = "Cache hit 0\r\n" +  "500 Unsupported Error.\n Please validate the url"
            client_socket.send(message.encode())
            client_socket.close()

        file_exists = "false"
        validStatus = ['200', '404']

        try:
        # Check whether the file exists in the cache
            f = open(filenametouse)
            cached_content = f.read()
            file_exists = "true"
            print ('\n\nYeah! Requested file exists in cache. Sending response to client from the cache.')
            response = cached_content.splitlines()[0] + "\nCache Hit :1\r\n" + cached_content.splitlines()[-1]
            client_socket.send(response.encode())
        
            # File not found in cache
        except IOError:
            if file_exists == "false":
                # Create a socket on the proxyserver
                print ('\nOOPS no cache hit.Creating socket on proxyserver\n')
                main_server = socket(AF_INET, SOCK_STREAM)
                try:
                    # Connect to the main server, port 80
                    main_server.connect((hostn, 80))
                    
                    request_server = "GET " + "/" + filenametouse + " HTTP/1.0\n\n"
                    print('\nsending the following message from proxy to server:\n'+request_server)
                    print ('Host:'+hostn)
                    main_server.send(request_server.encode())
                    result = main_server.recv(1024).decode()
                    print("\n\n"+ result)
                    header_content = result.splitlines()[0]
                    status = header_content.split(" ")[1]

                    if status == '200':
                        response_file_from_server(result)
                
                    else:
                        no_responsefile_from_server(result,status)
                
                    main_server.close()
                     
                except Exception as e:
                    print ('Bad Request!!!')
                    client_socket.send(("Bad Resquest").encode())
                    sys.exit(2)
        
    client_socket.close()        
             
            