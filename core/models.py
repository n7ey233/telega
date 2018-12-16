from django.db import models
from django.utils import timezone
from .telegram_api import set_webhook, get_tg

class telegram_project(models.Model):#proekt telegrama
    tg_types = (
    ('tg_shop_fake', 'tg_shop_fake'),
    )
    tg_type = models.CharField(max_length=22, blank = False, choices=tg_types, default='tg_shop_fake', verbose_name='Тип телеги')
    tg_token = models.CharField(max_length=128, blank = False, verbose_name='tg_token')
    tg_id = models.CharField(max_length=128, blank = True, verbose_name='tg_id, 为了看清楚')
    tg_username = models.CharField(max_length=128, blank = True, verbose_name='tg_username, 为了看清楚')
    tg_first_name = models.CharField(max_length=128, blank = True, verbose_name='tg_first_name, 为了看清楚')
    web_hook_chained = models.BooleanField(default = False, blank = False, verbose_name='вебхук')
    start_word = models.CharField(max_length=128, blank = False, verbose_name='стартовая фраза')
    class Meta:
        ordering = ['tg_username']
    def __str__(self):
        return str(self.tg_username)
    def save(self, *args, **kwargs):
        if self.id == None:#1st init
            if set_webhook(self.tg_token, self.pk) is True: self.web_hook_chained = True
            self.tg_id = str(get_tg(self.tg_token, 'id'))
            self.tg_username = str(get_tg(self.tg_token, 'username'))
            self.tg_first_name = str(get_tg(self.tg_token, 'first_name'))
        super().save()
class abonent(models.Model):
    #instance obsheniya (
    #0- default (nikakoi operacii)
    #1- (podgotovka oplati, ozhidaniye nomera transakcii)
    #2- 付款成功, redirect na 0
    #)
    ####
    #balance(dlya kur'yeznikh sluchaev, kogda zakinul chutka bolshe chem nuzhno или когда закинули недостаточно для оплаты)
    #ego id dlya telegi
    payment_instance = models.IntegerField(default = 0, verbose_name='инстанс платёжки')
    telega_id = models.IntegerField(blank = False, verbose_name='ID Телеги')
    balance = models.FloatField(default = 0, verbose_name='Баланс')
    #oborot(dlya skidok mb?)
    name = models.CharField(max_length=128, blank = True, verbose_name='名称为啥，用不用呢？')
    job_seeker = models.BooleanField(default=False, verbose_name='Ищет работу')
    support_seeker = models.BooleanField(default=False, verbose_name='Ждет связи с оператором')
    transaction_instance = models.ForeignKey('product', blank=True, null= True, on_delete=models.SET_NULL, verbose_name='используется для назначения инстанса при оплате транзакцией')
    fake_purchases =models.ManyToManyField('product' , blank = True,symmetrical=False, verbose_name='Список транзакциий апп', related_name="fake_one")
    class Meta:
        ordering = ['telega_id']
    def __str__(self):
        return str(self.telega_id)
class product_type(models.Model):##produkciya bivaet raznih tipov
    name = models.CharField(max_length=128, blank = False, verbose_name='Название')
    price = models.FloatField(blank = False, default = 500, verbose_name='Цена за ед. продукта, если пусто, то дефолту с неё берется ценник на товар')
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
class raion(models.Model):##ispol'zuyetsa dlya razdeleniya produkcii na raioni
    pre_full_name = models.TextField(blank = True, verbose_name='префикс, используется для отображения' )
    name = models.CharField(max_length=128, blank = False, verbose_name='Название' )
    subcategory_of = models.ForeignKey('self', blank=True, null= True, on_delete=models.SET_NULL, verbose_name='Подкатегория от')
    class Meta:
        ordering = ['pre_full_name']
    def __str__(self):
        return self.pre_full_name
    def save(self, *args, **kwargs):
        if self == self.subcategory_of:
            return None
        full_path = [self.name]
        k = self.subcategory_of 
        while k is not None:
            full_path.append(k.name)
            k = k.subcategory_of
        self.pre_full_name = '/'.join(full_path[::-1])
        super().save()
class product(models.Model):##eto instance sdelki, hotyaaa#voobshe, ya bi nazval eto product_instance, hotya kto suda polezet?
    #fk na product_type
    type_of_product = models.ForeignKey(product_type, blank=False, null= True, on_delete=models.SET_NULL, verbose_name='Вид товара')
    #fk na raion(tipo mesto v kakom raione prychetsya)
    placing = models.ForeignKey(raion, blank=False, null= True, on_delete=models.SET_NULL, verbose_name='Место хранения')
    #data pukupki
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    #data prodaji
    sold_date = models.DateTimeField(blank=True, null= True, verbose_name='Дата продажи')
    ##kolichestvo
    #a nado li ono?
    ##cena v chem-to
    price = models.FloatField(blank=True, null = True,verbose_name='Цена, если пусто, то ценник берется с вида продукции')
    #sostoyaniye sdelki(zavershena ili v processe ili pustuyet)
    #dop komentariy (hz zachem, vozmozhno opisaniye mesta zakladki?)
    commentary = models.TextField(blank = False, null = True, verbose_name='Дополнительное описание')
    #geolokaciya
    geolocation = models.URLField(max_length = 256,blank=False, null= True, verbose_name='Ссылка на геолокацию' )
    #ssilka na foto
    foto_link = models.URLField(max_length = 256,blank=False, null= True, verbose_name='Ссылка на фото' )
    #fk na abonent(pokupatelya, pri zavershenii sdelki)
    buyer = models.ForeignKey(abonent, blank=True, null= True, on_delete=models.SET_NULL, verbose_name='Покупатель')
    #fk na rabotnika(tipo kto delal zakladku)    
    #placer = models.ForeignKey(abonent, blank=False, null= True, on_delete=models.SET_NULL, verbose_name='Покупатель')
    class Meta:
        ordering = ['created_date']
    def __str__(self):
        return self.type_of_product.name
    def save(self, *args, **kwargs):
        if self.price == None:
            self.price = self.type_of_product.price
        super().save()
class chat_msg(models.Model):
    #abonent
    abonent = models.ForeignKey('abonent', blank = False, on_delete=models.CASCADE, verbose_name='Вид')
    #text
    text = models.TextField(blank = True, verbose_name='Текст')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')#datetime
    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        str(self.created_date) + ' ' + str(self.abonent) 
class site_settings(models.Model):
    product_main_spec = models.CharField(max_length=128, blank = True, verbose_name='Название первой категории')
    shop_name = models.CharField(max_length=128, blank = True, verbose_name='Название магазина')
    #tele_token
    tele_token =models.CharField(max_length=128, blank = True, verbose_name='токен телеги')
    #telebot_name
    #qiwi_token
    qiwi_token = models.CharField(max_length=128, blank = True, verbose_name='токен киви') 
    ##used in replenish balance
    #qiwi_wallet_num
    qiwi_wallet_num =  models.CharField(max_length=128, blank = True, verbose_name='номер киви')
    def __str__(self):
        return ('Настройки сайта')
class finished_transaction(models.Model):
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    project_fk = models.ForeignKey('telegram_project', blank=False, null= False, on_delete=models.CASCADE, verbose_name='project_fk')
    paid_transaction = models.BooleanField(default = False, blank = False, verbose_name='Оплачено')
    abonent = models.ForeignKey('abonent', blank = False, on_delete=models.CASCADE, verbose_name='Пополнитель(из телеги)')
    txnId = models.CharField(blank = True, max_length=128, verbose_name='Номер транзакции')
    cash = models.FloatField(default = 0, verbose_name='Сумма')
    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        str(self.created_date) + ' ' + str(self.amount)
