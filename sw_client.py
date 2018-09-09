# -*- coding: utf-8 -*-
import socket
import sys
import struct
import hashlib

def returnSecNsec():
    diff = time.time()
    sec, nsec = diff // 3600, diff % 3600
    return sec, nsec

def createPackage(seqnum, sec, nsec, size_message, message):
    m = md5.new()
    fields = str(seqnum) + str(sec) + str(nsec) + size_message + message
    m.update(fields)
    md5 = m.digest()
    package = fields + md5
    return package
def returnTuple():
    #...
    PORT = int(PORT)
    return HOST, PORT

def main():
    #PARAMS
    param = sys.argv[1:] 
    filename = param[0]
    dest = param[1]
    Wtx = param[2]
    Tout = param[3]
    Perror = param[4]

    file = open(filename,"r")
    seqnum = 0
    sec = 0
    nsec = 0
    size_message = 0
    package = ""
    try:
        socket.setdefaulttimeout(15)
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        udp.connect(dest)
        print('Conectado! Para sair, use CTRL+X\n')
        for line in file:
            sec,nsec = returnSecNsec()
            message = line
            size_message = len(message)
            package = createPackage(seqnum, sec, nsec, size_message, message)
            udp.send(package.encode('latin1'))
            server_confirmation = udp.recv(36).decode('latin1')
            #TRATAR DE SERVER_CONFIRMATION POR EXEMPLO SE O MD5 ESTA 
            #CORRETO E OUTRAS VALIDACOES
            seqnum = seqnum + 1
        #AO FINAL DA EXECUCAO O CLIENTE DEVE IMPRIMIR UMA LINHA COM O
        #NUMERO DE MENSAGENS DE LOG DISTINTAS, DE LOGS TRANSMITIDAS
        #INCLUINDO RETRANSMISSOES E O NUMERO DE TRANSMITIDAS COM md5
        #INCORRETO
    except(socket.timeout):
        print("Tempo limite de conexão excedido")
        pass

if __name__ == "__main__":
    main()
    print ("Término da execução")

    #python3 sw_client.py log.txt 127.0.0.1:5000 5 10 0.85

