import sys
import os
import socket
import threading
import time
import pickle
import Crypto
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

MULTICAST_ADDR = '224.0.0.1'
BIND_ADDR = '0.0.0.0'
PORT = 3000
MULTICAST_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UNICAST_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMER = 1
NEW_NODE = 0
SEND_NEWS = 1
REPORT = 2
IP_ADDR = socket.gethostbyname(socket.gethostname())
NODES = []
KEY = RSA.generate(2048)
PRIVATE_KEY = KEY.export_key()
PUBLIC_KEY = KEY.publickey().export_key()

def reportNode():
    name_node = input("Informe o nome de quem enviou fake news: ")
    #envia para todos os nodes na rede a nova reputacao do node reportado
    MULTICAST_SOCK.sendto(pickle.dumps([REPORT, name_node]), (MULTICAST_ADDR, PORT))

def sendNews(name_peer):
    news = input('Informe a noticia: ').encode('utf-8')
    for node in NODES:
        if node["name"] == name_peer:
            node_public_key = node["pub_key"]

    private_key = RSA.import_key(open('private-' + str(UNICAST_SOCK.getsockname()[1]) + '.pem', "rb").read())
    h = SHA256.new(news)
    signature = pss.new(private_key).sign(h)

    MULTICAST_SOCK.sendto(pickle.dumps([SEND_NEWS, news, signature, node_public_key, name_peer]), (MULTICAST_ADDR, PORT))

def receiveNews():
    data, address = MULTICAST_SOCK.recvfrom(1024)
    data_node = pickle.loads(data)

    #checando se operacao é que um novo node chegou na rede e se é o proprio node ou outro node da rede
    if data_node[0] == NEW_NODE and data_node[1] != PUBLIC_KEY:
        print('Novo node adicionado a rede!')
        NODES.append({ "pub_key": data_node[1], "address": data_node[2], "name": data_node[3], "rep": data_node[4] })
        # enviando a chave publica em unicast para quem acabou de chegar
        UNICAST_SOCK.sendto(pickle.dumps([NEW_NODE, PUBLIC_KEY, UNICAST_SOCK.getsockname(), NAME_PEER, NODES[0]["rep"]]), data_node[2])

    # checando se a operacao é o envio de uma noticia
    elif data_node[0] == SEND_NEWS:
        # public_key_import = RSA.import_key(PUBLIC_KEY) #pode ser usado para ver se a public key é diferente
        public_key_import = RSA.import_key(data_node[3]) #importanto a public key do node que enviou a noticia
        h = SHA256.new(data_node[1]) #criando uma hash com a noticia enviada
        verifier = pss.new(public_key_import)
        try:
            verifier.verify(h, data_node[2]) #verificando a hash e a assinatura
            print ('Noticia: ', data_node[1].decode('utf-8'), 'por', data_node[4])
        except (ValueError, TypeError): #caso um node esteja se passando por outro node
            print ('Nao foi possivel confirmar a autenticidade da noticia')

    elif data_node[0] == REPORT:
        for node in NODES:
            if node["name"] == data_node[1]: #o node que tiver o nome igual ao que foi digitado tem reputacao alterada para zero
                node["rep"] = 0
                print(NODES)
                print('Reputacao do node alterada!')

    threading.Timer(TIMER, receiveNews).start()

def welcomeNode():
    welcomeData, address = UNICAST_SOCK.recvfrom(1024) #recebendo as informacoes do node que entrou na rede
    welcome_node = pickle.loads(welcomeData)
    if welcome_node[0] == NEW_NODE: #verifica se a operacao foi a de um novo node entrando na rede
        print(welcome_node[3] + " mandou 'oi'") #cada node na rede envia em unicast para o node que entrou
        NODES.append({ "pub_key": welcome_node[1], "address": welcome_node[2], "name": welcome_node[3], "rep": welcome_node[4] })

    threading.Timer(TIMER, welcomeNode).start()

def main():
    global NAME_PEER, REPUTATION
    REPUTATION = 1
    NAME_PEER = input("Bem vindo a rede de noticias P2P!\nDigite seu nome: ")
    membership = socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
    MULTICAST_SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    MULTICAST_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    MULTICAST_SOCK.bind((IP_ADDR, PORT)) #ligando o socket do multicast, que todos os nodes ficaram escutando essa conexão
    UNICAST_SOCK.bind((IP_ADDR, 0)) #ligando o socket unicast com o ip da maquina e uma porta gerada aleatoriamente
    #enviando para o socket multicast os dados do node que entrou na rede
    MULTICAST_SOCK.sendto(pickle.dumps([NEW_NODE, PUBLIC_KEY, UNICAST_SOCK.getsockname(), NAME_PEER, REPUTATION]), (MULTICAST_ADDR, PORT))
    UNICAST_SOCK.sendto(pickle.dumps(['']), UNICAST_SOCK.getsockname())

    file_out = open('public-' + str(UNICAST_SOCK.getsockname()[1]) + '.pem', 'wb') #gravando a public key em um arquivo
    file_out.write(PUBLIC_KEY)
    file_out.close()

    file_out = open('private-' + str(UNICAST_SOCK.getsockname()[1]) + '.pem', 'wb') #gravando a private key em um arquivo
    file_out.write(PRIVATE_KEY)
    file_out.close()

    #adicionando a NODES as informacoes do node que entrou na rede agora (si proprio)
    NODES.append({ "pub_key": PUBLIC_KEY, "address": UNICAST_SOCK.getsockname(), "name": NAME_PEER, "rep": REPUTATION })

    receiveNews() #thread que escuta o recebimento de multicast
    welcomeNode() #thread que fica escutando e envia em unicast as informacoes de cada node quando um outro node entra na rede

    option = -1
    while option != "0":
        option = input("Insira uma das opcoes a seguir:\n0: Sair da rede\n1: Enviar noticias na rede\n2: Reportar um node\n3: Ver nodes na rede\n")
        if option == "0":
            print("Saindo da rede")
            #fechando as threads
            MULTICAST_SOCK.close()
            UNICAST_SOCK.close()
            os._exit(0)
        elif option == "1":
            sendNews(NAME_PEER) #metodo onde é enviado a noticia
        elif option == "2":
            reportNode() #metodo para reportar um node que tenha enviado uma fake news ou que nao seja confiavel
        elif option == "3":
            print("Nodes na rede:\n", NODES)
        else:
            print("Insira uma opcao valida!")
    os._exit(0)

if __name__ == '__main__':
    main()
