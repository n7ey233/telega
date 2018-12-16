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

#import kakih-to peremennykh
#from .data_settings import product_main_spec, start_msg, qiwi_headers
#utils
tele_token = '603323645:AAGdcg1XEs4G_-qq08CBxwAxuO-E9FGJNPc'
qiwi_wallet_num = '79841543923'
help_msg = 'Добро пожаловать в наш магазин!\nУважаемый клиент, перед оплатой товара, убедитесь в правильности выбранной информации.\nНа данный момент мы работает ТОЛЬКО с платёжной системой Qiwi.\nОбязательно сохраняйте реквизиты оплаты( выданый ботом номер кошелька, кошелёк на который была произведена оплата, номер транзакции).\n\n Процедура получения товара:\n1)Выбор местоположения, товара( бот предложит все имеющиеся варианты наших закладок).\n2)Бот напишет Вам наш номер кошелька и Ваш номер заказа. Если хотите провести оплату с вашего баланса, нажмите "Оплатить с баланса", если на балансе не будет хватать средств, бот предложит вам пополнить баланс.\n3)Производите оплату на указанный ботом счёт.\n4)Если сумма платежа равна или больше суммы заказа, то бот вышлет информацию о вашем товаре(город, район, описание товара, приблизетельный адресс, фото закладки, геолокацию).\n\nЕсли сумма оплаты превышает цену товара, то разница пополнит ваш баланс.Если же сумма оплаты ниже цены товара, то бот напишет сообщение об ошибке и зачислит средства на ваш баланс.\n\n Возврат денежных средств осуществляется исключительно через связь с оператором.'
replenish_msg = 'Для пополнения баланса отправьте денежные средства на Qiwi кошелёк: '+ qiwi_wallet_num
support_apply_msg = 'Спасибо за обращение, в близжайшее время с вами свяжется наш оператор.'
product_main_spec = 'Место'
shop_name = 'Ušə məəə<3'
start_msg = 'Привет, умняш!!!Добро пожаловать ко мне в магазин - «Use Me»!!!!! Я очень рада, что ты пришёл именно ко мне, ведь у меня для тебя огромный выбор вкусняшек ️\n\nНажми "Выбрать Место" для оформления заказа.\nНажми "Баланс" для проверки своего баланса или его дальнейшего пополнения.\nНажми "Прайс" чтобы увидеть весь ассортимент и цены.\nНажми "История" для просмотра истории своих покупок.\nНажми "Помощь" для просмотра раздела помощи и дальнейшей связи с оператором, если вдруг произойдёт какая-то нелепая ошибка!\n'





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
        text = 'Нажмите на кнопку для получения подробной информации о ваших покупках.\nИстория ваших покупок:'
        if fake_app == 0:
            asdf = product.objects.filter(buyer = q1).order_by('-sold_date')
        elif fake_app == 1:
            asdf = q1.fake_purchases.all()
        if len(asdf) == 0:
            text+='\nУвы, с вашего аккаунта ещё не было покупок'
        else:
            if fake_app == 1:
                for i in asdf:
                        l1.append(inline_keyboard(i.type_of_product.name, 'j'+str(i.pk)))
            else:
                for i in asdf:
                    l1.append(inline_keyboard(str(i.sold_date.strftime('%x'))+' '+i.type_of_product.name, 'j'+str(i.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'price_list':
        text = """
        Ak-47: 5г-5000р
        OG KUSH: 3г-3900р
        Bluberry: 3г-3600р
        Big But: 5г-4000р
        White Russia: 5г - 4000р
        Pineapple express: 3гр-6000р
        ️White Widow:3гр-3500р
        ️Hot pepper Skunk:3гр-3600р
        ️ Tangerine Kush: 3гр -3300р
        Гаш: 3г-2000р
        План: 3г-2000р
        🏻🏻🏻🏻🏻🏻🏻🏻🏻🏻 
        Амф: 1г-2500(белый) 
        Амф: 1г-2500.(розовый) 
        Соль: 1г-2500р. 
        Мет: 1г-3000р. 
        Меф: 1г-3000р
        MDMA(crystals): 1г-3500р. 
         
        Tesla (250mg MDMA) 
        SKYPE (230 mg MDMA) 
        Molly (230mg MDMA) 
        🔻1-5 шт. 1200р/шт 
        🔻5-10 шт. 980р/шт
        🍄🍄🍄🍄🍄🍄🍄🍄🍄🍄
        LSD доты: ЛСД-25(250мг)-2400р/2шт
        ️LSD марки: 250мг/3400р/2шт
        Мескалин: 
        🔻Мухоморы: 3000р/10гр/2дозы
        🔻Сульфат: 3000р/1гр/2дозы
        ️Псилоцебиновые грибы:
        🔻Golden teacher: 4000р/3гр
        🔻Psilocybe Cubensis:4000р/3гр
        🔻Pink Buffalo: 4000р/3гр
        ГРИБЫ!!!! Рекомендованая дозировка не мение 1г на человека. Для новичков не стоит употреблять больше 2г. Оптимальный вариант разделить 3г с другом, и отправиться в незабываемое путешествие, по глубинам своего сознания!
        Для опытных предлагаю дозировку в 3г. Погружение на 8 часов вам обеспеченно. Хорошо сочитаеться с марихуанной.
        Так же перед употреблением советуем не принимать пищу за 3-5 часов.""".replace('\n',' ')
        l1.append(inline_keyboard('Выбрать '+product_main_spec, 'main_cat'))
        l1.append(inline_keyboard('На главную', '/start')) 
    elif method == 'cashbalance':#balance itd
        text = 'Ваш баланс: '+str(q1.balance)+''
        l1.append(inline_keyboard('Пополнить', 'replenish'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish':
        text = replenish_msg
        l1.append(inline_keyboard('Отправил', 'replenish_check'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'replenish_check':
        text = 'Введите номер транзакции.'
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
        text = 'Данная транзакция отсутствует.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('На главную', '/start'))
    #/pomosh
    elif method == 'helpme':
        text = help_msg
        l1.append(inline_keyboard('Связь с оператором', 'support'))
        l1.append(inline_keyboard('Ищу работу', 'seekjob'))
        l1.append(inline_keyboard('На главную', '/start'))
    #oplata s balansa + redirect na popolneniye
    elif method[0] == 'b':
        dsa = product.objects.get(pk=method[1:])
        if dsa.buyer:
            text = 'К сожалению, данный товар был только-что куплен или зарезервирован, попробуйте выбрать снова.'
        else:
            text = 'Ваш баланс: '+str(q1.balance)+'.\nСтоимость '+dsa.type_of_product.name+' в '+ dsa.placing.pre_full_name+': '+str(dsa.price)
            #proveryaem est' li vozmozhnost' oplatit'
            if q1.balance >= dsa.price:
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
        l1.append(inline_keyboard('На главную', '/start'))
    #oplata s balansa
    elif method[0] == 'v':
        #tut sdelai proverku na nalichiye tovara, chtobi klient vdrug ne oplatil tovar kotoriy uzhe prodan cherez try except
        try:
            qua = product.objects.get(pk=method[1:], buyer = None)
            if q1.balance >= qua.price:
                q1.balance-=qua.price  
                if fake_app == 0:
                    qua.buyer = q1
                    qua.sold_date = timezone.now()
                    qua.save()
                elif fake_app == 1:
                    q1.fake_purchases.add(qua)
                q1.save()
                text = 'Оплата прошла успешно.\nВаш баланс: '+str(q1.balance)+'\nДля получения информации о товаре нажмите "Подробнее"'
                l1.append(inline_keyboard('Подробнее', 'j'+str(qua.pk)))
            else:
                text = 'К сожалению, на вашем балансе недостаточно средств для оплаты.'
        except:
            #tut soobsheniye ob oshibke, ili tovar prodan, ili deneg na balance ne hvataet, ili eshe kakayato ebala, zameni
            #na try except
            text = 'К сожалению, данный товар был только-что куплен или зарезервирован,попробуйте выбрать ещё раз.'
        l1.append(inline_keyboard('На главную', '/start'))
    #oplata transakciyei
    elif method[0] == 'h':
        dsa = product.objects.get(pk=method[1:])
        if dsa.buyer:
            text = 'К сожалению, данный товар был только-что куплен или зарезервирован, попробуйте выбрать снова.'
        else:
            text = 'Товар: '+dsa.type_of_product.name+'\n\nМестоположение:'+dsa.placing.pre_full_name+'\n\nСтоимость: '+str(dsa.price)+'\n\nОтправьте платёж на сумму: '+str(dsa.price)+' на киви кошелёк: ' +qiwi_wallet_num+', после оплаты нажмите *Продолжить*.'
            l1.append(inline_keyboard('Продолжить', 'x'+str(dsa.pk)))
            l1.append(inline_keyboard('Обновить', method))
        l1.append(inline_keyboard('Назад', 'f'+str(dsa.type_of_product.pk)+'r'+str(dsa.placing.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    #podtverjdeniye transakcii
    elif method[0] == 'x':
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
    #esli ne hvataet deneg dlya oplati transakcii
    elif method == 'transaction_nem':
        text= 'К сожалению, сумма вашей транзакции меньше стоимости товара, денежные средства были зачислены на ваш баланс.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'transaction_bought':
        text= 'К сожалению, товар был оплачен раньше чем подтвердился ваш платёж, денежные средства были зачислены на ваш баланс.'
        l1.append(inline_keyboard('Помощь', 'helpme'))
        l1.append(inline_keyboard('Баланс', 'cashbalance'))
        l1.append(inline_keyboard('На главную', '/start'))
    #pokaz info o tovare
    elif method[0] == 'j':
        #da i sdelai proverku chto-bi s kompa nel'zya bilo na sharu sdelat' query j1 ili j23 chtobi otkrilos'
        #t.e. eto budet kak proverka id abonenta i ego privyazku k productu, t.e. esli est' to est' info, esli net, to
        #vikidivat' kakoyeto ebanoe soobsheniye
        #
        ###111111111111
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
        l1.append(inline_keyboard('На главную', '/start'))
        None
    #otpravki obrasheniya
    elif method == 'support':
        text = support_apply_msg
        q1.support_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    elif method == 'seekjob':
        text = support_apply_msg
        q1.job_seeker=True
        q1.save()
        l1.append(inline_keyboard('На главную', '/start'))
    #vibor glavnoi kategorii
    elif method == 'main_cat':
        text = 'Выберите '+product_main_spec+':'
        for i in raion.objects.filter(subcategory_of = None):
            l1.append(inline_keyboard(i.name, 'r'+str(i.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
    #vibor tovara posle main raiona
    elif method[0] == 'r':
        ##вообще, тут может возникнуть дохуя ошибок, И если планируется нечто потипу мирового с разделениями на страны
        #, то требуется рефакторинг
        #uznaem voobshe chto eto za raion
        g0 = raion.objects.get(pk=method[1:])
        g1 = raion.objects.filter(subcategory_of = g0)
        #delaem spisok teh vidov tovara dostupnykh v dannom main_raione

        ##new
        k1 = set()
        for i in g1:
            for m in product.objects.filter(placing = i, buyer = None):
                k1.add(m.type_of_product)
        #udalyaem pokupki ot pokupatelya
        if fake_app == 1:
            None
        #esli est' tovar
        if len(k1) > 0:
            text = 'Выберите товар в '+g0.pre_full_name+'.'
            for i in k1:
                l1.append(inline_keyboard(i.name, 'f'+str(i.pk)+'r'+str(g0.pk)))
        #esli netu, to
        else:
            text = 'К сожалению,на данный момент нет товаров в '+g0.pre_full_name+', попробуйте выбрать другое место.'
        #add back button
        if g0.subcategory_of:
            l1.append(inline_keyboard('Назад', 'r'+str(g0.subcategory_of.pk)))
        else:
            l1.append(inline_keyboard('Назад', 'main_cat'))

        ##new

        l1.append(inline_keyboard('На главную', '/start'))
    #vibor tovara posle main raiona
    elif method[0] == 'f':
        #delim method na 2 chasti(ispolzuya split(method, 'r')) 'f' i 'r', gde [0](f...) - kategoriya, [1](r...) - raion
        method = method.split('r')
        ##new
        #vizvaniy main_raion
        g0 = raion.objects.get(pk=method[1])
        #podkategorii main raiona
        g1 = raion.objects.filter(subcategory_of = g0)
        #vid producta
        g2 = product_type.objects.get(pk=method[0][1:])
        set0 = set()
        #delaem query na vse producti s subcategory == o i vid producta po requestu
        for o in g1:
            #esli budet chtoto, to
            for i in product.objects.filter(buyer= None ,type_of_product = g2, placing = o):
                set0.add(i.placing)
        if len(set0) > 0:
            text = 'Товар: '+g2.name+ '\nВ городе: '+g0.pre_full_name+'\n\nУточните район.'
            for i in set0:
                l1.append(inline_keyboard(i.name, 'u'+str(g2.pk)+'r'+str(i.pk)))
        else:
            text = 'Увы, товар был только-что продан или зарезервирован.'
        l1.append(inline_keyboard('Назад', 'r'+method[1]))
        l1.append(inline_keyboard('На главную', '/start'))
    #vibor raiona posle vibora raiona
    elif method[0] == 'u':
        #delim method na 2 chasti(ispolzuya split(method, 'u')) 'u' i 'r', gde [0](u...) - kategoriya, [1](r...) - raion
        #get object from products(raion = r, product_type = u), order_by date i vibor u kotorogo data sozdaniya samaya poslednyaya
        method = method.split('r')
        try:
            #eshe order by date zakladki
            asd = product.objects.filter(buyer= None ,type_of_product = product_type.objects.get(pk=method[0][1:]), placing = raion.objects.get(pk=method[1]))[0]
            text = str(asd.type_of_product.name)+' в '+str(asd.placing.pre_full_name)+'\nПо цене: '+str(asd.price)
            l1.append(inline_keyboard('Оплата с баланса', 'b'+str(asd.pk)))
            l1.append(inline_keyboard('Оплата по транзакции', 'h'+str(asd.pk)))
        except:
            text = 'Увы, товар был только что зарезервирован или продан, попробуйте выбрать другой товар.'
        l1.append(inline_keyboard('Назад', 'f'+method[0][1:]+'r'+str(raion.objects.get(pk=method[1]).subcategory_of.pk)))
        l1.append(inline_keyboard('На главную', '/start'))
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
                    #payment is real and not used
                    user_a.payment_instance = 0
                    a1, a2 = qiwi_api(recieve_text)
                    #esli uspeh
                    if a1 == True:
                        user_a.balance=user_a.balance+ float(a2)
                        finished_transaction.objects.create(project_fk = tg_project, abonent = user_a, txnId = recieve_text, cash = float(a2))
                        #
                        #
                        #TUT
                        smsg(a2)
                        #OTPRAVLYAI OTCHET NA MOE OBLAKO ONO MNE NUZHNO
                        #CHTOBI SCHITAT' PRIBIL', PRIBIL' BUDET SCHTITASYA
                        #от сумм пополнения баланса или выполнения транзакций
                        #
                        #
                        return_dict["text"], return_dict["reply_markup"] = reply('replenish_success', user_a, a2)
                    #payment is real but already used
                    elif a1 == False:
                        return_dict["text"], return_dict["reply_markup"] = reply('replenish_exists', user_a)
                    #payment does'nt exists
                    #tipo void? ili kak v pythone eto der'mo?
                    else:
                        return_dict["text"], return_dict["reply_markup"] = reply('replenish_fail', user_a)
                    user_a.save()
                elif user_a.payment_instance == 2:#v sluchae podtverjdeniya oplati za zakaz(т.е. проведения транзакции)
                    user_a.payment_instance = 0
                    a1, a2 = qiwi_api(recieve_text)
                    if a1 == True:
                        #1000 + 1500 = 2500
                        user_a.balance=user_a.balance+ float(a2)
                        finished_transaction.objects.create(project_fk = tg_project, abonent = user_a, txnId = recieve_text, cash = float(a2))
                        #esli deneg hvataet na transakciyu
                        if user_a.balance >= user_a.transaction_instance.price:
                            #tut chekai est' li u obiekta pokupki pokupatel' dabi ne perepisivat' istoriyu
                            #esli ne norm, to:
                            if user_a.transaction_instance.buyer:
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
                        #
                        #
                        #TUT
                        smsg(a2)
                        #OTPRAVLYAI OTCHET NA MOE OBLAKO ONO MNE NUZHNO
                        #CHTOBI SCHITAT' PRIBIL', PRIBIL' BUDET SCHTITASYA
                        #от сумм пополнения баланса или выполнения транзакций
                        #
                        #
                    #payment is real but already used
                    elif a1 == False:
                        return_dict["text"], return_dict["reply_markup"] = reply('replenish_exists', user_a)
                    #payment does'nt exists
                    #tipo void? ili kak v pythone eto der'mo?
                    else:
                        return_dict["text"], return_dict["reply_markup"] = reply('replenish_fail', user_a)
                    user_a.transaction_instance = None
                    user_a.save()
                #v sluchae esli init fraza
                elif recieve_text == tg_project.start_word:
                    return_dict["text"], return_dict["reply_markup"] = reply(recieve_text)
                #missunderstood msg na obichnuyu otpravku soobsheniya
                else:
                    return_dict["text"] = 'Попробуйте написать: '+tg_project.start_word
        #esli eto nazhatiye na knopki
        elif reply_type == 'callback_query':
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
    if True:#testting purpose
        try:
            ##dlya raboti s jsonom
            print(user_info["data"])
            #print(request.body)
            #print(return_dict)
            None
        except:
            None
    if return_dict:return JsonResponse(return_dict)
    else:return HttpResponse('')

qiwi_token = '47b27250733beb5c3c153a2a6003e523'
qiwi_headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization' :'Bearer '+qiwi_token+''}
qiwi_wallet_num = '79841543923'
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
                        return True, str(transaction_json["total"]["amount"])
        except:
        ##payment does'nt exists ili ne prenadlejit etomu qiwi ili chtoto drugoe, mb server upal, mb qiwi upal, yaneebu
            return None, None
    #utils\test