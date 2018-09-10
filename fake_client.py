# Simula envio inicial de msg p servidro


import random
import socket
import hashlib
import time
import math

def bytes_size(value):
	math.ceil(value.bit_length()/8)

def create_md5(message):
	return hashlib.md5(message.encode('ascii')).digest()



# Cliente fake message
message = "pip bla bla 123 123 lorem ipsum"

seqnum = (9).to_bytes(8, byteorder = 'big')
sec,nsec = str(time.time()).split('.')

sec = int(sec)
nsec = int(nsec)

sec = (sec).to_bytes(8, byteorder = 'big')
nsec = (nsec).to_bytes(4, byteorder = 'big')
sz = (len(message)).to_bytes(2, byteorder = 'big')
hashed_md5 = create_md5(message)


socket.setdefaulttimeout(15)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
udp.connect(("127.0.0.1", 5000))
print('Conectado! Para sair, use CTRL+X\n')

# Crio o pacote concatenando os bytes e convertendo as duas string p bytes
package = seqnum + sec + nsec + sz + message.encode('ascii') + hashed_md5
# Não dou encode na hora de enviar porque package já são bytes
udp.send(package)


#message_bytes = (message).to_bytes(sz, byteorder = 'big')
print("Mensagem enviada: \n:")
print("sec: {} size: {}".format(sec, len(sec)))
print("nsec: {} size: {}".format(nsec, len(nsec)))
print("sz: {} size: {}".format(sz, len(sz)))
print("message: {} size: {}".format(message, len(message)))
print("hashed_md5: {} size: {}\n".format(hashed_md5, len(hashed_md5)))
print("–––––––––––––––––––––––––––––––––––")
#print("message_bytes: {}".format(message_bytes))

response, address = udp.recvfrom(36)

seqnum = int.from_bytes(response[:8], byteorder='big')
sec = int.from_bytes(response[8:16], byteorder='big')
nsec = int.from_bytes(response[16:20], byteorder='big')
md5 = (response[20:36])#.decode('ascii')


print("ACK #{} recebido".format(seqnum))

