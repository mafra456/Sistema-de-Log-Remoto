# -*- coding: latin1 -*-
import socket
import sys
import struct
import time
import hashlib
import numpy as np

global SWS
global LAR
global LFS
global SW

def create_md5(message):
    return hashlib.md5(message.encode('latin1')).digest()


def valid_md5(message, md5):
    return create_md5(message) == md5


def createPackage(seqnum, message):

    seqnum = (seqnum).to_bytes(8, byteorder = 'big')
    sec,nsec = str(time.time()).split('.')

    sec = int(sec)
    nsec = int(nsec)

    sec = (sec).to_bytes(8, byteorder = 'big')
    nsec = (nsec).to_bytes(4, byteorder = 'big')
    sz = (len(message)).to_bytes(2, byteorder = 'big')
    hashed_md5 = create_md5(message)
    package = seqnum + sec + nsec + sz + message.encode('ascii') + hashed_md5
    
    return package
def returnTuple(dest):
    #...
    split = np.empty(2,dtype=object)
    split[0] = list()
    split[1] = list()
    HOST = ""
    PORT = ""
    i = 0
    for s in dest:
        if(s == ':'):
            i = 1
        else:
            split[i] += s
    HOST = ''.join(split[0])
    PORT = ''.join(split[1])
    PORT = int(PORT)
    return HOST, PORT

def main():
    t_start = time.time()
    #PARAMS
    param = sys.argv[1:] 
    filename = param[0]
    dest = param[1]
    HOST, PORT = returnTuple(dest)
    Wtx = param[2]
    Tout = param[3]
    Perror = param[4]

    # Variaveis da Janela Deslizante

    # Tamanho da janela
    SWS = int(Wtx)
    # Ultima confirmacao recebida
    LAR = 0
    # Ultimo quadro enviado
    LFS = 0
    # Janela
    SW = [""] * SWS    

    file = open(filename,"r")
    seqnum = 0
    sec = 0
    nsec = 0
    size_message = 0
    package = ""

    n_distinct_logs = 0
    n_sent_logs = 0
    n_failed_md5_logs = 0
    try:
        socket.setdefaulttimeout(15)
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        print(HOST)
        print(PORT)
        dest = (HOST, PORT)
        udp.connect(dest)
        print('Conectado! Para sair, use CTRL+X\n')
        for line in file:
            message = line
            package = createPackage(seqnum, message)
            udp.send(package)

            n_distinct_logs = n_distinct_logs + 1
            n_sent_logs = n_sent_logs + 1

            response, address = udp.recvfrom(36)

            md5 = (response[20:36])#.decode('ascii')

            if(valid_md5(message, md5)):
                res_seqnum = int.from_bytes(response[:8], byteorder='big')
                res_sec = int.from_bytes(response[8:16], byteorder='big')
                res_nsec = int.from_bytes(response[16:20], byteorder='big')
                print("ACK #{} recebido".format(res_seqnum)) 
            else:
                n_failed_md5_logs = n_failed_md5_logs + 1

            seqnum = seqnum + 1
            
            #print(n_distinct_logs + " " + n_sent_logs + " " + n_failed_md5_logs + " %.3f"%(time.time()-t_start))
    except(socket.timeout):
        print("Tempo limite de conexão excedido")
        pass

if __name__ == "__main__":
    main()
    print ("Término da execução")
    #python3 cliente.py input.txt 127.0.0.1:5000 5 10 0.85

