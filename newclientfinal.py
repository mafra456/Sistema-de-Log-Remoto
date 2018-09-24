import 	threading
import socket
import sys
import os
import struct
import time
import hashlib
import random
import numpy as np
import threading

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
	checksum = hashlib.md5()
	checksum.update(package)
	return checksum.digest()

def valid_md5(message, md5):
    return create_md5(message) == md5

def checkUnreceivedACK(received):
	for index in range(len(received)):
		if(received[index] == 0): 
			return index
	return -1

def createPackage(seqnum, message,md5_incorrect):

	seqnum = (seqnum).to_bytes(8, byteorder = 'big')
	sec,nsec = str(time.time()).split('.')

	sec = int(sec)
	nsec = int(nsec)

	sec = (sec).to_bytes(8, byteorder = 'big')
	nsec = (nsec).to_bytes(4, byteorder = 'big')
	sz = (len(message)).to_bytes(2, byteorder = 'big')
	if(md5_incorrect == 1):
		message = ''.join(random.sample(message,len(message)))
	hashed_md5 = create_md5(seqnum + sec + nsec + sz + message.encode('ascii'))
	package = seqnum + sec + nsec + sz + message.encode('ascii') + hashed_md5
    
	return package

def sendPackage(udp, dest, messages, p, received, Perror, Tout):
	try:
		md5_incorrect = 0
		global n_sent_logs
		global n_failed_md5_logs
		global num_ret
		if(random.random() < Perror):
			md5_incorrect = 1
		package = createPackage(p + 1, messages[p], md5_incorrect)
		udp.connect(dest)
		udp.send(package)

		lock.acquire()
		n_sent_logs = n_sent_logs + 1
		lock.release()

		while(received[p] == 0):
			#Recebimento de resposta do servidor (ACK)
			response, address = udp.recvfrom(36)	
			res_seqnum = int.from_bytes(response[:8], byteorder='big')
			res_sec = int.from_bytes(response[8:16], byteorder='big')
			res_nsec = int.from_bytes(response[16:20], byteorder='big')	
			server_md5 = response[20:36]
			sz = int.from_bytes(package[20:22], byteorder='big')
			msg_end = sz + 22
			msg_decoded = (package[22:msg_end]).decode('latin1')

			if(valid_md5(msg_decoded, server_md5)):
				lock.acquire()
				received[res_seqnum] = 1
				lock.release()
			else:
				time.sleep(Tout)
				package = createPackage(p + 1, messages[p], md5_incorrect)

				udp.connect(dest)
				udp.send(package)

				lock.acquire()
				n_sent_logs = n_sent_logs + 1
				n_failed_md5_logs = n_failed_md5_logs + 1
				lock.release()
				

	except Exception as e:
		print(e)
		if(received[p] == 0):
			print("Retransmitindo")
			num_ret = num_ret + 1
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
	
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	udp.settimeout(int(Tout))
	dest = (HOST, PORT)
	
	file = open(filename,"r")
	lines = file.read().split('\n')
	n_distinct_logs = len(lines)
	threads = [None] * len(lines)
	received = np.zeros(len(lines))
	message = checkUnreceivedACK(received)

	for p in range(len(threads)):
		threads[p] = threading.Thread(target=sendPackage, args=(udp,dest,lines,p,received,Perror,Tout))

		if(threading.active_count() > SWS):
			while(received[message] == 0):
				pass
			message = checkUnreceivedACK(received)
		
		threads[p] = threads[p].start()

	# O cliente para quando todos as mensagens sao enviadas
	while(checkUnreceivedACK(received) != -1):
		pass
				
	udp.close()

	print(str(n_distinct_logs) + " " + str(n_sent_logs) + " " + str(n_failed_md5_logs) + " %.3f"%(time.time()-t_start))
	print("Retransmissoes: " + str(num_ret))

if __name__ == "__main__":
    main()
    print ("Termino da execucao")