from iqoptionapi.stable_api import IQ_Option
import time
import json
import sys
import config
from datetime import datetime
from trade_config import *
from dateutil import tz

API = IQ_Option(config.email, config.senha)
check, reason = API.connect()
print(check, reason)
API.change_balance('PRACTICE')


def timestamp_converter(x):  # Função para converter timestamp
    hora = datetime.strptime(datetime.utcfromtimestamp(
        x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
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
    cores = ''
    dir = False
    velas = API.get_candles(par, 60, 3, time.time())

    for x in range(len(velas)):
        velas[x] = 'g' if velas[x]['open'] < velas[x]['close'] else 'r' if velas[x]['open'] > velas[x]['close'] else 'd'
        cores = cores + velas[x]
        print(cores)

    print('Verificando candles..', end='')
    print(cores)

    # MHI sequencial:
    if cores.count('g') == sequencial_velas_minimas:
        dir = 'put'
    if cores.count('r') == sequencial_velas_minimas:
        dir = 'call'

    return dir


while True:
    if API.check_connect() == False:
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
            print('Direção:', dir)
            # f.write('\nDireção: ' + dir)

            valor_entrada = valor_entrada_b

            for i in range(martingale):
                status, id = API.buy_digital_spot(par, valor_entrada, dir, 1)

                if status:
                    while True:
                        status, valor = API.check_win_digital_v2(id)

                        if status:
                            valor = valor if valor > 0 else float(
                                '-' + str(abs(valor_entrada)))
                            lucro += round(valor, 2)

                            print('Resultado operação: ', end='')
                            print('WIN /' if valor > 0 else 'LOSS /', round(valor,
                                                                            2), ('/ '+str(i) + ' GALE' if i > 0 else ''))
                            if (i < gale_limite):
                                valor_entrada = Martingale(
                                    valor_entrada, payout)
                            print('LUCRO TOTAL: ', round(lucro, 2))

                            # f.write('\nResultado operação: ')
                            # f.write('WIN '+str(round(valor, 2)) if valor > 0 else 'LOSS '+str(round(valor, 2)))
                            # f.flush()
                            stop(lucro, stop_gain, stop_loss)

                            break

                    if valor > 0:
                        break

                else:
                    print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

    time.sleep(0.5)
