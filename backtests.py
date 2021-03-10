from iqoptionapi.stable_api import IQ_Option
import time, json, config
from datetime import datetime
from dateutil import tz

API = IQ_Option(config.email, config.senha)
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
            

def DirecaoOrdem():
    cores = ''
    dir = False
    velas = API.get_candles(par, 60, 3, time.time())

    print('PASSOU AQUI VEIO')

    velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
    velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
    velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'

    # ÚLTIMAS 5 VELAS:
    cores = velas[0] + ' ' + velas[1] + ' ' + velas[2]
    # print(cores)

    if cores.count('g') == 3:
        dir = 'put'
    if cores.count('r') == 3:
        dir = 'call'

    return dir



par = 'USDJPY'
cores = ''



end_from_time=time.time()
velas=[]
for i in range(1):
    data=API.get_candles(par, 60, 1000, end_from_time)
    velas =data+velas
    end_from_time=int(data[0]["from"])-1
# print(velas)


# velas = API.get_candles(par, 60, 1000, time.time())


for x in range(len(velas)):
	velas[x] = 'g' if velas[x]['open'] < velas[x]['close'] else 'r' if velas[x]['open'] > velas[x]['close'] else 'd'
	cores = cores + velas[x]


# print(cores)
print('Sequencial de compra: ' + str(cores.count('ggggggggg')))
print('Sequencial de venda:  ' + str(cores.count('rrrrrrrrr')))
print(DirecaoOrdem())
# print(cores.count('d'))
# if cores.count('g') > cores.count('r') and cores.count('d') == 0 : dir = 'put'
# if cores.count('r') > cores.count('g') and cores.count('d') == 0 : dir = 'call'
# if cores.count('g') == 3 : dir = 'put'
# if cores.count('r') == 3 : dir = 'call'