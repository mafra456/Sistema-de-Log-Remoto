''' 

INT 8 bytes – Número de sequencia
começa em 0 e incrementa
INT 8 bytes & INT 4 byets Timestamp 
o primeiro inteiro representa a quantidade de segundos desde a data de referência do período corrente, e o segundo inteiro a quantidade de nanosegundos desde o início do segundo atual (armazenado no primeiro inteiro).


INT 2 bytes - Tamanho da mensagem

String latin1 Mensagem – Deve ser menor que 2^14 bytes
hash MD5 16 bytes - calculador sobre os 4campos antreriores



Servidor:

Recebe mensagem do cliente

Checa md5

Se sucesso:
	Envia ack
	Escreve ultima mensagem da janela no arquivo

''' 

# python3 servidor.py output.txt 5000 5 0.85
import random
import socket
import hashlib
import sys
import threading
import pdb


def create_md5(package):
	print("Package: {}".format(package))
	#pdb.set_trace()
	checksum = hashlib.md5()
	checksum.update(package)
	return checksum.digest()


def valid_md5(md5, test_md5):
	return test_md5 == md5

# Função dummy para motivos de testes
def send_ACK(seqnum):
	print("ACK #{} enviado".format(seqnum))

def print_to_output_file(message):
	global f
	#print("Printing {} to file {}".format(message, sys.argv[1]))
	f.write(message + '\n')

# Representa o recebimento de uma mensagem e sua validação
def receive_message(client_key, seqnum, message, md5, test_md5):
	global RWS
	global sliding_windows
	#print("Mensagem #{} recebida no servidor: {}".format(seqnum, message))
	#print("RWS: {} NFE: {} LFA: {} SW: {}".format(RWS, NFE, LFA, SW))
	# A mensagem só é relevante para nós se seu seqnum está dentro da janela e seu md5 é válido. Caso contrário, ela é descartada.
	#if(valid_md5(message, md5) and (seqnum >= NFE and seqnum <= LFA)):

	# Cria md5 para conferir com o recebido
	#checksum = create_md5(seqnum + sec + nsec + sz + message)
	#pdb.set_trace()

	if(valid_md5(md5, test_md5) and (seqnum <= sliding_windows[client_key]['LFA'])):
		# Se a mensagem já foi ack, simplesmente retornamos True pra reenviar o ACK
		if(seqnum < sliding_windows[client_key]['NFE']):
			print("Mensagem {} já foi ACK".format(seqnum))
			return True

		# Adicionamos a mensagem na janela
		sliding_windows[client_key]['SW'][seqnum] = message
		print("\nMensagem #{} adicionada à janela.".format(seqnum))

		# Se o NFE agora tem uma mensagem, andamos com a janela.
		while(sliding_windows[client_key]['SW'][sliding_windows[client_key]['NFE']] != ""):
			print_to_output_file(sliding_windows[client_key]['SW'][sliding_windows[client_key]['NFE']])
			sliding_windows[client_key]['NFE'] = sliding_windows[client_key]['NFE'] + 1
			sliding_windows[client_key]['LFA'] = sliding_windows[client_key]['LFA'] + 1
			sliding_windows[client_key]['SW'].append("")
			print("\nEscrevendo {} no arquivo -- Janela movida: {} – {} -> {} – {}".format(sliding_windows[client_key]['SW'][sliding_windows[client_key]['NFE']-1], sliding_windows[client_key]['NFE']-1, sliding_windows[client_key]['LFA']-1, sliding_windows[client_key]['NFE'], sliding_windows[client_key]['LFA']))

		# Printa nova janela
		print("\nNFE: {} LFA: {} SW: {}".format(sliding_windows[client_key]['NFE'], sliding_windows[client_key]['LFA'], sliding_windows[client_key]['SW']))

		# Retornamos True para indicar que a mensagem foi válida (md5 correto e permitida na range da janela)
		return True

	# Retornamos False se a mensagem foi descartada
	if(valid_md5(md5, test_md5) == False):
		print("ERRO: MD5 inválido.")
	if(seqnum > sliding_windows[client_key]['LFA']):
		print("ERRO: SeqNum ({}) > LFA({})".format(seqnum, sliding_windows[client_key]['LFA']))
	return False


def client_worker(client_socket, request):
	global Perror

	client_key = str(client_socket[0]) + ":" + str(client_socket[1])


	#print("\n\nrequest CRUA recebida: {}".format(request))
	seqnum = int.from_bytes(request[:8], byteorder='big')
	sec = int.from_bytes(request[8:16], byteorder='big')
	nsec = int.from_bytes(request[16:20], byteorder='big')
	sz = int.from_bytes(request[20:22], byteorder='big')
	message = (request[22:22+sz]).decode('latin1')
	md5 = (request[(22+sz):22+sz+16])#.decode('latin1')




	# Cria md5 para conferir com o recebido
	test_md5 = create_md5(request[:8] + request[8:16] + request[16:20] + request[20:22] + request[22:22+sz])



	#print("Request recebida @{}:\n seqnum: {} \n sec: {} \n nsec: {} \n sz: {} \n message: {} \n md5: {} ".format(client_socket, seqnum, sec, nsec, sz, message, md5))
	# Se a mensagem foi recebida com sucesso, enviamos a confirmação
	if(receive_message(client_key, seqnum, message, md5, test_md5) == True):
		int_seqnum = seqnum
		seqnum = (seqnum).to_bytes(8, byteorder = 'big')
		sec = (sec).to_bytes(8, byteorder = 'big')
		nsec = (nsec).to_bytes(4, byteorder = 'big')
		
		


		#udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
		#udp.connect(("127.0.0.1", 5000))
		

		#print("seqnum bytes: {}".format(seqnum))

		
		# Aqui forcamos um erro baseado em probabilidade. Caso o md5 deva ser enviado errado, simplesmente tiramos o md5 do md5 
		if(random.random() <= Perror):
			ack_md5 = (1231231231231231).to_bytes(16, byteorder = 'big')
			print("Forçou um erro no MD5: {}".format(ack_md5))
		else:
			ack_md5 = create_md5(seqnum + sec + nsec)

		# Criamos o pacote concatenando os bytes e convertendo as duas string p bytes
		package = seqnum + sec + nsec + ack_md5
		#print("Package a ser enviado p cliente: {}".format(package))
		print("ACK #{} enviado para cliente".format(int_seqnum))
		server_socket.sendto(package, client_socket)




output, port, Wrx, Perror = sys.argv[1:]
print(sys.argv)

# Parses
port = int(port)
Wrx = int(Wrx)
Perror = float(Perror)
f = open(output,'w')

# Receptor Window Size (Tamanho da janela)
RWS = Wrx

# Next Frame Expected (Primeiro quadro da janela)
NFE = 1

# Last Frame Acceptable (Último quadro da janela)
LFA = NFE + RWS - 1

# Janela – Adicionamos +1 pois o indice começa em 1, e nao em 0
SW = [""] * (RWS + 1)

sliding_windows = dict()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', port))
client_list = []


# Aceita conexões c/ Threads
while True:
	request, client_socket = server_socket.recvfrom(16422)
	
	# Criamos o dicionario de dicionarios. A chave principal é a chave que identifica o cliente <host:port>
	# e o dicionario interno contem a janela, o LFA e o NFE
	client_key = str(client_socket[0]) + ":" + str(client_socket[1])
	if client_key not in sliding_windows:
		inner_dict = dict()
		inner_dict['SW'] = SW
		inner_dict['LFA'] = LFA
		inner_dict['NFE'] = NFE
		sliding_windows[client_key] = inner_dict

	t = threading.Thread(target=client_worker, args=(client_socket, request, ))
	client_list.append(t)
	t.start()
	


# server_socket.sendto(message, address)














