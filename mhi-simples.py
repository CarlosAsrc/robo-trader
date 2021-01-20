from iqoptionapi.stable_api import IQ_Option
import time, json
from datetime import datetime
from dateutil import tz

API = IQ_Option("email", "senha")
check, reason=API.connect()
print(check, reason)
API.change_balance('PRACTICE')

while True:
    if API.check_connect()==False:
        print("Erro ao conectar")
        API.connect() 
    else:
        print("Conectado com sucesso")
        break
    time.sleep(1)
            

def perfil(): # Função para capturar informações do perfil
	perfil = json.loads(json.dumps(API.get_profile_ansyc()))
	
	return perfil
	
	'''
		name
		first_name
		last_name
		email
		city
		nickname
		currency
		currency_char 
		address
		created
		postal_index
		gender
		birthdate
		balance		
	'''


def timestamp_converter(x): # Função para converter timestamp
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]




par = input(' Indique uma paridade para operar: ')
valor_entrada = float(input(' Indique um valor para entrar: '))

while True:
	minutos = float(((datetime.now()).strftime('%M.%S'))[2:])
	entrar = True if (minutos >= 0.58 and minutos <= 0.59) or minutos == 0.00 else False
	print('Hora de entrar?',entrar,'/ Minutos:',minutos)
	
	if entrar:
		print('\n\nIniciando operação!')
		dir = False
		print('Verificando cores..', end='')
		velas = API.get_candles(par, 60, 3, time.time())
		
		velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
		velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
		velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
		
		cores = velas[0] + ' ' + velas[1] + ' ' + velas[2]		
		print(cores)
	
		if cores.count('g') > cores.count('r') and cores.count('d') == 0 : dir = 'put'
		if cores.count('r') > cores.count('g') and cores.count('d') == 0 : dir = 'call'
		
		
		if dir:
			print('Direção:',dir)
			
			status,id = API.buy_digital_spot(par, valor_entrada, dir, 1)
			
			if status:
				while True:
					status,valor = API.check_win_digital_v2(id)
					
					if status:
						print('Resultado operação: ', end='')
						print('WIN /' if valor > 0 else 'LOSS /' , round(valor, 2))
						break					
			else:
				print('\nERRO AO REALIZAR OPERAÇÃO\n\n')
				
	time.sleep(0.5)