from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import logout, authenticate, login
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
#import kakih-to peremennykh
from .data_settings import tele_token, help_msg, support_apply_msg, product_main_spec, start_msg


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
        elif request.GET.get('q', '') == 'product_type':
            if request.GET.get('que', '') != '':
                object = product_type.objects.get(pk=request.GET.get('que'))
            form = product_typeForm(instance = object)
        #elif request.GET.get('q', '') == 'product_type':
        if request.method == "POST":
            if request.GET.get('q', '') == 'raion':
                form = raionForm(request.POST, instance=object)
            elif request.GET.get('q', '') == 'product_type':
                form = product_typeForm(request.POST, instance=object)
            if form.is_valid():
                i = form.save()
                return redirect('/main_page/cp'+ '?q=%s'%(request.GET.get('q'))) 
        return render(request, 'cp/formpage.html',{
        'form':form,
        })


####logika dlya raboti s api telegrama
def inline_keyboard(a, b):
    smth = dict()
    smth["text"] = a
    smth["callback_data"] = b
    #1st array(v nem oborachivaem otdel'nuyu liniyu knopok)
    somelist1 = list()
    somelist1.append(smth)
    return somelist1
#formiruyet dict knopok dlya otveta iz spiska @a
def form_reply_markup(a):
    z = dict()
    z["inline_keyboard"] = a
    return z
#reply func dlya manual'nogo formirovaniya otvetov
def reply(method):
    somelist1 = list()
    if method == '/privet':
        text = start_msg
        somelist1 = list()
        somelist1.append(inline_keyboard('Выбрать '+product_main_spec, 'main_cat'))
        somelist1.append(inline_keyboard('Баланс', 'cashbalance'))
        somelist1.append(inline_keyboard('Подтвердить оплату', 'applypayment'))
        somelist1.append(inline_keyboard('Помощь', 'helpme'))
    elif method == 'helpme':
        text = help_msg
        somelist1.append(inline_keyboard('Связь с оператором', 'support'))
        somelist1.append(inline_keyboard('Назад', 'main'))
    elif method == 'support':
        text = support_apply_msg
        somelist1.append(inline_keyboard('На главную', 'main'))
    elif method == 'main_cat':
        text = 'Выберите город:'
        ##########po horoshemu dobav' spisok gorodov v bazu ili uberi nahui, voobshe, kak variant, sdelat' eto s podkategoriyami
        ##########tipo kak category s subctegory na FK, no hz? 
        somelist1.append(inline_keyboard('Владивосток', 'town_vlad'))
        somelist1.append(inline_keyboard('Находка', 'town_nakh'))
        somelist1.append(inline_keyboard('Уссурийск', 'town_ussu'))
    if len(somelist1) > 0:
        buttons = form_reply_markup(somelist1)
    else:
        buttons = None
    return text, buttons
#reply
@csrf_exempt
def telegram_api(request):
    #testing purpose
    try:
        ##dlya raboti s jsonom
        print(json.loads(request.body))
        #print(request.body)
        ###v sluchae esli eto message
        ##id poluchatelya
        #print(json.loads(request.body)["message"]["from"]["id"])
        ##text
        #print(json.loads(request.body)["message"]["text"])
        ###esli callback query
        ##id poluchatelya
        #
        None
    except:
        None
    #check if json, ignore ussual requests
    try:
        fulljson = json.loads(request.body)
    except:
        raise Http404
    #main logic
    reciever_id = None
    recieve_text = None
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
    if user_info["from"]["is_bot"] == 'true':
        raise Http404
    #eto otvet json
    return_dict = dict()
    #然后就可以改变发信的方式
    return_dict["method"] = 'sendmessage'
    #tut hranitsya id abonenta
    return_dict["chat_id"] = reciever_id
    #做完后这个100%没有用
    somelist1 = list()
    #esli eto soobsheniye
    if reply_type == 'message':
        recieve_text = fulljson["message"]["text"]
        if recieve_text == '/privet':
            return_dict["text"], return_dict["reply_markup"] = reply(recieve_text)
        #v sluchae otpravki transakcii, chekai instance abonenta
        elif False:
            None
        #missunderstood msg
        else:
            return_dict["text"] = 'Попробуйте написать: /privet'
    #esli eto nazhatiye na knopki
    elif reply_type == 'callback_query':
        query = user_info["data"]
        ##po horoshemu, na etot query nado otvechat'
        #query_id = user_info["id"]
        #reply
        return_dict["text"], return_dict["reply_markup"] = reply(query)
        if False:
            return_dict["text"], return_dict["reply_markup"] = reply(query)         
        elif query == 'support':
            return_dict["text"], return_dict["reply_markup"] = reply(query) 
        elif query == 'main_cat':
            return_dict["text"], return_dict["reply_markup"] = reply(query) 
        #gavno i palki:D
        if len(somelist1)!=0:
            return_dict["reply_markup"] = form_reply_markup(somelist1)
        ##做完后可以改到:
        # #$return_dict["text"], return_dict["reply_markup"] = reply(query)
        #if query == 'main':
    return JsonResponse(return_dict)

#logika dlya raboti s qiwi
def qiwi_api():
    None

# Create your views here.
