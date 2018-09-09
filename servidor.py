''' 

INT 8 bytes – Número de sequencia
começa em 0 e incrementa
INT 8 bytes & INT 4 byets Timestamp 
o primeiro inteiro representa a quantidade de segundos desde a data de referência do período corrente, e o segundo inteiro a quantidade de nanosegundos desde o início do segundo atual (armazenado no primeiro inteiro).


INT 2 bytes - Tamanho da mensagem

String ASCII Mensagem – Deve ser menor que 2^14 bytes
hash MD5 16 bytes - calculador sobre os 4campos antreriores



Servidor:

Recebe mensagem do cliente

Checa md5

Se sucesso:
	Envia ack
	Escreve ultima mensagem da janela no arquivo

''' 

# python3 servidor.py output.txt 5000 4 0.5
import random
import socket
import hashlib
import sys



def create_md5(message):
	return hashlib.md5(message.encode('ascii')).hexdigest()


def valid_md5(message, md5):
	return create_md5(message) == md5




output, port, Wrx, Perror = sys.argv[1:]
print(sys.argv)

# Parses
port = int(port)
Wrx = int(Wrx)
Perror = float(Perror)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', port))


#UNCOMMENT while True:
# TO DO Recebe conexão do cliente 
#UNCOMMENT message, address = server_socket.recvfrom(1024)


# Decodifica mensagem do cliente
message = "bla bla bla 123 123 lorem ipsum"
seqnum = 1
sec = 1536451863
nsec = 515483
sz = 31
md5 = "677f7c58069d8c3293f9ff8214b15303"

# Checa MD5
if(valid_md5(message, md5)):	
	# Se o MD5 é válido, enviamos ack

	# E depois ashli

# TO DO Envia resposta a cliente
# server_socket.sendto(message, address)














