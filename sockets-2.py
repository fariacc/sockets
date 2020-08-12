import sys
import os
import socket
import threading
import time
import Crypto
from Crypto.PublicKey import RSA

MULTICAST_ADDR = '224.0.0.1'
BIND_ADDR = '0.0.0.0'
PORT = 3000
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMER = 1
KEY = RSA.generate(1024)
PRIVATE_KEY = KEY.export_key()
PUBLIC_KEY = KEY.publickey().export_key()
IPADDR = socket.gethostbyname(socket.gethostname())

known_nodes = []

def sendNews():
    print('Message: ')
    noticia = PUBLIC_KEY.decode('utf-8') + ',' + input()
    SOCK.sendto(noticia.encode('utf-8'), (MULTICAST_ADDR, PORT))

def reportNode(node_public_key):
    SOCK.sendto((node_public_key + ',' + "report").encode('utf_8'), (MULTICAST_ADDR, PORT))

def receiveNews():
    data, address = SOCK.recvfrom(1024)
    info = data.decode('utf_8').split(',', maxsplit=1)

    # if it's me, don't show anything
    if info[0] != PUBLIC_KEY.decode('utf_8'):
        # it may be a newcomer or some message
        #if it's a newcomer, there won't be any ,
        
        if len(info) > 1:
            if info[1] == "report":
                for node in known_nodes:
                    if node["pub_key"] == info[0]:
                        node["rep"] = 0
                        print(known_nodes)
                        print('Node reputation changed!')
            else:
                print("Message: ", info[1])
                isReported = input("Insert 1 to report or 0 to continue: ")
                if isReported == '1':
                    reportNode(info[0])
        else:
            known_nodes.append({
                "ip": address,
                "pub_key": info[0],
                "rep": 1
            })
            print('Newcomer added to known nodes!')
            #print(known_nodes)

    threading.Timer(TIMER, receiveNews).start()

def main():
    print("Welcome to the P2P News Sharing Network") 
    reputation = 1
    membership = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
    SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCK.bind((BIND_ADDR, PORT))
    SOCK.sendto(PUBLIC_KEY, (MULTICAST_ADDR, PORT))

    receiveNews()

    option = -1
    while option != "0":
        print("Please insert one of the following options:\n0: Leave network\n1: Send news to network\n2: Check known nodes")
        option = input()
        if option == "0":
            print("Leaving network")
            SOCK.close()
            os._exit(0)
        elif option == "1":
            sendNews()
        elif option == "2":
            print("Known nodes:")
            print(known_nodes)
        else:
            print("Insert one of the possible options!")
    os._exit(0)

if __name__ == '__main__':
    main()