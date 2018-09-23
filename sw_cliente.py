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
global n_distinct_logs
global n_sent_logs
global n_failed_md5_logs

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
    package = seqnum + sec + nsec + sz + message.encode('latin1') + hashed_md5
    print("Package a ser enviada:\n seqnum: {} \n sec: {} \n nsec: {} \n sz: {} \n message: {} \n md5: {} ".format(seqnum, sec, nsec, sz, message, hashed_md5))
    
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

def returnSeqPackage(SW,SWS,response):
    match = 0
    #print("SW" + str(len(SW)))
    for i in range(len(SW)):#while(match == 0 or i < SWS):
        package = createPackage(i, SW[i])
        rsp = int.from_bytes(response[:8], byteorder='big')
        pck = int.from_bytes(package[:8], byteorder='big')
        print("rsp " + str(rsp))
        print("esperado " + str(pck))
        if(rsp == pck):
            match = 1
            return i, package
    return -1, "this ack is not valid"
        
    #if(match == 0):
    #    return 99
    # else:
    #     return i

def sendPackage(udp,SW,seqnum):
    for p in range(len(SW)):
        package = createPackage(seqnum, SW[p])
        udp.send(package)
        LFS = package[:8] #ultimo quadro enviado (Tenho que conferir se ele enviou todos?)

def serverSocket(udp,SWS,SW,sent_pck_wdw):
    print("entrou")
    to_receive = 0
    while(True):
        if(to_receive == sent_pck_wdw):
            break;            
        response, address = udp.recvfrom(36)
        print("RECEBEU UM ACK")
        print(response)
        index, package = returnSeqPackage(SW,SWS,response)
        print("returncode" + str(index))

        if(index != -1):
            to_receive = to_receive + 1
            LAR = package[:8]#ultimo quadro recebido	
            md5 = (response[20:36])
            sz = int.from_bytes(package[20:22], byteorder='big')
            msg_end = sz + 22
            msg_decoded = (package[22:msg_end]).decode('latin1')
            if(valid_md5(msg_decoded, md5)):
                print("md5 validated")
                res_seqnum = int.from_bytes(response[:8], byteorder='big')
                res_sec = int.from_bytes(response[8:16], byteorder='big')
                res_nsec = int.from_bytes(response[16:20], byteorder='big')
                print("ACK #{} recebido".format(res_seqnum)) 
            else:
                print("falha no MD5 recebido")
                #n_failed_md5_logs = n_failed_md5_logs + 1

        elif(index == -1):
            to_receive = to_receive + 1
            package = createPackage(index, SW[index])
            udp.send(package)
            print("RETRANSMITIU")
            n_sent_logs = n_sent_logs + 1
            r_SW = []
            r_SW.append(SW[i])
            serverSocket(udp,1,r_SW)	

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
    #SW = bytearray()

    file = open(filename,"r")
    #num_lines = sum(1 for line in file)
    seqnum = 0
    sec = 0
    nsec = 0
    size_message = 0
    package = ""
    sent_pck_wdw = 0

    try:
        socket.setdefaulttimeout(int(Tout))
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        print(HOST)
        print(PORT)
        dest = (HOST, PORT)
        udp.connect(dest)
        print('Conectado! Para sair, use CTRL+X\n')
        n_distinct_logs = 0
        n_sent_logs = 0
        n_failed_md5_logs = 0
        count = 0
        while True:
            line = file.readline()
            count = count + 1
            print("count " + str(count))
            if(seqnum % SWS == 0 and seqnum != 0):
                sendPackage(udp,SW,seqnum)
                print("ENVIEI PACOTE #{}".format(seqnum))
                n_distinct_logs = n_distinct_logs + 1
                n_sent_logs = n_distinct_logs
                serverSocket(udp,SWS,SW,sent_pck_wdw)
                sent_pck_wdw = 0
                
            elif(line == ""):
                sendPackage(udp,SW,seqnum)
                print("ENVIEI PACOTE #{}".format(seqnum))
                n_distinct_logs = n_distinct_logs + 1
                n_sent_logs = n_distinct_logs
                serverSocket(udp,SWS,SW,sent_pck_wdw)
                sent_pck_wdw = 0
                print("file finished")
                break
            
            else:
                message = line
                SW.append(message)
                sent_pck_wdw = sent_pck_wdw + 1
                #print(type(SW[0]))

            seqnum = seqnum + 1
            print("seqnum " + str(seqnum))
            
        print(str(n_distinct_logs) + " " + str(n_sent_logs) + " " + str(n_failed_md5_logs) + " %.3f"%(time.time()-t_start)) #+ " %.3f"%(time.time()-t_start)

    except(socket.timeout):
        print("Tempo limite de conexão excedido")
        pass

if __name__ == "__main__":
    main()
    print ("Término da execução")
#python3 sw_cliente.py input.txt 127.0.0.1:5000 5 10 0.85
