import os
import socket
import threading
import time
import pickle
import Crypto
from Crypto.PublicKey import RSA
# from Crypto.Random import get_random_bytes
# from Crypto.Cipher import AES, PKCS1_OAEP

MULTICAST_ADDR = '224.0.0.1'
ENVIAR_NOTICIA = 1
MUDAR_REPUTACAO = 2
NOVO_NO = 3
RESPOSTA_NOVO_NO = 4
BIND_ADDR = '0.0.0.0'
PORT = 3000
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMER = 1
KEY = RSA.generate(1024)
PRIVATE_KEY = KEY.export_key()
PUBLIC_KEY = KEY.publickey().export_key()
NODES = []

def checkReputation(node):
    if reputation == 'Confiavel':
        reputation = 'Nao confiavel'
        reputation_node = [MUDAR_REPUTACAO, reputation]
        SOCK.sendto(pickle.dumps(reputation_node), (MULTICAST_ADDR, PORT))

def sendNews():
    print('Escreva a mensagem: ')
    noticia = input()
    news_node = [ENVIAR_NOTICIA, noticia]
    SOCK.sendto(pickle.dumps(news_node), (MULTICAST_ADDR, PORT))

def receiveThread():
    data_node_sender, address_sender = SOCK.recvfrom(1024)
    data_node = pickle.loads(data_node_sender)
    if data_node[0] == NOVO_NO:
        print("IP do node: ", address_sender[0], ", porta: ", address_sender[1])
        print("Chave publica do node: ", data_node[1])
        print("Reputacao do node: ", data_node[2])
        NODES = [data_node[1], data_node[2], address_sender]
        your_data = [RESPOSTA_NOVO_NO, PUBLIC_KEY, 'Confiavel']
        SOCK.sendto(pickle.dumps(your_data), address_sender)
    elif data_node[0] == RESPOSTA_NOVO_NO:
        NODES = [data_node[1], data_node[2], address_sender]
    elif data_node[0] == MUDAR_REPUTACAO:
        checkReputation()
    else:
        print("Noticia: ", data_node[1])

    threading.Timer(TIMER, receiveThread).start()

def main():
    reputation = 'Confiavel'
    tipoOperacao = NOVO_NO
    membership = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
    SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCK.bind((BIND_ADDR, PORT))

    data_node = [tipoOperacao, PUBLIC_KEY, reputation]
    SOCK.sendto(pickle.dumps(data_node), (MULTICAST_ADDR, PORT))

    receiveThread()

    print('Opcoes: \n 1 - Enviar noticia \n 2 - Avisar sobre reputacao de node \n 0 - Sair')
    tipoOperacao = input()

    while True:
        if tipoOperacao == "1":
            sendNews()
        elif tipoOperacao == "2":
            checkReputation()
        else:
            break
        print('Opcoes: \n 1 - Enviar noticia \n 2 - Avisar sobre reputacao de node \n 0 - Sair')
        tipoOperacao = input()
    os._exit(0)

if __name__ == '__main__':
    main()

# def sender():
#     while 1:
#
#         print('Escreva a mensagem: ')
#         mensagem = input().encode("utf-8")
#         file = open("encrypted_mensagem.bin", "wb")
#
#         recipient_key = RSA.import_key(public_key)
#         session_key = get_random_bytes(16)
#
#         cipher_rsa = PKCS1_OAEP.new(recipient_key)
#         enc_session_key = cipher_rsa.encrypt(session_key)
#
#         cipher_aes = AES.new(session_key, AES.MODE_EAX)
#         ciphertext, tag = cipher_aes.encrypt_and_digest(mensagem)
#
#         [ file.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
#         file.close()
#
#         SOCK.sendto(mensagem, (multicast_addr, port))
#         SOCK.sendto(private_key, (multicast_addr, port))
