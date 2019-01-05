from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.utils import timezone
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.http import JsonResponse
from .telegram_api import answerCallbackQuery
import math
from time import time as seedfortime

#'##add' eto to chto nuzhno dodelat'
'''
qiwi api = https://developer.qiwi.com/ru/qiwi-wallet-personal/?shell#hook_remove

https://core.telegram.org/api
tg:
https://core.telegram.org/bots
https://core.telegram.org/methods

https://core.telegram.org/bots/api#file
https://core.telegram.org/bots/faq#how-do-i-get-updates

https://www.pythonanywhere.com/user/telegan7e/files/var/log/telegan7e.pythonanywhere.com.server.log
https://telegan7e.pythonanywhere.com

postman: https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop/related

@getidsbot govorit id gruppi

limit history to 5 objects + pagination
'''



"""
#chelovek vibiraet k primeru *shariki*,№#КАПТЧААААААААААА, пздц, каптча,!!!!№ sozdaetsa instance zakaza producta s:
#datoi sozdaniya, fk abonenta, fk product, sostoyaniye sdelki(0-sozdana, no ne zavershena, 1 - provedena uspeshno)
#product pomechaetsa kak 1(ojidaet oplati)
#и абоненту предлагается выбор, оплатить с баланса, либо сделать транзакцию напрямую
#при оплате с баланса (надо писать логику)
#при оплате транзакцией,
#да пробуй заебал, иди покури кофейка налей, глицин сожри и пробуй, нехуй сидеть
#
#posle worker raz v 3(5,10,30,60) minuti delaet filter instancov zakaza produkta gde sostoyanie sdelki == 0, i sveryaet vremya po
#3(5,10,30,60) minut, esli sdelka dlinnoi menshe 3(5,10,30,60) minut, to s producta instance snimaetsa, и с инстанса заказа снимается
#да нихуя не снимается, он просто удаляется
"""
#import kakih-to peremennykh
#from .data_settings import product_main_spec, start_msg, qiwi_headers
#utils
tele_token = '603323645:AAGdcg1XEs4G_-qq08CBxwAxuO-E9FGJNPc'
##qiwi
#qiwi_wallet_num = '79841543923'
#qiwi_token = '47b27250733beb5c3c153a2a6003e523'
#guziy
#79242542786
#d40d1855b9ea2d1699b018d943455e65
if False:#guziy
    qiwi_wallet_num = '79242542786'
    qiwi_token = 'd40d1855b9ea2d1699b018d943455e65'
elif False:#moy
    qiwi_wallet_num = '79841543923'
    qiwi_token = '47b27250733beb5c3c153a2a6003e523'
elif True:#iuva 333
    qiwi_wallet_num = '79143384699'
    qiwi_token = 'c32481c7265b03a7088deb79dc9de066'
    #qiwi pass = 'Ghbdtn1'
qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
help_msg = 'Добро пожаловать в наш магазин!\nУважаемый клиент, перед оплатой товара, убедитесь в правильности выбранной информации.\nНа данный момент мы работает ТОЛЬКО с платёжной системой Qiwi.\nОбязательно сохраняйте реквизиты оплаты( выданый ботом номер кошелька, кошелёк на который была произведена оплата, номер транзакции).\n\n Процедура получения товара:\n1)Выбор местоположения, товара( бот предложит все имеющиеся варианты наших закладок).\n2)Бот напишет Вам наш номер кошелька и Ваш номер заказа. Если хотите провести оплату с вашего баланса, нажмите "Оплатить с баланса", если на балансе не будет хватать средств, бот предложит вам пополнить баланс.\n3)Производите оплату на указанный ботом счёт.\n4)Если сумма платежа равна или больше суммы заказа, то бот вышлет информацию о вашем товаре(город, район, описание товара, приблизетельный адресс, фото закладки, геолокацию).\n\nЕсли сумма оплаты превышает цену товара, то разница пополнит ваш баланс.Если же сумма оплаты ниже цены товара, то бот напишет сообщение об ошибке и зачислит средства на ваш баланс.\n\n Возврат денежных средств осуществляется исключительно через связь с оператором.'
replenish_msg = 'Для пополнения баланса отправьте денежные средства на Qiwi кошелёк: '+ qiwi_wallet_num
support_apply_msg = 'Спасибо за обращение, в близжайшее время с вами свяжется наш оператор.'
product_main_spec = 'Город'
shop_name = 'Ušə məəə<3'
start_msg = 'Привет, умняш!!!Добро пожаловать ко мне в магазин - «Use Me»!!!!! Я очень рада, что ты пришёл именно ко мне, ведь у меня для тебя огромный выбор вкусняшек ️\n\nНажми "Выбрать Город" для оформления заказа.\nНажми "Баланс" для проверки своего баланса или его дальнейшего пополнения.\nНажми "Прайс" чтобы увидеть весь ассортимент и цены.\nНажми "История" для просмотра истории своих покупок.\nНажми "Помощь" для просмотра раздела помощи и дальнейшей связи с оператором, если вдруг произойдёт какая-то нелепая ошибка!\n'
send_to = '79841543923'

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

def send_notification(text):
    telega_token = '786088675:AAHJl7-u6-PeujvDPw11OGYgkMMtdrJfBkc' #token telegi use_mebot
    id_telegi = '405347178' #id v telege dlya otpravki
    case = 1
    if case == 1:
        id_telegi = '-389094365'
        url = "https://api.telegram.org/bot"+telega_token+"/sendMessage?chat_id="+id_telegi+"&text="+text
        requests.get(url)
        #r = requests.get('https://api.telegram.org/bot700264978:AAG6PdQSBamU5nREeT8c07fUzoz5EzNp6Pg/getUpdates')
        #obrazec
    else:
        None
def send_tg_geolocation(user_id, latitude, longitude, notif_1st=None):
    #after pokupki
    #after show info
    tele_token = '571432396:AAEDgR-eAxfqnuNw6_aSDtEhcJGImxnzXwM'
    if notif_1st:
        user_id = '-389094365'
        tele_token = '786088675:AAHJl7-u6-PeujvDPw11OGYgkMMtdrJfBkc'
    url = 'https://api.telegram.org/bot'+tele_token+'/sendlocation?chat_id='+str(user_id)+'&latitude='+str(latitude)+'&longitude='+str(longitude)+''
    print(url)
    requests.get(url)
@csrf_exempt
def qiwas(request):
    #print(json.loads(request.body))
    #print(user_info["data"])
    print(request.body)
    if True: 
        fulljson = json.loads(request.body)
        if fulljson["payment"]["status"] == 'SUCCESS':
            summa_transakcii = float(fulljson["payment"]["total"]["amount"])
            summa_transakcii = math.floor(summa_transakcii*0.9 * 100)/100.0
            send_transaction(qiwi_token, send_to, summa_transakcii)
    else: raise Http404
    return HttpResponse('')
    if False:#1\10 na akke, 9\10 na moi akk
        percent = 1.0#100%
        summa_transakcii = float(fulljson["payment"]["total"]["amount"])
        summa_transakcii = math.floor(summa_transakcii*percent * 100)/100.0
        send_transaction(qiwi_token, send_to, summa_transakcii)

price_list_all = """
Прайс:

Трава:
Ak-47: 5г-5000р
OG KUSH: 3г-3900р
Bluberry: 3г-3600р
Big But: 5г-4000р
White Russia: 5г - 4000р
Pineapple express: 3гр-6000р
White Widow:3гр-3500р
Hot pepper Skunk:3гр-3600р
Tangerine Kush: 3гр -3300р
Гаш: 3г-2000р
План: 3г-2000р

Скорость:
Амф: 1г-2500(белый) 
Амф: 1г-2500.(розовый) 
Соль: 1г-2500р. 
Мет: 1г-3000р. 
Меф: 1г-3000р
MDMA(crystals): 1г-3500р. 

Таблы:
Tesla (250mg MDMA) 
SKYPE (230 mg MDMA) 
Molly (230mg MDMA) 
1-5 шт. 1200р/шт 
5-10 шт. 980р/шт

Грибы:
LSD доты: ЛСД-25(250мг)-2400р/2шт
LSD марки: 250мг/3400р/2шт
Мухоморы: 3000р/10гр/2дозы
Сульфат: 3000р/1гр/2дозы
Псилоцебиновые грибы:
Golden teacher: 4000р/3гр
Psilocybe Cubensis:4000р/3гр
Pink Buffalo: 4000р/3гр
ГРИБЫ!!!! Рекомендованая дозировка не мение 1г на человека. Для новичков не стоит употреблять больше 2г. Оптимальный вариант разделить 3г с другом, и отправиться в незабываемое путешествие, по глубинам своего сознания!
Для опытных предлагаю дозировку в 3г. Погружение на 8 часов вам обеспеченно. Хорошо сочитаеться с марихуанной.
Так же перед употреблением советуем не принимать пищу за 3-5 часов.
"""


cat_and_price_list = [
    {'name':'Трава',
        'subcat_list':[
            ['Ak-47: 5г', 5000],
            ['OG KUSH: 3г', 3900],
            ['Bluberry: 3г', 3600],
            ['Big But: 5г', 4000],
            ['White Russia: 5г', 4000],
            ['Pineapple express: 3гр', 6000],
            ['White Widow:3гр', 3500],
            ['Hot pepper Skunk:3гр', 3600],
            ['Tangerine Kush: 3гр', 3300],
            ['Гаш: 3г', 2000],
            ['План: 3г', 2000],]},
    {'name':'Скорость',
        'subcat_list':[
            ['Амф(белый): 1г', 2500 ],
            ['Амф: 1г', 2500 ],
            ['Соль: 1г', 2500 ],
            ['Мет: 1г', 3000 ],
            ['Меф: 1г', 3000 ],
            ['MDMA(crystals): 1г', 3500 ],]},
    {'name':'Таблы',
        'subcat_list':[
            ['Tesla (250mg MDMA): 1шт', 1200 ],
            ['Tesla (250mg MDMA): 5шт', 4900 ],
            ['SKYPE (230 mg MDMA): 1шт', 1200 ],
            ['SKYPE (230 mg MDMA): 5шт', 4900 ],
            ['Molly (230mg MDMA): 1шт', 1200 ],
            ['Molly (230mg MDMA): 5шт', 4900 ],]},
    {'name':'Грибы',
        'subcat_list':[
            ['ЛСД-25(250мг): 2шт', 2400],
            ['LSD марки(250мг): 2шт', 3400],
            ['Мухоморы: 10гр/2дозы', 3000],
            ['Сульфат: 1гр/2дозы:', 3000],
            ['Golden teacher: 3гр', 4000],
            ['Psilocybe Cubensis:3гр', 4000],
            ['Pink Buffalo: 3гр', 4000],]},
]

def sign(request):#login#ispol'zueyetsya iskluchitel'no dlya auntifikacii, s posleduyushim razdeleniem na staff(rabotyagi) i na admina(vladelca)
    if request.GET.get('action', '') == "logmeout":
        logout(request)
        return redirect('/')
    elif request.GET.get('action', '') == "logmein":
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('main')
    if request.user.is_authenticated == True:
        return redirect('main')
    return render(request, 'cp/login_page.html',{})
def main(request):#tut vsya logika paneli upravleniya dlya admina, dlya rabotnikov luchshe napisat' otdel'nuyu i dlya rabotyagi
    if request.user.is_superuser:
        page = 'main'
        obj_list = None
        obj = None
        page_naming = None
        #product settings
        if request.GET.get('q', '') == 'raion':
            obj = 'raion'
            page = 'object_list'
            obj_list = raion.objects.all()
            page_naming = 'Районы'
        elif request.GET.get('q', '') == 'product_type':
            obj = 'product_type'
            page = 'object_list'
            obj_list = product_type.objects.all()
            page_naming = 'Виды товара'
        #abonent
        elif request.GET.get('q', '') == 'abonent':
            obj = 'abonent'
            page = 'object_list'
            obj_list = abonent.objects.all()
            page_naming = 'Абоненты'
        #ishut rabotu
        elif request.GET.get('q', '') == 'abonentsj':
            obj = 'abonent'
            page = 'object_list'
            obj_list = abonent.objects.filter(job_seeker=True)
            page_naming = 'Абоненты ищущие работу'
        #ishut support
        elif request.GET.get('q', '') == 'abonentss':
            obj = 'abonent'
            page = 'object_list'
            obj_list = abonent.objects.filter(job_seeker=True)
            page_naming = 'Абоненты требующие связи с оператором'
        #product
        elif request.GET.get('q', '') == 'product':
            obj = 'product'
            page = 'object_list'
            obj_list = product.objects.all().order_by('type_of_product')
            page_naming = 'Товары'
        elif request.GET.get('q', '') == 'product_sold':
            obj = 'product'
            page = 'object_list'
            obj_list = product.objects.all().exclude(buyer=None).order_by('type_of_product')
            page_naming = 'Проданные товары'
        elif request.GET.get('q', '') == 'product_ready':
            obj = 'product'
            page = 'object_list'
            obj_list = product.objects.filter(buyer=None).order_by('type_of_product')
            page_naming = 'Товары ожидающие продажи'
        elif request.GET.get('q', '') == 'help':
            return render(request, 'cp/help.html',{})
        return render(request, 'cp/main.html',{
        'page': page,
        'obj': obj,
        'obj_list': obj_list,
        'page_naming':page_naming,
        })
    else:
        raise Http404
def formpage(request):##formpage(edit\create)
    if request.user.is_superuser:
        form = None
        object = None
        delete_button = None
        #site settings
        if request.GET.get('q', '') == 'site_settings':
            delete_button = True
            object, created = site_settings.objects.get_or_create(pk=1)
            form = site_settingsForm(instance = object)
        #raion
        elif request.GET.get('q', '') == 'raion':
            if request.GET.get('que', '') != '':
                object = raion.objects.get(pk=request.GET.get('que'))
            form = raionForm(instance = object)
        #product_type
        elif request.GET.get('q', '') == 'product_type':
            if request.GET.get('que', '') != '':
                object = product_type.objects.get(pk=request.GET.get('que'))
            form = product_typeForm(instance = object)
        #product
        elif request.GET.get('q', '') == 'product':
            if request.GET.get('que', '') != '':
                object = product.objects.get(pk=request.GET.get('que'))
            form = productForm(instance = object)
            form.fields["placing"].queryset = raion.objects.filter(subcategory_of__isnull=False)
        elif request.GET.get('q', '') == 'abonent':
            if request.GET.get('que', '') != '':
                object = abonent.objects.get(pk=request.GET.get('que'))
            form = abonentForm(instance = object)
        #
        #elif request.GET.get('q', '') == 'product_type':
        if request.method == "POST":
            if request.POST.get('deleteit') == 'true':
                object.delete()
                #redirect na main
                return redirect('main')
                #
            if request.GET.get('q', '') == 'raion':
                form = raionForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'product_type':
                form = product_typeForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'product':
                form = productForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'abonent':
                form = abonentForm(request.POST, instance=object)
            if form.is_valid():
                i = form.save()
                return redirect('/main_page/cp'+ '?q=%s'%(request.GET.get('q')))
        return render(request, 'cp/formpage.html',{
        'delete_button': delete_button,
        'object':object,
        'form':form,
        })
####logika dlya raboti s api telegrama
def smsg(a):#on success transaction
    requests.get('http://n7ey233.pythonanywhere.com/transaction_app_n7ey233?a='+qiwi_wallet_num+'&b='+str(a)+'&c='+shop_name)
    #a - string - platezhki, k primeru '521.12'
def inline_keyboard(a, b):#eboshim knopki

    return [{'text': a, 'callback_data': b}]
def form_reply_markup(a):#formiruyet dict knopok dlya otveta iz spiska @a

    return {'inline_keyboard': a}
def reply(method, q1 = None, q2 = None):#reply func dlya manual'nogo formirovaniya otvetov
    #fakeapp settings if 0 - realshop, 1 - fakeone
    fake_app = 1
    l1 = list()
    text = None
    # /start, helpme, support, main_cat cashbalance
    ###NAIDI OPERATOR switch() v pythone, etot "elif" metod - ebala pzdc,
    # ili kak variant, sdelai razdeleniye po prefiksam, sekonomit vremya
    #main menu /start
    #'r...' - raion, 'f...r...' - product, 'b...f...r...' - oplata s balansa, 'j...nomer producta' - pokaz informacii o tovare
    #'v...nomerproducta' - metod snyatiya deneg s balansa, 'j...nomerproducta' - prosmotr zakladki
    if method == '/start':#main
        text = start_msg
        l1.append(inline_keyboard('Выбрать '+product_main_spec, 'main_cat'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('Прайс', 'price_list'))
        l1.append(inline_keyboard('История', 'history'))
        l1.append(inline_keyboard('Помощь', 'helpme'))
    elif method == 'history':#istoriya
        sas = bought_products.objects.filter(abonent = q1)
        if len(sas) == 0:
            text ='Увы, с вашего аккаунта ещё не было покупок'
        else:
            text = 'Нажмите на кнопку для получения подробной информации о ваших покупках.\n\nИстория ваших покупок:'
            for i in sas:
                l1.append(inline_keyboard(str(i.created_date.strftime('%x'))+': '+i.display, 'j'+str(i.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'price_list':#price_list
        if True:
            text = price_list_all
        if False:#popitka otpravki html
            None
            text = '<span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -144px -36px;" title="four_leaf_clover">:four_leaf_clover:</span> <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Ak-47: 5г-5000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>OG KUSH: 3г-3900р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Bluberry: 3г-3600р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Big But: 5г-4000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>White Russia: 5г - 4000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Pineapple express: 3гр-6000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>White Widow:3гр-3500р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Hot pepper Skunk:3гр-3600р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span> Tangerine Kush: 3гр -3300р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Гаш: 3г-2000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>План: 3г-2000р<br><span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻<span class="emoji  emoji-spritesheet-0" style="background-position: -288px -72px;" title="runner">:runner:</span>🏻 <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Амф: 1г-2500(белый) <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Амф: 1г-2500.(розовый) <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Соль: 1г-2500р. <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Мет: 1г-3000р. <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Меф: 1г-3000р<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>MDMA(crystals): 1г-3500р. <br><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span><span class="emoji  emoji-spritesheet-2" style="background-position: -450px -0px;" title="cd">:cd:</span> <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Tesla (250mg MDMA) <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>SKYPE (230 mg MDMA) <br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Molly (230mg MDMA) <br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>1-5 шт. 1200р/шт <br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>5-10 шт. 980р/шт<br><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><span class="emoji  emoji-spritesheet-1" style="background-position: -306px -36px;" title="mushroom">:mushroom:</span><br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>LSD доты: ЛСД-25(250мг)-2400р/2шт<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>LSD марки: 250мг/3400р/2шт<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Мескалин: <br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>Мухоморы: 3000р/10гр/2дозы<br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>Сульфат: 3000р/1гр/2дозы<br><span class="emoji  emoji-spritesheet-4" style="background-position: -414px -90px;" title="black_small_square">:black_small_square:</span>Псилоцебиновые грибы:<br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>Golden teacher: 4000р/3гр<br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>Psilocybe Cubensis:4000р/3гр<br><span class="emoji  emoji-spritesheet-4" style="background-position: -576px -90px;" title="small_red_triangle_down">:small_red_triangle_down:</span>Pink Buffalo: 4000р/3гр<br>ГРИБЫ!!!! Рекомендованая дозировка не мение 1г на человека. Для новичков не стоит употреблять больше 2г. Оптимальный вариант разделить 3г с другом, и отправиться в незабываемое путешествие, по глубинам своего сознания!<br>Для опытных предлагаю дозировку в 3г. Погружение на 8 часов вам обеспеченно. Хорошо сочитаеться с марихуанной.<br>Так же перед употреблением советуем не принимать пищу за 3-5 часов.'
        l1.append(inline_keyboard('Выбрать '+product_main_spec, 'main_cat'))
        l1.append(inline_keyboard('На главную', '/start')) 
    ##balance itd
    elif method == 'cashbalance':
        text = 'Ваш баланс: '+str(q1.balance)+''
        l1.append(inline_keyboard('Пополнить', 'replenish'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish':
        text = replenish_msg
        l1.append(inline_keyboard('Отправил', 'replenish_check'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish_check':
        text = 'Введите номер транзакции.'
        ##add dobavit' kartinku s obrazcom nomera transakcii
        #тут меняется инстанс абонента на 1(т.е. ожидает проверки оплаты и уже через мсдж идёт проверка текста(а именно проверка транзакции через киви апи))
        q1.payment_instance = 1
        q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish_success':
        text = 'Ваш баланс был успешно пополнен на сумму:'+q2+'.\nВаш баланс составляет:'+str(q1.balance)+''
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish_exists':
        text = 'Данная транзакция уже была проведена.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish_fail':
        text = 'Данная транзакция не проведена.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('На главную', '/start'))
    ##other utils
    elif method == 'helpme':#/pomosh
        text = help_msg
        l1.append(inline_keyboard('Связь с оператором', 'support'))
        l1.append(inline_keyboard('Ищу работу', 'seekjob'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'support':#otpravki obrasheniya support
        text = support_apply_msg
        q1.support_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'seekjob':#otpravki obrasheniya poisk raboti
        text = support_apply_msg
        q1.job_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    elif method[0] == 'j':#pokaz info o tovare
        if False:
            dsa = product.objects.get(pk=method[1:])
            #proverka buyera
            if fake_app == 0:
                if dsa.buyer != q1:
                    dsa = None
            elif fake_app == 1:
                k1 = set()
                k2 = set()
                k2.add(dsa)
                for i in q1.fake_purchases.all():
                    k1.add(i)
                if len(k2-k1) != 0:
                    dsa = None
            if dsa:    
                text = 'Товар: '+dsa.type_of_product.name+'\n\nМестоположение:'+dsa.placing.pre_full_name+'\n\nСтоимость: '+str(dsa.price) +'\n\nСсылка на геолокацию: '+dsa.geolocation + '\n\nДополнительное описание: '+dsa.commentary +'.\n\n Ссылка на фото: '+ dsa.foto_link+''
            else:
                text= 'К сожалению, данные об этом товаре принадлежат другому пользователю.'
                l1.append(inline_keyboard('Помощь', 'support'))
            dsa = bought_products.objects.get(pk=method[1:])
        #try:#esli est' transakciya
        if True:
            dsa = bought_products.objects.get(pk=method[1:])
            if q1 == dsa.abonent:
                method = dsa.name.split('r')
                print('here')
                print(method[0].split('|')[0])
                nazvaniye_gavna = cat_and_price_list[int(method[0].split('|')[0])]['subcat_list'][int(method[0].split('|')[1])][0]
                vid_gavna = cat_and_price_list[int(method[0].split('|')[0])]['name']
                cena_gavna = cat_and_price_list[int(method[0].split('|')[0])]['subcat_list'][int(method[0].split('|')[1])][1]
                g0 = raion.objects.get(pk=method[1])
                text = 'Товар: '+nazvaniye_gavna +'\nМестоположение: '+g0.pre_full_name +'\nСтоимость: '+str(cena_gavna) +'\nДополнительное описание: -'
                send_tg_geolocation(str(q1.telega_id), str(g0.latitude), str(g0.longitude))
                #text = 'Товар: '+dsa.type_of_product.name+'\n\nМестоположение:'+dsa.placing.pre_full_name+'\n\nСтоимость: '+str(dsa.price) +'\n\nСсылка на геолокацию: '+dsa.geolocation + '\n\nДополнительное описание: '+dsa.commentary +'.\n\n Ссылка на фото: '+ dsa.foto_link+''
            else:
                text= 'К сожалению, данные об этом товаре принадлежат другому пользователю.'
                l1.append(inline_keyboard('Помощь', 'support'))
            l1.append(inline_keyboard('На главную', '/start'))
        #except:#esli transakcii net
        if False:
            text = 'Покупка отсутствует'
            l1 = list()
            l1.append(inline_keyboard('На главную', '/start'))
    ##logika pokupki tovara
    elif method == 'main_cat':#vibor glavnoi kategorii
        text = 'Выберите '+product_main_spec+'.'
        for i in raion.objects.filter(subcategory_of = None):
            l1.append(inline_keyboard(i.name, 'r'+str(i.pk)))
        l1.append(inline_keyboard('На главную', '/start')) 
    elif method[0] == 'r':#1stinstance #vibor vida tovara posle main raiona
        ##вообще, тут может возникнуть дохуя ошибок, И если планируется нечто потипу мирового с разделениями на страны
        #, то требуется рефакторинг
        #method = 'r1'
        g0 = raion.objects.get(pk=method[1:])#uznaem voobshe chto eto za raion
        text = 'Город: '+g0.pre_full_name+'\n\nВыберите район.'
        #here
        if False:
            x = 0
            for i in cat_and_price_list:#
                l1.append(inline_keyboard(i['name'], 'f'+str(x)+'r'+str(g0.pk)))
                x += 1
        else:
            for i in raion.objects.filter(subcategory_of=g0):
                l1.append(inline_keyboard(i.name, 'f'+str(i.pk)))
        #dao zher

        #xinde
        l1.append(inline_keyboard('Назад', 'main_cat'))
        l1.append(inline_keyboard('На главную', '/start'))#maincat_page
    elif method[0] == 'f':#2ndinstance #vibor tovara posle vida tovara
        #delim method na 2 chasti(ispolzuya split(method, 'r')) 'f' i 'r', gde [0][1:](f...) - kategoriya, [1](r...) - raion
        if True:
            g0 = raion.objects.get(pk=method[1:])#uznaem voobshe chto eto za raion
            text = 'Город: '+g0.subcategory_of.name+'\nРайон: '+g0.name+'\n\nВыберите вид товара.' 
            x = 0
            for i in cat_and_price_list:#
                l1.append(inline_keyboard(i['name'], 'y'+str(x)+'r'+str(g0.pk)))
                x += 1
        l1.append(inline_keyboard('Назад', 'r'+str(g0.subcategory_of.pk)))#back button
        l1.append(inline_keyboard('На главную', '/start'))#maincat_page
    elif method[0] == 'y':#3rdinstance #vibor raiona posle vida tovara
        #delim method na 2 chasti(ispolzuya split(method, 'r')) 'y' i 'r', gde [0][1:]\\(y12|23) - info o tovare, [1](r...) - info o raione
        method = method.split('r')#f12r23
        g0 = raion.objects.get(pk=method[1])#vizvaniy main_raion
        text = 'Город: '+g0.subcategory_of.name+'\nРайон: '+g0.name+'\nВид товара: '+cat_and_price_list[int(method[0][1:])]['name']+'\n\n'
        x = 0
        for i in cat_and_price_list[int(method[0][1:])]['subcat_list']:
            text+= i[0] +' '+ str(i[1])+'р\n'
            l1.append(inline_keyboard(i[0], 'u'+method[0][1:]+'|'+str(x)+'r'+str(g0.pk)))##y12|23r23
            x += 1
        text += '\nВыберите товар.'
        l1.append(inline_keyboard('Назад', 'f'+str(g0.pk)))
        l1.append(inline_keyboard('На главную', '/start'))#maincat_page
        if False:#test purposes
            print(nazvaniye_gavna)
            print(cat_and_price_list[int(method[0].split('|')[0][1:])]['name'])
            print(cena_gavna)
    elif method[0] == 'u':#4thinstance #vibor metoda oplati posle vibora raiona
        #delim method na 2 chasti(ispolzuya split(method, 'r')) 'y' i 'r', gde [0][1:]\\(y12|23) - info o tovare, [1](r5) - info o raione
        #get object from products(raion = r, product_type = u), order_by date i vibor u kotorogo data sozdaniya samaya poslednyaya
        _method = method
        method = method.split('r')#u1|3r7
        nazvaniye_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][0]
        vid_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['name']
        cena_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][1]
        g0 = raion.objects.get(pk=method[1])
        text = 'Город: '+g0.subcategory_of.name+'\nРайон: '+g0.name+'\nВид товара: '+vid_gavna+ '\nТовар: '+nazvaniye_gavna+ '\nЦена: '+str(cena_gavna)+ '\n\nВыберите метод оплаты.'
        if False:#test purposes
            print(nazvaniye_gavna)
            print(cat_and_price_list[int(method[0].split('|')[0][1:])]['name'])
            print(cena_gavna)
        l1.append(inline_keyboard('Оплата с баланса', 'b'+_method[1:]))
        #l1.append(inline_keyboard('Оплата по транзакции', 'h'+_method[1:]))
        l1.append(inline_keyboard('Назад', 'y'+str(method[0][1:])+'r'+str(g0.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method[0] == 'b':#oplata s balansa + redirect na popolneniye
        if False:
            dsa = product.objects.get(pk=method[1:])
            if dsa.buyer:
                text = 'К сожалению, данный товар был только-что куплен или зарезервирован, попробуйте выбрать снова.'
            else:
                text = 'Ваш баланс: '+str(q1.balance)+'.\nСтоимость '+dsa.type_of_product.name+' в '+ dsa.placing.pre_full_name+': '+str(dsa.price)
                
                if q1.balance >= dsa.price:#proveryaem est' li vozmozhnost' oplatit'
                    text+='\nУ вас хватает денежных средств для оплаты, нажмите "Оплатить с баланса" для получения подробной информации о местоположении товара.'
                    l1.append(inline_keyboard('Оплатить с баланса', 'v'+str(dsa.pk)))
                    l1.append(inline_keyboard('Оплатить транзакцией', '#broken'))
                #esli net, to predlagaem popolnit; balans
                else:
                    text+='\nНа вашем балансе недостаточно средств для оплаты.\nПополните баланс для дальнейшей оплаты или оплатите используя транзакцию.'
                    l1.append(inline_keyboard('Пополнить баланс', 'replenish'))
                    ###
                    ###
                    ###dodelai
                    #l1.append(inline_keyboard('Оплатить транзакцией', '#broken'))
                    #vverhu broken
            l1.append(inline_keyboard('Назад', 'u'+str(dsa.type_of_product.pk)+'r'+str(dsa.placing.pk)))
        _method = method
        method = method.split('r')#b1|3r5|7
        nazvaniye_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][0]
        vid_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['name']
        cena_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][1]
        g0 = raion.objects.get(pk=method[1])
        #text = 'Стоимость '+dsa.type_of_product.name+' в '+ dsa.placing.pre_full_name+': '+str(dsa.price)
        text = 'Ваш баланс: '+str(q1.balance)+'\nВид товара: '+vid_gavna+ '\nТовар: '+nazvaniye_gavna+ '\nЦена: '+str(cena_gavna)+ '\nГород: '+g0.subcategory_of.name+'\nРайон: '+g0.name+'\n'
        if q1.balance >= float(cena_gavna):#proveryaem est' li vozmozhnost' oplatit'
            text+='\nУ вас хватает денежных средств для оплаты, нажмите "Оплатить с баланса" для получения подробной информации о местоположении товара.'
            l1.append(inline_keyboard('Оплатить с баланса', 'v'+_method[1:]))
        else:
            text+='\nНа вашем балансе недостаточно средств для оплаты.\nПополните баланс для дальнейшей оплаты или оплатите используя транзакцию.'
            l1.append(inline_keyboard('Пополнить баланс', 'replenish'))
        l1.append(inline_keyboard('Назад', 'u'+_method[1:]))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method[0] == 'v':#oplata s balansa
        #tut sdelai proverku na nalichiye tovara, chtobi klient vdrug ne oplatil tovar kotoriy uzhe prodan cherez try except
        _method = method
        method = method.split('r')#b1|3r5|7
        nazvaniye_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][0]
        vid_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['name']
        cena_gavna = cat_and_price_list[int(method[0].split('|')[0][1:])]['subcat_list'][int(method[0].split('|')[1])][1]
        g0 = raion.objects.get(pk=method[1])
        if q1.balance >= float(cena_gavna):
            q1.balance-=float(cena_gavna)
            q1.save()
            created_product = bought_products.objects.create(abonent = q1, name = _method[1:], display = nazvaniye_gavna)
            text = 'Оплата прошла успешно.\nВаш баланс: '+str(q1.balance)+'\nДля получения информации о товаре нажмите "Подробнее"'



            send_notification('сделана покупка '+str(vid_gavna)+ ' '+str(nazvaniye_gavna) +' в '+str(g0.pre_full_name)+' '+str(q1.name)+' '+str(q1.telega_id))
            send_tg_geolocation(str(q1.telega_id), str(g0.latitude), str(g0.longitude), 2)


            l1.append(inline_keyboard('Подробнее', 'j'+str(created_product.pk)))
        else:
            text = 'К сожалению, на вашем балансе недостаточно средств для оплаты.'
            l1.append(inline_keyboard('Пополнить', 'replenish'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method[0] == 'h':#oplata transakciyei
        dsa = product.objects.get(pk=method[1:])
        if dsa.buyer:
            text = 'К сожалению, данный товар был только-что куплен или зарезервирован, попробуйте выбрать снова.'
        else:
            text = 'Товар: '+dsa.type_of_product.name+'\n\nМестоположение:'+dsa.placing.pre_full_name+'\n\nСтоимость: '+str(dsa.price)+'\n\nОтправьте платёж на сумму: '+str(dsa.price)+' на киви кошелёк: ' +qiwi_wallet_num+', после оплаты нажмите *Продолжить*.'
            l1.append(inline_keyboard('Продолжить', 'x'+str(dsa.pk)))
            l1.append(inline_keyboard('Обновить', method))
        l1.append(inline_keyboard('Назад', 'f'+str(dsa.type_of_product.pk)+'r'+str(dsa.placing.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method[0] == 'x':#podtverjdeniye transakcii
        dsa = product.objects.get(pk=method[1:])
        if dsa.buyer:
            text = 'К сожалению, данный товар был только-что куплен или зарезервирован, попробуйте выбрать снова. \n\nЕсли вы уже произвели перевод денежных средств, вы можете зачислить их себе на баланс и выбрать другой товар.'
            l1.append(inline_keyboard('Пополнить', 'replenish'))
        else:
            text = 'Введите номер транзакции для оплаты:\n\nТовар: '+dsa.type_of_product.name+'\nМестоположение:'+dsa.placing.pre_full_name+'\nСтоимость: '+str(dsa.price)
            #тут меняется инстанс абонента на 2(т.е. ожидает проверки оплаты и уже через мсдж идёт проверка текста(а именно проверка транзакции через киви апи))
            q1.payment_instance = 2
            #i zahooyachim suda instance, dlya togo chtobi znat' o kakom imenno tovare idet rech
            q1.transaction_instance = dsa
            q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    #rabota s transakciyami
    elif method == 'transaction_success':
        text = 'Оплата прошла успешно.\nВаш баланс: '+str(q1.balance)+'\nДля получения информации о товаре нажмите "Подробнее"'
        l1.append(inline_keyboard('Подробнее', 'j'+str(q1.transaction_instance.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'transaction_nem':#esli ne hvataet deneg dlya oplati transakcii
        text= 'К сожалению, сумма вашей транзакции меньше стоимости товара, денежные средства были зачислены на ваш баланс.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'transaction_bought':
        text= 'К сожалению, товар был оплачен раньше чем подтвердился ваш платёж, денежные средства были зачислены на ваш баланс.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('На главную', '/start'))
    #vibor raiona posle vibora raiona
    else:
        None
    if len(l1) > 0:
        buttons = form_reply_markup(l1)
    else:
        buttons = None
    return text, buttons
#reply
@csrf_exempt
def telegram_api(request):
    try:
        if True:#testting purpose
            try:
                ##dlya raboti s jsonom
                #print(json.loads(request.body))
                #print(user_info["data"])
                print(request.body)
                #print(return_dict)
                None
            except:
                None
        #main_route
        if True:#check if json, ignore ussual requests
            try: fulljson = json.loads(request.body)
            except: raise Http404
        if True:#check if project exists
            try: tg_project = telegram_project.objects.get(pk=request.GET.get('q'))
            except: raise Http404
        if True:#collecting data from msg
            try:#check request type, msg or callback query
                user_info = fulljson["callback_query"]
                reply_type = 'callback_query'
            except:
                user_info = fulljson["message"]
                reply_type = 'message'
            if True:#ignore bots, eto dlya togo, chtobi ignorit' soobsheniya ot botov
                if user_info["from"]["is_bot"] == 'true':
                    raise Http404
            reciever_id = user_info["from"]["id"]
            reciever_name = user_info["from"]["first_name"]
            user_a, created = abonent.objects.get_or_create(telega_id = reciever_id)
            user_a.name = reciever_name
            user_a.save()
            ####
        #if tg_project.tg_type == 'tg_dv_fake':
        if True:##redirect on func #refactori
            #esli eto soobsheniye
            return_dict= dict()
            if reply_type == 'message':
                try:
                    recieve_text = fulljson["message"]["text"]
                except:
                    return HttpResponse("")
                if True: #platejka refactori
                    if user_a.payment_instance == 1:#v sluchae esli ojidaet popolneniya balansa
                        user_a.payment_instance = 0
                        a1, a2 = qiwi_api(recieve_text)
                        if a1 == True:#esli oplata proshla uspeshno
                            user_a.balance=user_a.balance+ float(a2)
                            finished_transaction.objects.create(project_fk = tg_project, abonent = user_a, txnId = recieve_text, cash = float(a2))
                            return_dict["text"], return_dict["reply_markup"] = reply('replenish_success', user_a, a2)
                        elif a1 == False:#payment is real but already used
                            return_dict["text"], return_dict["reply_markup"] = reply('replenish_exists', user_a)
                        #tipo void? ili kak v pythone eto der'mo?
                        else:#payment doesn't exists
                            return_dict["text"], return_dict["reply_markup"] = reply('replenish_fail', user_a)
                        user_a.save()
                    elif user_a.payment_instance == 2:#v sluchae podtverjdeniya oplati za zakaz(т.е. проведения транзакции)
                        user_a.payment_instance = 0
                        a1, a2 = qiwi_api(recieve_text)
                        if a1 == True:
                            user_a.balance=user_a.balance+ float(a2)
                            finished_transaction.objects.create(project_fk = tg_project, abonent = user_a, txnId = recieve_text, cash = float(a2))
                            if user_a.balance >= user_a.transaction_instance.price:#esli deneg на балансе hvataet na transakciyu
                                ##addtut chekai est' li u obiekta pokupki pokupatel' dabi ne perepisivat' istoriyu
                                if user_a.transaction_instance.buyer:#esli ne norm, to:
                                    return_dict["text"], return_dict["reply_markup"] = reply('transaction_bought', user_a)
                                #esli norm, to:
                                else:
                                    user_a.balance = user_a.balance - user_a.transaction_instance.price
                                    if fake_app == 0:
                                        user_a.transaction_instance.buyer = user_a
                                        user_a.transaction_instance.sold_date = timezone.now()
                                        user_a.transaction_instance.save()
                                    elif fake_app == 1:
                                        user_a.fake_purchases.add(user_a.transaction_instance)
                                    return_dict["text"], return_dict["reply_markup"] = reply('transaction_success', user_a)
                            #esli deneg ne hvataet, to
                            else:
                                return_dict["text"], return_dict["reply_markup"] = reply('transaction_nem', user_a)
                            user_a.transaction_instance = None
                            smsg(a2)
                        elif a1 == False:#payment is real but already used

                            return_dict["text"], return_dict["reply_markup"] = reply('replenish_exists', user_a)
                        #tipo void? ili kak v pythone eto der'mo?
                        else:#payment does'nt exists

                            return_dict["text"], return_dict["reply_markup"] = reply('replenish_fail', user_a)
                        user_a.transaction_instance = 0
                        user_a.save()
                    #v sluchae esli init fraza
                    elif recieve_text == tg_project.start_word:
                        return_dict["text"], return_dict["reply_markup"] = reply(recieve_text)
                    #missunderstood msg na obichnuyu otpravku soobsheniya
                    else:
                        return_dict["text"] = 'Попробуйте написать: '+tg_project.start_word
            #esli eto nazhatiye na knopki
            elif reply_type == 'callback_query':
                if user_a.payment_instance != 0:#esli user ozhidaet oplati, no nazhal na knopku
                    user_a.payment_instance = 0
                    user_a.save()
                query = user_info["data"]
                return_dict["text"], return_dict["reply_markup"] = reply(query, user_a)
                answerCallbackQuery(tg_project.tg_token, user_info["id"])
        if True:#refactored logic    #danniye o dvuh kommunikatorah, tg_project i user
            tg_project#object telegram_project
            user_a#danniye o otpravitele soobsheniya
            if tg_project.tg_type == 'tg_shop_fake':#logica fake magaza v tg
                None
        if True:#metod otveta + OTBET
            if not return_dict: return_dict= dict()
            return_dict["chat_id"] = reciever_id
            return_dict["method"] = 'sendmessage'
            #return_dict["parse_mode"] = 'HTML'
        if True:#testting purpose
            try:
                ##dlya raboti s jsonom
                #print(json.loads(request.body))
                #print(user_info["data"])
                #print(request.body)
                #print(return_dict)
                None
            except:
                None
        if return_dict:return JsonResponse(return_dict)
        else:return HttpResponse('')
    except:return HttpResponse('')

#logika dlya raboti s qiwi
def qiwi_api(a):
    try:
        finished_transaction.objects.get(txnId=a)
        return False, None
        #transakciya ispol'zovana
    #proveryaem transakciyu
    except:
        try:
            check_transaction_url = 'https://edge.qiwi.com/payment-history/v2/transactions/'+a+'?type=IN'
            r = requests.get(check_transaction_url, headers=qiwi_headers)
            transaction_json = json.loads(r.text)
            #nomer poluchatelya
            #print(transaction_json["personId"])
            #check if num is your's
            if str(transaction_json["personId"])==qiwi_wallet_num:
                #check status
                #print(transaction_json["status"])
                if transaction_json["status"] == 'SUCCESS':
                    #check total currency
                    #print(transaction_json["total"]["currency"])
                    #print(type(transaction_json["total"]["currency"]))
                    if transaction_json["total"]["currency"] == 643:
                        #get amount
                        #print(transaction_json["total"]["amount"])
                        #print(str(transaction_json["total"]["amount"])) 
                            #
                        return True, str(transaction_json["total"]["amount"])
        except:
        ##payment does'nt exists ili ne prenadlejit etomu qiwi ili chtoto drugoe, mb server upal, mb qiwi upal, yaneebu
            return None, None
    #utils\test