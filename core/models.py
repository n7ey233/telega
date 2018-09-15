from django.db import models
##pokupatel', chtobi smotret' ego balance, 
#mb delat' skidki 
#i otslezhivat' sostoyaniye obsheniya s botom
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
    telega_id = models.IntegerField(blank = False, verbose_name='ID')
    balance = models.FloatField(default = 0)
    #oborot(dlya skidok mb?)
    name = models.CharField(max_length=128, blank = True, verbose_name='名称为啥')
    job_seeker = models.BooleanField(default=False, verbose_name='Ищет работу')
    support_seeker = models.BooleanField(default=False, verbose_name='Ждет связи с оператором')
    class Meta:
        ordering = ['telega_id']
    def __str__(self):
        return str(self.telega_id)
##produkciya bivaet raznih tipov
class product_type(models.Model):
    name = models.CharField(max_length=128, blank = False, verbose_name='Название')
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
##ispol'zuyetsa dlya razdeleniya produkcii na raioni
class raion(models.Model):
    pre_full_name = models.TextField(blank = True, verbose_name='префикс, используется для отображения' )
    name = models.CharField(max_length=128, blank = False, verbose_name='Название' )
    subcategory_of = models.ForeignKey('self', blank=True, null= True, on_delete=models.SET_NULL, verbose_name='Подкатегория от')
    class Meta:
        ordering = ['pre_full_name']
    def __str__(self):
        return self.name
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
##eto instance sdelki, hotyaaa
#voobshe, ya bi nazval eto product_instance, hotya kto suda polezet?
class product(models.Model):
    #fk na product_type
    placing = models.ForeignKey(product_type, blank=False, null= True, on_delete=models.SET_NULL, verbose_name='Вид товара')
    #fk na raion(tipo mesto v kakom raione prychetsya)
    placing = models.ForeignKey(raion, blank=False, null= True, on_delete=models.SET_NULL, verbose_name='Место хранения')
    #kolichestvo
    #cena v chem-to
    #sostoyaniye sdelki(zavershena ili v processe ili pustuyet)
    #dop komentariy (hz zachem, vozmozhno opisaniye mesta zakladki?)
    #geolokaciya
    #ssilka na foto
    #fk na abonent(pokupatelya, pri zavershenii sdelki)
    name = models.CharField(max_length=128, blank = False)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class chat_msg(models.Model):
    #abonent
    abonent = models.ForeignKey('abonent', blank = False, on_delete=models.CASCADE, verbose_name='Вид')
    #text
    text = models.TextField(blank = True, verbose_name='Текст')
    #datetime

class site_settings(models.Model):
    product_main_spec = models.TextField(blank = True, verbose_name='Название первой категории')
    shop_name = models.TextField(blank = True, verbose_name='Название магазина')
# Create your models here.
