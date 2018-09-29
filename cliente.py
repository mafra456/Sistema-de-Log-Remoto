import threading
import socket
import sys
import os
import time
import hashlib
import random
import numpy as np
import pdb
import traceback

''' 
INT 8 bytes – Número de sequencia
começa em 0 e incrementa
INT 8 bytes & INT 4 byets Timestamp 
o primeiro inteiro representa a quantidade de segundos desde a data de 
referência do período corrente, e o segundo inteiro a quantidade de 
nanosegundos desde o início do segundo atual (armazenado no primeiro inteiro).
INT 2 bytes - Tamanho da mensagem
String latin1 Mensagem – Deve ser menor que 2^14 bytes
hash MD5 16 bytes - calculador sobre os 4campos antreriores
Cliente:
Envia mensagem ao cliente
Checa md5 do ACK recebido
Se sucesso:
    confirma recebimento e encerra thread

''' 
n_sent_logs = 0
n_failed_md5_logs = 0
n_distinct_logs = 0
num_ret = 0
lock = threading.Lock()

def create_md5(package):
    m = hashlib.md5()
    m.update(package)
    return m.digest()

def valid_md5(md5, test_md5):
    return test_md5 == md5

def checkUnreceivedACK(received):
    for index in range(len(received)):
        if(received[index] == 0): 
            return index
    return -1

def createPackage(seqnum, message, Perror):

    seqnum = (seqnum).to_bytes(8, byteorder = 'big')
    sec,nsec = str(time.time()).split('.')

    sec = int(sec)
    nsec = int(nsec)

    sec = (sec).to_bytes(8, byteorder = 'big')
    nsec = (nsec).to_bytes(4, byteorder = 'big')
    sz = (len(message)).to_bytes(2, byteorder = 'big')
    new_message = message
    if(random.random() <= Perror):
        hashed_md5 = (1231231231231231).to_bytes(16, byteorder = 'big')
    else:
        hashed_md5 = create_md5(seqnum + sec + nsec + sz + message.encode('latin1'))

    package = seqnum + sec + nsec + sz + message.encode('latin1') + hashed_md5
    
    return package

def sendPackage(udp, dest, messages, p, received, Perror, Tout):
    try:
        global n_sent_logs
        global n_failed_md5_logs
        global num_ret

        package = createPackage(p + 1, messages[p], Perror)
        udp.sendto(package, dest)

        lock.acquire()
        n_sent_logs = n_sent_logs + 1
        lock.release()
        
        while(received[p] == 0):
            #Recebimento de resposta do servidor(ACK)
            response, address = udp.recvfrom(36)    
            res_seqnum = int.from_bytes(response[:8], byteorder='big')
            res_sec = int.from_bytes(response[8:16], byteorder='big')
            res_nsec = int.from_bytes(response[16:20], byteorder='big') 
            server_md5 = response[20:36]
            sz = int.from_bytes(package[20:22], byteorder='big')
            msg_end = sz + 22
            msg_decoded = (package[22:msg_end]).decode('latin1')

            # Cria md5 para conferir com o recebido
            test_ack_md5 = create_md5(response[:8] + response[8:16] + response[16:20])

            seqnum_response = res_seqnum - 1

            if(valid_md5(test_ack_md5, server_md5)):
                lock.acquire()
                received[seqnum_response] = 1
                lock.release()
            else:
                time.sleep(int(Tout))
                package = createPackage(p + 1, messages[p], Perror)

                udp.sendto(package, dest)
                print("Retransmitindo mensagem #{}".format(p + 1))
                num_ret = num_ret + 1

                lock.acquire()
                n_sent_logs = n_sent_logs + 1
                n_failed_md5_logs = n_failed_md5_logs + 1
                lock.release()
                

    except Exception as e:
        if(received[p] == 0):
            num_ret = num_ret + 1
            n_failed_md5_logs = n_failed_md5_logs + 1
            print("Retransmitindo mensagem #{}".format(p + 1))
            sendPackage(udp, dest, messages, p, received, Perror, Tout)

def returnTuple(dest):
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
    
    #Parametros
    param = sys.argv[1:] 
    filename = param[0]
    dest = param[1]
    HOST, PORT = returnTuple(dest)
    Wtx = param[2]
    Tout = param[3]
    Perror = float(param[4])

    #Escreve na tela
    print("Conectando com: " + dest)
    print("Tamanho da Janela: " + Wtx)
    print("Probabilidade de erro: " + str(Perror))

    # Tamanho da janela
    SWS = int(Wtx)

    global n_sent_logs
    global n_failed_md5_logs
    global n_distinct_logs
    global num_ret
    
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    udp.settimeout(int(Tout))
    dest = (HOST, int(PORT))
    
    file = open(filename,"r", encoding = "latin1")
    lines = file.read().split('\n')
    n_distinct_logs = len(lines)
    threads = [None] * len(lines)
    received = np.zeros(len(lines))
    message = 0

    for p in range(len(threads)):
        threads[p] = threading.Thread(target=sendPackage, args=(udp,dest,lines,p,received,Perror,Tout))

        if(threading.active_count() > SWS):
            while(received[message] == 0):
                pass
            #Seleciona a nova mensagem sem ack a ser checada
            message = checkUnreceivedACK(received)
        
        threads[p] = threads[p].start()

    # A execucao termina quando todas as mensagens sao enviadas e tem seu recebimento confirmado
    while(checkUnreceivedACK(received) != -1):
        pass
                
    udp.close()

    print(str(n_distinct_logs) + " " + str(n_sent_logs) + " " + str(n_failed_md5_logs) + " %.3f"%(time.time()-t_start))
    print("Retransmissoes: " + str(num_ret))

if __name__ == "__main__":
    main()
    print ("Termino da execucao")
