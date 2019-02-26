# Name: Alejandro Balderrama
# Class: Computer Networks
# Assignment: UDP File Transfer
# Program: UDP Client
# Description: The following program implements a UDP client that interacts with a UDP 
#              server to either put or get files from the server.

import socket
import time

def put(fileName):
    mySocket.settimeout(1.0)    #Socket time out is set to 1 second
    
    with open(fileName, "rb") as binaryFile:    #Open specified file in binary mode 
        data = binaryFile.read()    #read() gives a bytes object
        totalBytes = len(data)      #Determine the number of bytes in the file
        
        numPackets = ((totalBytes/64) + 1)  #Calculate the number of packets to be transmitted
        
        lastPacketBytes = totalBytes % 64   #Calculate the number of bytes in the last packet
        
        fileInfoPacket = str(0)+'@'+'put'+'@'+fileName+'@'+str(numPackets)  #Info packet delimited by '@'
        
        mySocket.sendto(fileInfoPacket, serverAddress)  #Send the info packet to the server
        
        i = 0
        while i < (totalBytes - lastPacketBytes):   #Send all packets excluding the last packet
            binaryFile.seek(i)      #Determine bytes to be sent next
            dataBytes = binaryFile.read(64)     #Assign the next 64 bytes of the file to dataBytes
            packetNum = ((i / 64) + 1)      #Determine the current packet number
            
            dataBytes = str(packetNum)+'@'+dataBytes    #Prepend the packet number to the file bytes (delimiter '@')
            
            mySocket.sendto(dataBytes, serverAddress)   #Send packet to server
            sendTime = time.clock()     #Determine the packet send time
            acknowledged = False
            
            while not acknowledged:     #Loop while the packet acknowledgement has not been received
                try:
                    packetAck, address = mySocket.recvfrom(4096)    #Attempt to receive acknowledgement
                    receiveTime = time.clock()      #Determine packet receive time
                    roundTripTime = receiveTime - sendTime      #Calculate round trip time
                    
                    print("Received packet "+str(packetAck)+" acknowledgement from "+str(address))
                    print("Round trip time: "+str(roundTripTime))
                    
                    if packetAck == str(packetNum):     #Set acknowledged to true only if the packet...
                        acknowledged = True             #equals the the packet number sent
                        
                except socket.timeout:      #If the socket times out resend the packet
                    mySocket.sendto(dataBytes, serverAddress)
                        
            i += 64
            
        lastDataBytes = binaryFile.read(lastPacketBytes)        #Ready to send the last packet
        lastDataBytes = str(packetNum + 1)+'@'+lastDataBytes+'@'+'fin'  #Format last packet
        
        mySocket.sendto(lastDataBytes, serverAddress)       #Send last packet to server
        mySocket.close()        

def get(fileName):  
    fileInfoPacket = str(0)+'@'+'get'+'@'+fileName      #Format info packet
    mySocket.sendto(fileInfoPacket, serverAddress)      #Send info packet to server
    
    while 1:
        print("\nWaiting to receive file")
        packedData, senderServerAddress = mySocket.recvfrom(4096)   #Receive packets from server
        
        print("Received "+str(len(packedData))+" bytes from "+str(senderServerAddress))
        
        packetInfo = packedData.split('@')      #Split received packet by the delimiter '@'
        
        print(packetInfo[1])
        
        packetAck = packetInfo[0]       #Determine packet number received
        mySocket.sendto(packetAck, senderServerAddress)     #Send packet acknowledgement to server
       
        print("Sent packet "+str(packetAck)+" acknowledgement back to "+ str(senderServerAddress))


mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #Setup socket
serverAddress = ('localhost', 10000)    #Setup server address
clientAddress = ('localhost', 10010)    #Setup client address
mySocket.bind(clientAddress)    #Bind client address for listening

getPutInput = raw_input('Would you like to get or put a file? (get/put) ')  #Prompt for user input (get or put)

if getPutInput == 'put':
    fileName = raw_input('Please enter file name: ')    #Prompt for file
    
    put(fileName)   #Call put() for specified file
    
elif getPutInput == 'get':
    fileName = raw_input('Please enter file name: ')    #Prompt for file
     
    get(fileName)   #Call get() for specified file

else:       #User input not recognized
    while getPutInput != 'put' or getPutInput != 'get':
        getPutInput = raw_input('Would you like to get or put a file? (get/put) ')
        
        if getPutInput == 'put':
            fileName = raw_input('Please enter file name: ')    #Prompt for file
    
            put(fileName)   #Call put() for specified file
            break
    
        elif getPutInput == 'get':
            fileName = raw_input('Please enter file name: ')    #Prompt for file
     
            get(fileName)   #Call get() for specified file
            break