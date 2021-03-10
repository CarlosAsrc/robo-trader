from iqoptionapi.stable_api import IQ_Option
import time, json, sys, config
from datetime import datetime
from trade_config import *
from dateutil import tz

API = IQ_Option(config.email, config.senha)
check, reason=API.connect()
print(check, reason)
API.change_balance('PRACTICE')
            

def timestamp_converter(x): # Função para converter timestamp
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]

def stop(lucro, gain, loss):
	if lucro <= float('-' + str(abs(loss))):
		print('Stop Loss batido!')
		sys.exit()
		
	if lucro >= float(abs(gain)):
		print('Stop Gain Batido!')
		sys.exit()

def Martingale(valor, payout):
	lucro_esperado = valor * payout
	perca = float(valor)	
		
	while True:
		if round(valor * payout, 2) > round(abs(perca) + lucro_esperado, 2):
			return round(valor, 2)
			break
		valor += 0.01

def Payout(par):
	API.subscribe_strike_list(par, 1)
	while True:
		d = API.get_digital_current_profit(par, 1)
		if d != False:
			d = round(int(d) / 100, 2)
			break
		time.sleep(1)
	API.unsubscribe_strike_list(par, 1)
	
	return d


def DeveEntrar():
	segundos = float(((datetime.now()).strftime('%M.%S'))[2:])
	return True if (segundos >= 0.58 and segundos <= 0.59) else False
	# return True if (segundos == 0.59) else False

def DirecaoOrdem():
	dir = False
	velas = API.get_candles(par, 60, 9, time.time())
	

	velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
	velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
	velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
	velas[3] = 'g' if velas[3]['open'] < velas[3]['close'] else 'r' if velas[3]['open'] > velas[3]['close'] else 'd'
	velas[4] = 'g' if velas[4]['open'] < velas[4]['close'] else 'r' if velas[4]['open'] > velas[4]['close'] else 'd'
	velas[5] = 'g' if velas[5]['open'] < velas[5]['close'] else 'r' if velas[5]['open'] > velas[5]['close'] else 'd'
	velas[6] = 'g' if velas[6]['open'] < velas[6]['close'] else 'r' if velas[6]['open'] > velas[6]['close'] else 'd'
	velas[7] = 'g' if velas[7]['open'] < velas[7]['close'] else 'r' if velas[7]['open'] > velas[7]['close'] else 'd'
	velas[8] = 'g' if velas[8]['open'] < velas[8]['close'] else 'r' if velas[8]['open'] > velas[8]['close'] else 'd'
	# velas[9] = 'g' if velas[9]['open'] < velas[9]['close'] else 'r' if velas[9]['open'] > velas[9]['close'] else 'd'

	
	# MHI CONSIDERANDO 5 VELAS:
	# cores = velas[0] + ' ' + velas[1] + ' ' + velas[2] + ' ' + velas[3] + ' ' + velas[4]		
	# if cores.count('g') > cores.count('r') : dir = 'put'
	# if cores.count('r') > cores.count('g') : dir = 'call'
	
	# APÓS SEQUENCIAL DE 8 VELAS:
	cores = velas[0] + ' ' + velas[1] + ' ' + velas[2] + ' ' + velas[3] + ' ' + velas[4] + ' ' + velas[5] + ' ' + velas[6] + ' ' + velas[7] + ' ' + velas[8]

	# print('Verificando candles..', end='')
	# f.write('\nVerificando candles..')
	# print(cores)
	# f.write(cores)
	# f.flush()

	if cores.count('g') == sequencial_velas_minimas : dir = 'put'
	if cores.count('r') == sequencial_velas_minimas : dir = 'call'
	
	return dir



while True:
    if API.check_connect()==False:
        print("Erro ao conectar")
        API.connect() 
    else:
        print("Conectado com sucesso")
        break
    time.sleep(1)

# par = input(' Indique uma paridade para operar: ').upper()
# valor_entrada = float(input(' Indique um valor para entrar: '))
# valor_entrada_b = float(valor_entrada)
# martingale = int(input(' Indique a quantia de martingales: '))
# martingale += 1

# stop_loss = float(input(' Indique o valor de Stop Loss: '))
# stop_gain = float(input(' Indique o valor de Stop Gain: '))


# f = open("./RESULTADOS/mhi-martin-gale." + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".txt", "w")


lucro = 0
payout = Payout(par)

while True:
	entrar = DeveEntrar()
	
	if entrar:
		dir = DirecaoOrdem()
		
		if dir:
			print('\n\nIniciando operação!')
			# f.write('\n\nIniciando operação!')
			print('Direção:',dir)
			# f.write('\nDireção: ' + dir)

			valor_entrada = valor_entrada_b

			for i in range(martingale):
				status,id = API.buy_digital_spot(par, valor_entrada, dir, 1)
				
				if status:
					while True:
						status,valor = API.check_win_digital_v2(id)
						
						if status:
							valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
							lucro += round(valor, 2)

							print('Resultado operação: ', end='')
							print('WIN /' if valor > 0 else 'LOSS /' , round(valor, 2), ('/ '+str(i)+ ' GALE' if i > 0 else '' ))
							if (i < gale_limite):
								valor_entrada = Martingale(valor_entrada, payout)
							print('LUCRO TOTAL: ', round(lucro, 2))
							
							# f.write('\nResultado operação: ')
							# f.write('WIN '+str(round(valor, 2)) if valor > 0 else 'LOSS '+str(round(valor, 2)))
							# f.flush()
							stop(lucro, stop_gain, stop_loss)

							break
								
					if valor > 0 : break

				else:
					print('\nERRO AO REALIZAR OPERAÇÃO\n\n')
				
	time.sleep(0.2)