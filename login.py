import socket
import struct
import zlib
from identifypacket import identify
#from packetbuilder import packetbuilder #I'm having really big issues with how python uses bytes

HOST = "localhost"
PORT = 25565

handshakestatus = bytes([0x10, 0x00, 0xff, 0x05, 0x09, 0x6c, 0x6f, 0x63, 0x61, 0x6c, 0x68, 0x6f, 0x73, 0x74, 0x63, 0xDD, 0x01])

def waituntilpacket(bit=0x00, position=0):
    while True:
        check = bytearray(s.recv(1024))
        if check[position] == bit:
            break
    return check


def removepacketlength(packet=bytearray):
    count = 0
    for i in range(len(packet)):
        binary = bin(int(packet[i]))[2:].zfill(8)
        #print(binary)
        if binary[:1] == "0":
            #print(i+1)
            count = i+1
            break
        else:
            continue
    return count




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(handshake)
    # s.send(handshakestatus)
    # s.send(bytes([0x01, 0x00]))

    # print(str(s.recv(1024)))

    #enter login mode
    s.send(bytearray([0x10, 0x00, 0xff, 0x05, 0x09, 0x6c, 0x6f, 0x63, 0x61, 0x6c, 0x68, 0x6f, 0x73, 0x74, 0x63, 0xDD, 0x02]))
    #start login username and UUID
    s.send(bytearray([0x18, 0x00, 0x06, 0x63, 0x6f, 0x6f, 0x6c, 0x69, 0x6f, 0x65, 0xB0, 0xFF, 0x3E, 0x4C, 0x4A, 0x2B, 0x1E, 0x65, 0xB0, 0xFF, 0x3E, 0x4C, 0x4A, 0x2B, 0x1E]))
    #get compression
    print(str(s.recv(1024)))
    #get login success
    print(str(s.recv(1024)))
    #send login aknowledged with non compression byte 0x00
    s.send(bytearray([0x02, 0x00, 0x03]))
    #get required resource packs
    
    resourcepacks = waituntilpacket(0x0e, 2)
    print(resourcepacks)

    #send same packet back with 0x07 instead lol
    resourcepacks[2] = 0x07
    s.send(resourcepacks)

    #in configuration mode
    while True:
        packet = bytearray(s.recv(2097151))
        length = removepacketlength(packet)
        packet = packet[length:]

        if len(packet) >= 2 and packet[0] > 0x00:
            try:
                #print(packet)
                remove = removepacketlength(packet)
                uncompressed = zlib.decompress(packet[remove:], zlib.MAX_WBITS|32)
                f = open("./uncompacket.txt", "a")
                #print(str(uncompressed), file=f)
                f.close()
            except:
                f = open("./errorpacket.txt", "a")
                #print(str(packet)+ "\n\n", file = f)
                f.close()
                print("!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!!!!!")
                f.close()
                continue
        if len(packet) >= 2 and packet[0] == 0x00: # 0x00 at pos 2 means uncompressed
            #print(str(packet))
            #wait until finish config sent
            if packet[1] == 0x03:
                #send acknowledge and go into play mode
                s.send(bytes([0x02, 0x00, 0x03]))
                print("sent fin conf")
                break
        elif len(packet) < 2 and len(packet) > 0: #packet should be uncompressed but maybe bigger than 1024
            print(str(packet))

    #in play mode :DDDD
    #try send comple login packet to spawn
    s.send(bytearray([0x03, 0x00, 0x09, 0x01]))
    while True:
        packet = bytearray(s.recv(2097151))
        length = removepacketlength(packet)
        packet = packet[length:]

        if len(packet) >= 2 and packet[0] > 0x00:
            try:
                remove = removepacketlength(packet)
                uncompressed = zlib.decompress(packet[remove:], zlib.MAX_WBITS|32)
                f = open("./uncompacket.txt", "a")
                print(str(uncompressed), file=f)
                f.close()
            except:
                f = open("./errorpacket.txt", "a")
                #print(str(packet)+ "\n\n", file = f)
                f.close()
                print("!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!!!!!")
                f.close()
                continue
        elif len(packet) >= 2 and packet[0] == 0x00:
            #print(str(packet))
            print(identify.play(packet[1:]))
            if packet[1] == 0x26: #solving keep alive packets :DDDD
                print("Got Keep ALive")
                print(packet)
                response = bytearray([0x0a, 0x00, 0x18]) + packet[2:]
                print(response)
                s.send(response)

        else:
            continue
            #print(str(packet))
