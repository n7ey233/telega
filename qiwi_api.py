import requests
import json
from time import time as seedfortime


'''
233

'''
#get+ проверка на блокировку аккаунта
def check_qiwi_blocked(qiwi_token):
    url = 'https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=false&userInfoEnabled=false'
    qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
    r = requests.get(url, headers=qiwi_headers)
    transaction_json = json.loads(r.text)
    status = transaction_json['contractInfo']['blocked']
    return status #returns bool(False) if not blocked
#get+ баланс
def get_qiwi_balance(qiwi_num, qiwi_token, currency='qw_wallet_rub'):
    #currency = 'qw_wallet_rub' ## рубль
    url = 'https://edge.qiwi.com/funding-sources/v2/persons/'+qiwi_num+'/accounts'
    qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
    r = requests.get(url, headers=qiwi_headers)
    transaction_json = json.loads(r.text)
    iter_x = 0
    while iter_x != True:
        try:
            transaction_json['accounts'][iter_x]['alias']
        except:
            #catch index error
            return None
        if transaction_json['accounts'][iter_x]['alias'] != currency:
            iter_x+=1
        else:
            #if everything is success then return float сумму на балансе
            return transaction_json['accounts'][iter_x]['balance']['amount']
#get+ check if transaction exists, if exists, return True, float(num)
def check_qiwi_transaction(qiwi_num, qiwi_token, transaction_id):
    try:
        url = 'https://edge.qiwi.com/payment-history/v2/transactions/'+transaction_id+'?type=IN'
        qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
        r = requests.get(url, headers=qiwi_headers)
        transaction_json = json.loads(r.text)
        if str(transaction_json["personId"])==qiwi_num and transaction_json["status"] == 'SUCCESS' and transaction_json["total"]["currency"] == 643:
            return str(transaction_json["total"]["amount"])
        else:
            return None 
    except:
    ##payment does'nt exists ili ne prenadlejit etomu qiwi ili chtoto drugoe, mb server upal, mb qiwi upal, yaneebu
        return None
#post+ Перевод qiwi+ перевод карта??
def send_transaction(qiwi_token, send_to, amount, comment=None):
    transaction_id = int(seedfortime()*1000)
    #qiwi
    url = 'https://edge.qiwi.com/sinap/api/v2/terms/99/payments'
    qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
    data = dict()
    data['id'] = str(transaction_id)
    data['sum'] = {'amount': amount,"currency":"643"}
    data["paymentMethod"] = {"type":"Account","accountId":"643"}
    data["fields"] = {"account":'+'+str(send_to)}
    if comment: data["comment"] = comment
    r = requests.post(url, headers=qiwi_headers, json=data)
    print(r.text)
    if int(json.loads(r.text)['id']) != int(transaction_id): send_transaction(qiwi_token, send_to, amount, 'recursion')

#Идентификация пользователя
def qiwi_identification():
    None
#undone functions
def get_qiwi_rates(qiwi_num, qiwi_token, currency):
    currency = 99 # 99 - qiwi, 1963 - sber
    url = 'https://edge.qiwi.com/sinap/providers/'+str(currency)+'/form'
    qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
    r = requests.get(url, headers=qiwi_headers)
    transaction_json = json.loads(r.text)
#test
qiwi_token = 'd40d1855b9ea2d1699b018d943455e65'
qiwi_wallet_num = '79242542786'
def test_check_qiwi_block():
    a = check_qiwi_blocked(qiwi_token)
    return a
def test_get_qiwi_balance():
    a = get_qiwi_balance(qiwi_wallet_num, qiwi_token, 'qw_wallet_rub')
    return a
def test_check_qiwi_transaction():
    transaction_id = '14413812252'
    zx = check_qiwi_transaction(qiwi_wallet_num, qiwi_token, transaction_id)
    return float(zx)
def test_send_qiwi_transaction():
    amount = 1.50
    send_to = '79247283606'
    send_transaction(qiwi_token, send_to, amount)
def run_tests():
    test_check_qiwi_block()
    test_get_qiwi_balance()
    test_send_qiwi_transaction()

test_send_qiwi_transaction()