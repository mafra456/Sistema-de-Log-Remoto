## Sliding Window Draft

# Força md5 válido para motivos de testes
def valid_md5():
	return True


# Função dummy para motivos de testes
def send_ACK(seqnum):
	print("ACK #{} enviado".format(seqnum))



# Receptor Window Size (Tamanho da janela)
RWS = 1

# Next Frame Expected (Primeiro quadro da janela)
NFE = 0

# Last Frame Acceptable (Último quadro da janela)
LFA = NFE + RWS - 1

# Janela
SW = [""] * RWS


# Representa o recebimento de uma mensagem e sua validação
def receive_message(seqnum, message):
	global RWS
	global NFE
	global SW
	global LFA
	print("")
	print("Mensagem #{} recebida no servidor: {}".format(seqnum, message))
	print("RWS: {} NFE: {} LFA: {} SW: {}".format(RWS, NFE, LFA, SW))
	# A mensagem só é relevante para nós se seu seqnum está dentro da janela e seu md5 é válido. Caso contrário, ela é descartada.
	if(valid_md5() and (seqnum >= NFE and seqnum <= LFA)):
		
		# Adicionamos a mensagem na janela
		SW[seqnum] = message
		print("Mensagem #{} adicionada à janela.".format(seqnum))

		# Se o NFE agora tem uma mensagme, andamos com a janela.
		while(SW[NFE] != ""):
			NFE = NFE + 1
			LFA = LFA + 1
			SW.append("")
			print_to_output_file(file, message)
			print("Janela movida: {} – {} -> {} – {}".format(NFE-1, LFA-1, NFE, LFA))

		# Printa nova janela
		print("RWS: {} NFE: {} LFA: {} SW: {}".format(RWS, NFE, LFA, SW))

		# Enviamos o ACK para o cliente
		send_ACK(seqnum)

		# Retornamos True para indicar que a mensagem foi válida (md5 correto e permitida na range da janela)
		return True

	# Retornamos False se a mensagem foi descartada
	return False




# Clara inabilidade do programador em printar newlines
print("")
print("")
print("")


## Imita o cliente mandando as mensagens

messages = ["Log #0", "Log #1", "Log #2", "Log #3", "Log #4"]


# Iteramos no array de mensagens simulando o envio do cliente. O seqnum é o índice da mensagem no array
#for seqnum, message in enumerate(messages):
	#receive_message(seqnum, message)

receive_message(2, messages[2])
receive_message(1, messages[1])
receive_message(0, messages[0])
receive_message(4, messages[4])



print("")
print("Sliding Window: {}".format(SW))