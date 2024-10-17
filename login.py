import socket
import struct
#from packetbuilder import packetbuilder #I'm having really big issues with how python uses bytes

HOST = "localhost"
PORT = 25565

handshakestatus = bytes([0x10, 0x00, 0xff, 0x05, 0x09, 0x6c, 0x6f, 0x63, 0x61, 0x6c, 0x68, 0x6f, 0x73, 0x74, 0x63, 0xDD, 0x01])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(handshake)
    # s.send(handshakestatus)
    # s.send(bytes([0x01, 0x00]))

    # print(str(s.recv(1024)))

    #enter login status
    s.send(bytes([0x10, 0x00, 0xff, 0x05, 0x09, 0x6c, 0x6f, 0x63, 0x61, 0x6c, 0x68, 0x6f, 0x73, 0x74, 0x63, 0xDD, 0x02]))
    #start login username and UUID
    s.send(bytes([0x18, 0x00, 0x06, 0x63, 0x6f, 0x6f, 0x6c, 0x69, 0x6f, 0x65, 0xB0, 0xFF, 0x3E, 0x4C, 0x4A, 0x2B, 0x1E, 0x65, 0xB0, 0xFF, 0x3E, 0x4C, 0x4A, 0x2B, 0x1E]))
    #get compression
    print(str(s.recv(1024)))
    #get login success
    print(str(s.recv(1024)))
    #send login aknowledged with non compression byte 0x00
    s.send(bytes([0x02, 0x00, 0x03]))
    #get required resource packs
    print(str(s.recv(1024)))
    #send same packet back with 0x07 instead lol
    s.send(bytes(b'\x19\x00\x07\x01\tminecraft\x04core\x061.21.1'))

    #in configuration mode
    while True:
        packet = s.recv(1024)
        if len(packet) >= 2 and packet[1] == 0x00: # 0x00 at pos 2 means uncompressed
            print(str(packet))
            #wait until finish config sent
            if packet == bytes([0x02, 0x00, 0x03]):
                #send acknowledge and go into play mode
                s.send(bytes([0x02, 0x00, 0x03]))
                print("sent fin conf")
                break
        elif len(packet) < 2 and len(packet) > 0: #packet should be uncompressed but maybe bigger than 1024?
            print(str(packet))

    #in play mode :DDDD
    while True:
        packet = s.recv(1024)
        if len(packet) >= 2 and packet[1] == 0x00:
            #print(str(packet))
            if packet[2] == 0x26: #solving keep alive packets :DDDD
                print("Got keep alive")
                print(str(packet))
                response = bytes([0x0a, 0x00, 0x18]) + packet[3:]
                s.send(response)

        elif len(packet) < 2 and len(packet) > 0:
            continue
            #print(str(packet))

