from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import logout, authenticate, login
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
#import kakih-to peremennykh
from .data_settings import help_msg, support_apply_msg, product_main_spec, start_msg, replenish_msg


#login
#ispol'zueyetsya iskluchitel'no dlya auntifikacii, s posleduyushim razdeleniem na staff(rabotyagi) i na admina(vladelca)
def sign(request):
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

#tut vsya logika paneli upravleniya dlya admina, dlya rabotnikov luchshe napisat' otdel'nuyu i dlya rabotyagi
def main(request):
    if request.user.is_superuser:
        page = 'main'
        obj_list = None
        obj = None
        if request.GET.get('q', '') == 'raion':
            obj = 'raion'
            page = 'object_list'
            obj_list = raion.objects.all()
        elif request.GET.get('q', '') == 'product_type':
            obj = 'product_type'
            page = 'object_list'
            obj_list = product_type.objects.all()
        elif request.GET.get('q', '') == 'abonent':
            obj = 'abonent'
            page = 'object_list'
            obj_list = abonent.objects.all()
        elif request.GET.get('q', '') == 'product':
            obj = 'product'
            page = 'object_list'
            obj_list = product.objects.all()
        return render(request, 'cp/main.html',{
        'page': page,
        'obj': obj,
        'obj_list': obj_list,
        })
    else:
        raise Http404

##formpage(edit\create)
def formpage(request):
    if request.user.is_superuser:
        form = None
        object = None
        if request.GET.get('q', '') == 'raion':
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
        #elif request.GET.get('q', '') == 'product_type':
        if request.method == "POST":
            if request.GET.get('q', '') == 'raion':
                form = raionForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'product_type':
                form = product_typeForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'product':
                form = productForm(request.POST, instance=object)
            if form.is_valid():
                i = form.save()
                return redirect('/main_page/cp'+ '?q=%s'%(request.GET.get('q'))) 
        return render(request, 'cp/formpage.html',{
        'form':form,
        })


####logika dlya raboti s api telegrama
def inline_keyboard(a, b):

    return [{'text': a, 'callback_data': b}]
#formiruyet dict knopok dlya otveta iz spiska @a
def form_reply_markup(a):

    return {'inline_keyboard': a}
#reply func dlya manual'nogo formirovaniya otvetov
def reply(method, q1 = None, q2 = None):
    l1 = list()
    text = None
    # /privet, helpme, support, main_cat cashbalance
    ###NAIDI OPERATOR switch() v pythone, etot "elif" metod - ebala pzdc,
    # ili kak variant, sdelai razdeleniye po prefiksam, sikonomit vremya
    #main menu /privet
    if method == '/privet':
        text = start_msg
        l1.append(inline_keyboard('Выбрать '+product_main_spec, 'main_cat'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('Подтвердить оплату', 'applypayment'))
        l1.append(inline_keyboard('Помощь', 'helpme'))
    #balance itd
    elif method == 'cashbalance':
        text = 'Ваш баланс: '+str(q1.balance)+'.'
        l1.append(inline_keyboard('Пополнить', 'replenish'))
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'replenish':
        text = replenish_msg
        l1.append(inline_keyboard('Отправил', 'replenish_check'))
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'replenish_check':
        text = 'Введите номер транзакции.\n\n//тестовый вариант, введи *123456789*, это типо номер успешной транзакции на 500 рублей,\n введи *987654321*, это номер уже проведённой транзакции, получишь сообщение о неудаче платежа, мол типо транзакция уже зарегестрирована,\n другие цифры или значения или я неебу чё означают несуществующую транзакцию.\n\n мне нужно 2 киви кошелька для тестов'
        #тут меняется инстанс абонента на 1(т.е. ожидает проверки оплаты и уже через мсдж идёт проверка текста(а именно проверка транзакции через киви апи))
        q1.payment_instance = 1
        q1.save()
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'replenish_success':
        text = 'Ваш баланс был успешно пополнен на сумму:'+q2+'.\nВаш баланс составляет:'+str(q1.balance)+'.'
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'replenish_exists':
        text = 'Данная транзакция уже была проведена.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'replenish_fail':
        text = 'Данная транзакция отсутствует.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('На главную', '/privet'))
    #/pomosh
    elif method == 'helpme':
        text = help_msg
        l1.append(inline_keyboard('Связь с оператором', 'support'))
        l1.append(inline_keyboard('Ищу работу', 'seekjob'))
        l1.append(inline_keyboard('На главную', '/privet'))
    #otpravki obrasheniya
    elif method == 'support':
        text = support_apply_msg
        q1.support_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/privet'))
    elif method == 'seekjob':
        text = support_apply_msg
        q1.job_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/privet'))
    #vibor glavnoi kategorii
    elif method == 'main_cat':
        text = 'Выберите '+product_main_spec+':' 
        for i in raion.objects.filter(subcategory_of = None):
            l1.append(inline_keyboard(i.name, 'r'+str(i.pk)))
        l1.append(inline_keyboard('На главную', '/privet'))
    #vibor raiona
    elif method[0] == 'r':
        #uznaem voobshe chto eto za raion
        g0 = raion.objects.get(pk=method[1:])
        g1 = raion.objects.filter(subcategory_of = g0)
        #check esli eto kategoriya bez podkategoriy, to prodolzhaem vibor
        if len(g1)>0:
            text = 'Уточните местоположение в '+g0.pre_full_name+'.'
            for i in g1:
                l1.append(inline_keyboard(i.name, 'r'+str(i.pk)))
            if g0.subcategory_of:
                l1.append(inline_keyboard('Назад', 'r'+str(g0.subcategory_of.pk)))
            else:
                l1.append(inline_keyboard('Назад', 'main_cat'))
        #inache predlagaem product_type
        else:
            ##berem spisok tovarov v dannom raione
            g2 = product.objects.filter(placing = g0)
            ##chekaem est' li tovar v dannom raione
            if len(g2)==0:
                text = 'К сожалению,на данный момент нет товаров в '+g0.pre_full_name+', попробуйте выбрать другое место.'
                if g0.subcategory_of:
                    l1.append(inline_keyboard('Назад', 'r'+str(g0.subcategory_of.pk)))
                else:
                    l1.append(inline_keyboard('Назад', 'main_cat'))
            ##predlagaem product_type v dannom raione
            else:
                text = 'Выберите товар в '+g0.pre_full_name+'.'
                ##eto 
                u2 = set()
                for i in g2:
                    u2.add(i.product.type)
                ##tut uzhe vibor product_type
                for j in u2:
                    l1.append(inline_keyboard(j.name, 'f'+str(j.pk)+'r'+str(g0.pk)))
        l1.append(inline_keyboard('На главную', '/privet'))
    #vibor tovara
    elif method[0] == 'f':
        #delim method na 2 chasti(ispolzuya split(method, 'r')) 'f' i 'r', gde [0](f...) - kategoriya, [1](r...) - raion
        #get object from products(raion = r, product_type = f) u kotorogo data sozdaniya samaya poslednyaya
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
        None
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
    #testing purpose
    try:
        ##dlya raboti s jsonom
        #print(json.loads(request.body))
        print(request.body)
        None
    except:
        None
    #utils##

    #check if json, ignore ussual requests
    try:
        fulljson = json.loads(request.body)
    except:
        raise Http404
    #collecting data
    reciever_id = None
    user_info = None
    reply_type = None
    #check request type, msg or callback query
    try:
        user_info = fulljson["callback_query"]
        reply_type = 'callback_query'
    except:
        user_info = fulljson["message"]
        reply_type = 'message'
    reciever_id = user_info["from"]["id"]
    #ignore bots, eto dlya togo, chtobi ignorit' soobsheniya ot botov
    if user_info["from"]["is_bot"] != 'False':
        raise Http404
    #eto otvet json
    return_dict = dict()
    #然后就可以改变发信的方式
    return_dict["method"] = 'sendmessage'
    #tut hranitsya id abonenta
    return_dict["chat_id"] = reciever_id
    user_a, created = abonent.objects.get_or_create(telega_id = reciever_id)
    ##redirect on func
    #esli eto soobsheniye
    if reply_type == 'message':
        recieve_text = fulljson["message"]["text"]
        #v sluchae esli ojidaet popolneniya balansa
        if user_a.payment_instance == 1:
            #payment is real and not used
            user_a.payment_instance = 0
            a1, a2 = qiwi_api(recieve_text)
            if a1 == True:
                user_a.balance=user_a.balance+ float(a2)
                return_dict["text"], return_dict["reply_markup"] = reply('replenish_success', user_a, a2)
            #payment is real but already used
            elif a1 == False:
                return_dict["text"], return_dict["reply_markup"] = reply('replenish_exists', user_a)
            #payment does'nt exists
            else:
                return_dict["text"], return_dict["reply_markup"] = reply('replenish_fail', user_a)
            user_a.save()
        #v sluchae podtverjdeniya oplati za zakaz
        elif user_a.payment_instance == 2:
            None
        #v sluchae esli init fraza
        elif recieve_text == '/privet':
            return_dict["text"], return_dict["reply_markup"] = reply(recieve_text)
        #missunderstood msg na obichnuyu otpravku soobsheniya
        else:
            return_dict["text"] = 'Попробуйте написать: /privet'
    #esli eto nazhatiye na knopki
    elif reply_type == 'callback_query':
        query = user_info["data"]
        return_dict["text"], return_dict["reply_markup"] = reply(query, user_a)
        ##po horoshemu, na etot query nado otvechat'
        #query_id = user_info["id"]
    return JsonResponse(return_dict)

#logika dlya raboti s qiwi
def qiwi_api(a):
    if a == '123456789':
        return True, '500'
    elif a == '987654321':
        return False, None
    else:
        return None, None

# Create your views here.
