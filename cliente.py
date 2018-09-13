# -*- coding: utf-8 -*-
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
	return hashlib.md5(message.encode('utf-8')).digest()

def valid_md5(message, md5):
	return create_md5(message) == md5

def returnSecNsec():
    diff = time.time()
    sec, nsec = diff // 3600, diff % 3600
    return sec, nsec

def createPackage(seqnum, sec, nsec, size_message, message):
    m = hashlib.md5()
    fields = str(seqnum) + str(sec) + str(nsec) + str(size_message) + message
    fields = fields.encode('latin1')
    m.update(fields)
    md5 = m.digest()
    package = fields + md5
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
            sec,nsec = returnSecNsec()
            message = line
            size_message = len(message)
            package = createPackage(seqnum, sec, nsec, size_message, message)
            udp.send(package)

            n_distinct_logs = n_distinct_logs + 1
            n_sent_logs = n_sent_logs + 1

            response, address = udp.recv(36).decode('utf-8')
            md5 = response[20:36]

            if(valid_md5(message, md5)):
                res_seqnum = int.from_bytes(response[:8], byteorder='big')
                print("ACK #{} recebido".format(res_seqnum)) 
            else:
                n_failed_md5_logs = n_failed_md5_logs + 1

            seqnum = seqnum + 1
            
            print(n_distinct_logs + " " + n_sent_logs + " " + n_failed_md5_logs + " %.3f"%(time.time()-t_start))
    except(socket.timeout):
        print("Tempo limite de conexão excedido")
        pass

if __name__ == "__main__":
    main()
    print ("Término da execução")

    #python3 sw_client.py log.txt 127.0.0.1:5000 5 10 0.85

