import sys
import os
import socket
import threading
import time
import pickle
import Crypto
from Crypto.PublicKey import RSA

MULTICAST_ADDR = '224.0.0.1'
BIND_ADDR = '0.0.0.0'
PORT = 3000
MULTICAST_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UNICAST_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMER = 1
NEW_NODE = 0
NEWS = 1
REPORT = 2
KEY = RSA.generate(1024)
PRIVATE_KEY = KEY.export_key()
PUBLIC_KEY = KEY.publickey().export_key()
IP_ADDR = socket.gethostbyname(socket.gethostname())

NODES = []

def sendNews():
    print('Noticia: ')
    # TODO enviar a noticia criptografada
    noticia = input()
    MULTICAST_SOCK.sendto(pickle.dumps([NEWS, noticia]), (MULTICAST_ADDR, PORT))

def reportNode():
    print("Informe o nome de quem enviou fake news")
    name_node = input()

    MULTICAST_SOCK.sendto(pickle.dumps([REPORT, name_node]), (MULTICAST_ADDR, PORT))

def welcomeNode():
    welcomeData, address = UNICAST_SOCK.recvfrom(1024)
    welcome_node = pickle.loads(welcomeData)
    if welcome_node[0] == NEW_NODE:
        print("Os nodes da rede dizem 'oi'!")
        NODES.append({
            "pub_key": welcome_node[1],
            "address": welcome_node[2],
            "name": welcome_node[3],
            "rep": welcome_node[4]
        })

    threading.Timer(TIMER, welcomeNode).start()

def receiveNews():
    data, address = MULTICAST_SOCK.recvfrom(1024)
    data_node = pickle.loads(data)

    if data_node[0] == NEW_NODE and data_node[1] != PUBLIC_KEY:
        print('Novo node adicionado a rede!')
        NODES.append({
            "pub_key": data_node[1],
            "address": data_node[2],
            "name": data_node[3],
            "rep": data_node[4]
        })
        # enviado a chave publica em unicast para quem acabou de chegar
        UNICAST_SOCK.sendto(pickle.dumps([NEW_NODE, PUBLIC_KEY, UNICAST_SOCK.getsockname(), NAME_PEER, NODES[0]["rep"]]), data_node[2])
    elif data_node[0] == NEWS:
        print('Noticia: ', data_node[1])
        # TODO funcao de assinatura digital

    elif data_node[0] == REPORT:
        for node in NODES:
            if node["name"] == data_node[1]:
                node["rep"] = 0
                print(NODES)
                print('Reputacao do node alterada!')

    threading.Timer(TIMER, receiveNews).start()

def main():
    global NAME_PEER
    global REPUTATION
    REPUTATION = 1
    print("Bem vindo a rede de noticias P2P! \nDigite seu nome: ")
    NAME_PEER = input()
    membership = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
    MULTICAST_SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    MULTICAST_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    MULTICAST_SOCK.bind((IP_ADDR, PORT))
    UNICAST_SOCK.bind((IP_ADDR, 0))
    MULTICAST_SOCK.sendto(pickle.dumps([NEW_NODE, PUBLIC_KEY, UNICAST_SOCK.getsockname(), NAME_PEER, REPUTATION]), (MULTICAST_ADDR, PORT))
    UNICAST_SOCK.sendto(pickle.dumps(['']), UNICAST_SOCK.getsockname())

    NODES.append({
        "pub_key": PUBLIC_KEY,
        "address": UNICAST_SOCK.getsockname(),
        "name": NAME_PEER,
        "rep": REPUTATION
    })

    print("tipo: ", type(NODES[0]))

    receiveNews()
    welcomeNode()

    option = -1
    while option != "0":
        print("Insira uma das opcoes a seguir:\n0: Sair da rede\n1: Enviar noticias na rede\n2: Reportar um node\n3: Ver nodes na rede")
        option = input()
        if option == "0":
            print("Saindo da rede")
            MULTICAST_SOCK.close()
            UNICAST_SOCK.close()
            os._exit(0)
        elif option == "1":
            sendNews()
        elif option == "2":
            reportNode()
        elif option == "3":
            print("Nodes na rede:")
            print(NODES)
        else:
            print("Insira uma opcao valida!")
    os._exit(0)

if __name__ == '__main__':
    main()
