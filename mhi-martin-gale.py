from iqoptionapi.stable_api import IQ_Option
import time, json, sys
from datetime import datetime
from dateutil import tz

API = IQ_Option("email", "senha")
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

par = 'AUDJPY'
valor_entrada = 5.0
valor_entrada_b = valor_entrada
martingale = 5
martingale += 1
stop_loss = 300
stop_gain = 300


f = open("./RESULTADOS/mhi-martin-gale." + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".txt", "w")


lucro = 0
payout = Payout(par)

while True:
	segundos = float(((datetime.now()).strftime('%M.%S'))[2:])
	entrar = True if (segundos >= 0.58 and segundos <= 0.59) or segundos <= 0.02 else False
	# print('Hora de entrar?',entrar,'/ segundos:',segundos)
	
	if entrar:
		print('\n\nIniciando operação!')
		f.write('\n\nIniciando operação!')
		dir = False
		print('Verificando cores..', end='')
		f.write('\nVerificando cores..')
		velas = API.get_candles(par, 60, 5, time.time())
		
		velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
		velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
		velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
		velas[3] = 'g' if velas[3]['open'] < velas[3]['close'] else 'r' if velas[3]['open'] > velas[3]['close'] else 'd'
		velas[4] = 'g' if velas[4]['open'] < velas[4]['close'] else 'r' if velas[4]['open'] > velas[4]['close'] else 'd'
		
		cores = velas[0] + ' ' + velas[1] + ' ' + velas[2] + ' ' + velas[3] + ' ' + velas[4]
		print(cores)
		f.write(cores)
		f.flush()

		if cores.count('g') > cores.count('r') : dir = 'put'
		if cores.count('r') > cores.count('g') : dir = 'call'
		
		
		if dir:
			print('Direção:',dir)
			f.write('\nDireção: ' + dir)

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
							print('WIN /' if valor > 0 else 'LOSS /' , round(valor, 2) ,'/', round(lucro, 2),('/ '+str(i)+ ' GALE' if i > 0 else '' ))
							valor_entrada = Martingale(valor_entrada, payout)
							print('LUCRO: ', round(lucro, 2))
							
							f.write('\nResultado operação: ')
							f.write('WIN '+str(round(valor, 2)) if valor > 0 else 'LOSS '+str(round(valor, 2)))
							f.flush()
							stop(lucro, stop_gain, stop_loss)


							break
								
					if valor > 0 : break

				else:
					print('\nERRO AO REALIZAR OPERAÇÃO\n\n')
				
	time.sleep(0.5)