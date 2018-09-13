from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import logout, authenticate, login
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .data_settings import tele_token


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

#tut vsya logika paneli upravleniya dlya admina i dlya rabotyagi
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


#logika dlya raboti s api telegrama
def inline_keyboard(a, b):
    smth = dict()
    smth["text"] = a
    smth["callback_data"] = b
    #1st array(v nem oborachivaem otdel'nuyu liniyu knopok)
    somelist1 = list()
    somelist1.append(smth)
    return somelist1


@csrf_exempt
def telegram_api(request):
    #print(json.loads(request.body)["result"][0]["message"]["from"]["id"])
    try:
        ##dlya raboti s jsonom
        #print(json.loads(request.body))
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
    try:
        fulljson = json.loads(request.body)
    except:
        raise Http404
    reciever_id = None
    recieve_text = None
    user_info = None
    try:
        user_info = fulljson["callback_query"]
    except:
        user_info = fulljson["message"]
    try:
        recieve_text = fulljson["message"]["text"]
    except:
        None
    reciever_id = user_info["from"]["id"]
    if user_info["from"]["is_bot"] == 'true':
        return HttpResponse('')
    return_dict = dict()
    return_dict["method"] = 'sendmessage'
    return_dict["chat_id"] = reciever_id
    if recieve_text:
        if recieve_text == '/privet':
            return_dict["text"] = 'Привет! В наличии есть:'
            #array(v nem uzhe vse knopki)
            somelist1 = list()
            somelist1.append(inline_keyboard('Выбрать город', 'choosetown'))
            somelist1.append(inline_keyboard('Баланс', 'cashbalance'))
            somelist1.append(inline_keyboard('Помощь', 'helpme'))
            dict2 = dict()
            dict2["inline_keyboard"]= somelist1
            return_dict["reply_markup"] = dict2
        #v sluchae otpravki transakcii, chekai instance abonenta
        elif False:
            None
        else:
            return_dict["text"] = 'Попробуй написать:\n /privet'
    return JsonResponse(return_dict)
    #return HttpResponse('')

#logika dlya raboti s qiwi
def qiwi_api():
    None

# Create your views here.
