import requests
import json
#отправка сообщения
def sendMessage(telegram_token, chat_id, content):
    url = "https://api.telegram.org/bot"+telegram_token+"/sendMessage"
    data = {'chat_id': chat_id, 'text': content}
    requests.get(url,headers={'Content-Type': 'application/json' }, json=data)
#set webhook
def set_webhook(telegram_token, pk):
    url = 'https://api.telegram.org/bot'+telegram_token+'/setWebhook?url=https://telegan7e.pythonanywhere.com/j128302dwiq0ej833fcu8iaqhj8c932?q='+str(pk)
    r = requests.get(url)
    if True: #check if so
    #\\prodoljai s dopisivaniya views telegram api potom model' proekta i tut
        try:json.loads(r.text)['result']
        except:None
    if json.loads(r.text)['result'] != True: set_webhook(telegram_token, pk)
    return True

#ответ на callbackquery
def answerCallbackQuery(telegram_token, callback_query_id):
    requests.get("https://api.telegram.org/bot"+telegram_token+"/answerCallbackQuery?callback_query_id="+str(callback_query_id))

def get_tg(telegram_token, method):
    return json.loads(requests.get("https://api.telegram.org/bot"+telegram_token+"/getme").text)['result'][method]
def form_inline_button(name, data):

    return [{'text': name, 'callback_data': data}]
#formiruyet dict knopok dlya otveta iz spiska @a
def reply_markup(a):

    return {'inline_keyboard': a}

if True:
    #sendMessage('700264978:AAG6PdQSBamU5nREeT8c07fUzoz5EzNp6Pg', 405347178, 'qqqq255522552551142555452451 \n wwww')
    #set_webhook('571432396:AAEDgR-eAxfqnuNw6_aSDtEhcJGImxnzXwM', 1)
    None