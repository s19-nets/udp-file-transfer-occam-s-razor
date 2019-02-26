# Name: Alejandro Balderrama
# Class: Computer Networks
# Assignment: UDP File Transfer
# Program: UDP Server
# Description: The following program implements a UDP server that interacts with a UDP 
#              client to either send or receive files from the client.

import socket
import time

def receive(fileName, numPackets):
    while 1:
        print("\nWaiting to receive message")
        packedData, clientAddress = mySocket.recvfrom(4096)     #Receive packets from client
        
        print("Received "+str(len(packedData))+" bytes from "+str(clientAddress)+" regarding "+fileName)
    
        packetInfo = packedData.split('@')      #Split received packet by the delimiter '@'
        
        print(packetInfo[1])
        
        packetAck = packetInfo[0]   #Determine packet number received
        mySocket.sendto(packetAck, clientAddress)   #Send packet acknowledgement to client
    
        print("Sent packet "+str(packetAck)+"/"+str(numPackets)+" acknowledgement back to "+ str(clientAddress))

def send(fileName):
    mySocket.settimeout(1.0)    #Socket time out is set to 1 second
    
    with open(fileName, "rb") as binaryFile:    #Open specified file in binary mode
        data = binaryFile.read()    #read() gives a bytes object
        totalBytes = len(data)      #Determine the number of bytes in the file
        
        numPackets = ((totalBytes/64) + 1)  #Calculate the number of packets to be transmitted
        
        lastPacketBytes = totalBytes % 64    #Calculate the number of bytes in the last packet
        
        sendFileInfoPacket = fileName+'@'+str(numPackets)   #Info packet delimited by '@'
        
        mySocket.sendto(sendFileInfoPacket, clientAddress)  #Send the info packet to the server
        
        i = 0
        while i < (totalBytes - lastPacketBytes):   #Send all packets excluding the last packet
            binaryFile.seek(i)      #Determine bytes to be sent next
            dataBytes = binaryFile.read(64)     #Assign the next 64 bytes of the file to dataBytes
            packetNum = ((i / 64) + 1)      #Determine the current packet number
            
            dataBytes = str(packetNum)+'@'+dataBytes    #Prepend the packet number to the file bytes (delimiter '@')
            
            mySocket.sendto(dataBytes, clientAddress)   #Send packet to client
            sendTime = time.clock()     #Determine the packet send time
            acknowledged = False
            
            while not acknowledged:     #Loop while the packet acknowledgement has not been received
                try:
                    packetAck, address = mySocket.recvfrom(4096)    #Attempt to receive acknowledgement
                    receiveTime = time.clock()      #Determine packet receive time
                    roundTripTime = receiveTime - sendTime      #Calculate round trip time
                    print("Received packet "+str(packetNum)+" acknowledgement from "+str(address))
                    print("Round trip time: "+str(roundTripTime))
                    packetData = packetAck.split('@')   #Split received packet by the delimiter '@'
                    packetNumAck = packetData[0]    #Determine packet number received
                    
                    if packetNumAck == str(packetNum):      #Set acknowledged to true only if the packet...
                        acknowledged = True                 #equals the the packet number sent
            
                except socket.timeout:     #If the socket times out resend the packet 
                    mySocket.sendto(dataBytes, clientAddress)
            
            i += 64
            
        lastDataBytes = binaryFile.read(lastPacketBytes)    #Ready to send the last packet
        packetNum = int(packetNum) + 1
        lastDataBytes = str(packetNum)+'@'+lastDataBytes+'@'+'fin'  #Format last packet
        
        mySocket.sendto(lastDataBytes, clientAddress)   #Send last packet to server
        mySocket.close()


mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #Setup socket
serverAddress = ('localhost', 10000)    #Setup server address
mySocket.bind(serverAddress)        #Bind server address for listening
clientAddress = ('localhost', 10010)    #Setup client address

print("Starting up on "+str(serverAddress[0])+" port "+str(serverAddress[1]))

while 1:
    packedData, clientAddress = mySocket.recvfrom(4096)     #Receive packet from client
    
    packetInfo = packedData.split('@')      #Split received packet by the delimiter '@'
    
    if packetInfo[0] == '0':    #Packet received is info packet
        clientRequest = packetInfo[1]   #Determine client's request
        
        if clientRequest == 'put':  #Client put request
            receive(packetInfo[2], int(packetInfo[3]))
            
        elif clientRequest == 'get':    #Client get request
            send(packetInfo[2])
            break