import sys
import socket
import threading
import time
import Crypto
from Crypto.PublicKey import RSA
# from Crypto.Random import get_random_bytes
# from Crypto.Cipher import AES, PKCS1_OAEP

MULTICAST_ADDR = '224.0.0.1'
BIND_ADDR = '0.0.0.0'
PORT = 3000
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMER = 1
KEY = RSA.generate(1024)
PRIVATE_KEY = KEY.export_key()
PUBLIC_KEY = KEY.publickey().export_key()


def sendNews():
    print('Escreva a mensagem: ')
    noticia = input()
    SOCK.sendto(noticia.encode('utf-8'), (MULTICAST_ADDR, PORT))

def receiveNews():
    # DEFINIR FORMA DE PRINTAR O IP, A CHAVE PUBLICA E A REPUTACAO QUANDO UM
    # NÓ CHEGAR, E NAO TODAS AS VEZES QUE MANDAR UMA NOTICIA

    # news_sender = SOCK.recvfrom(1024)
    # print("Noticia: ", news_sender[0])
    public_key_sender, address_sender = SOCK.recvfrom(1024)
    # reputation_sender = SOCK.recvfrom(1024)
    print("Chave publica: ", public_key_sender)
    print("Meu IP: ", address_sender[0])
    # print("Minha reputacao: ", reputation_sender[0])

    threading.Timer(TIMER, receiveNews).start()

def main():
    reputation = 'Confiavel'
    membership = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
    SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCK.bind((BIND_ADDR, PORT))

    file = open(MULTICAST_ADDR + ".txt", "w")
    file.writelines([MULTICAST_ADDR + "\n", PUBLIC_KEY.decode('utf-8') + "\n",  reputation + "\n"])
    file.close()

    SOCK.sendto(PUBLIC_KEY, (MULTICAST_ADDR, PORT))
    # SOCK.sendto(reputation.encode('utf-8'), (MULTICAST_ADDR, PORT)) # ENVIAR APENAS NA PRIMEIRA VEZ

    receiveNews()

    print('Voce pode enviar uma notícia digitando SIM ou NAO (para sair do programa), ou aguarde receber uma noticia')
    opcao = input()

    while opcao == 'SIM':
        sendNews()
        print('Voce pode enviar uma notícia digitando SIM ou NAO (para sair do programa), ou aguarde receber uma noticia')
        opcao = input()
    sys.exit() # POR QUE ESSE DIACHO NAO FINALIZA O PROGRAMA AAAAAA

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
