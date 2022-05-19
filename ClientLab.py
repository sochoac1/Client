# ********************************************************************************************
    # Lab: Introduction to sockets
    # Course: ST0255 - Telemática
    # TCP-Socket Client
# ********************************************************************************************
#cd MultiThread\LabSocketsMultiThread\LabSocketsMultiThread
#Import libraries for networking communication...


from http import client
import socket
from unicodedata import name
from urllib import request
import constants
import base64
import os                   
import time                   
from bs4 import BeautifulSoup



def main():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('---------------- NEW CLIENT ----------------')
    print('Client is running...')
    server=input('Input the hostname: ')
    client_socket.connect((server,constants.PORT))
    local_tuple = client_socket.getsockname()
    print('Connected to the server from:', local_tuple)
    print('Enter \"quit\" to exit')
    print('Input commands:')
    command_to_send = input()
    while command_to_send != constants.QUIT:
        if command_to_send == '':
            print('Please input a valid command...')
            command_to_send = input()       
        #POST                 
        elif (command_to_send == constants.POST):
            data_to_send = input('Input data to send: ')
            if not checkFileExistance('Client/' + data_to_send):
                print('File not found')
            else:
                #Send request
                request=command_to_send+' '+data_to_send+' '+'HTTP/1.1\r\nHost: '+server+'\r\n\r\n'
                print(request.split('\r\n\r\n')[0])
                request=request.encode()
                #File to send
                file=open('Client/' + data_to_send,'rb')
                response=file.read()
                file.close()          
                final_response=request+response      
                client_socket.send(final_response)
                print("File transfer Complete. :)")
                #Receive response
                data_received = client_socket.recv(constants.RECV_BUFFER_SIZE)  
                print('Answer received')
                print(data_received.decode(constants.ENCONDING_FORMAT)) 
            print("**********************")
            #Stablish connection again
            client_socket.close()  
            #Create a new socket
            main() 
            return
            command_to_send = input()
        #GET   
        elif (command_to_send == constants.GET):
            #Send GET
            data_to_send = input('Input data to get:') 
            request = command_to_send + ' ' + data_to_send + ' ' + 'HTTP/1.1\r\nHost: ' + server + '\r\n\r\n'
            print(request.split('\r\n\r\n')[0])
            client_socket.send(request.encode()) 
            #Receive GET and save file
            actual=b's'
            res = b''
            while(True):
                actual = client_socket.recv(9999999)
                if(actual == b''):
                    break 
                else:
                    res += actual
            
            response = res.split(b"\r\n\r\n")
            print(response[0].decode()) 
            #200 or 404
            status_code = response[0].decode().split(' ')[1] 
            if(status_code == '200'):
                file_receive = response[1]
                if(data_to_send.lstrip('/') == ('')):
                    data_to_send ='html/index.html'
                file = open("./Client/"+data_to_send, 'wb')
                file.write(file_receive)
                file.close() 
                #Stablish connection again
                client_socket.close()   
                print('File receive :)')     
                if(data_to_send.endswith('.html')):
                    #Method parseGET
                    name_html = data_to_send.lstrip('/')
                    parseHtml(name_html, server)
                
                
            else:
                print(response[1].decode())
            #Create a new socket
            main() 
            return
            print("**********************")
            #command_to_send=input()
        #HEAD
        elif(command_to_send == constants.HEAD):        
            data_to_send = input('Input data to head:')
            #Send HEAD
            request = command_to_send + ' ' + data_to_send + ' ' + 'HTTP/1.1\r\nHost: ' + server + '\r\n\r\n'
            print(request.split('\r\n\r\n')[0])
            client_socket.send(request.encode())
            #Receive HEAD
            data_received = client_socket.recv(constants.RECV_BUFFER_SIZE)      
            print(data_received.decode(constants.ENCONDING_FORMAT))     
            print("**********************")
            command_to_send = input()
        else:
            print('Invalid command, try again:')
            command_to_send=input()
        
    request = command_to_send + ' ' + 'server' + ' ' + 'HTTP/1.1\r\nHost: ' + server + '\r\n\r\n'
    client_socket.send(request.encode())
    data_received = client_socket.recv(constants.RECV_BUFFER_SIZE)        
    print(data_received.decode(constants.ENCONDING_FORMAT))
    print('Closing connection...BYE BYE...')
    client_socket.close()    

#Method to find file existance
def checkFileExistance(filePath):
    try:
        with open(filePath, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False


def parseHtml(name_html, server):

    links =[]
    with open('Client/' + name_html) as fp:
        soup = BeautifulSoup(fp, "html.parser")
        images = soup.findAll('img') 
        css = soup.find_all('link')
        video = soup.find_all('video')
        for img in images:
            links.append(img['src'])
        for c in css:
            links.append(c['href'])
        for v in video:
            links.append(v['src']) 
    if len(links) > 0:
        print("**********************")
        for i in links:
            #Create new Client
            client = clientParser(server)
            request = 'GET' + ' ' +'/' + i + ' ' + 'HTTP/1.1\r\nHost: ' + server + '\r\n\r\n'
            print(request.split('\r\n\r\n')[0])
            client.send(request.encode()) 
            actual=b's'
            res = b''
            while(True):
                #print(actual)
                actual = client.recv(9999999)
                if(actual == b''):
                    break 
                else:
                    res += actual
            response = res.split(b"\r\n\r\n")
            print(response[0].decode()) 
            #200 or 404
            status_code = response[0].decode().split(' ')[1]
            if(status_code == '200'):
                #time.sleep(1.5)
                file_receive = response[1]
                #print(file_receive.decode())
                file = open("./Client/"+i, 'wb')
                file.write(file_receive)
                file.close()       
                print('File receive :)')
            else:
                print(response[1].decode())
            #Close client
            client.close()  
            print("**********************")

def clientParser(server):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((server,constants.PORT))
    return client


if __name__ == '__main__':
    main()