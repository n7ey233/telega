from django.db import models
##pokupatel', chtobi smotret' ego balance, 
#mb delat' skidki 
#i otslezhivat' sostoyaniye obsheniya s botom
class abonent(models.Model):
    #instance obsheniya (
    #0- hello
    #1- tovar vibran
    #2- vibran raion
    #3- soglasiye na oplatu
    #4- redirect na 0, t.k. sdelka provedena
    #)
    ####
    #balance(dlya kur'yeznikh sluchaev, kogda zakinul chutka bolshe chem nuzhno)
    #ego id dlya telegi
    telega_id = models.IntegerField(default = 0, verbose_name='ID')
    #oborot(dlya skidok mb?)
    name = models.CharField(max_length=128, blank = True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
##produkciya bivaet raznih tipov
class product_type(models.Model):
    name = models.CharField(max_length=128, blank = False)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
##ispol'zuyetsa dlya razdeleniya produkcii na raioni
class raion(models.Model):
    name = models.CharField(max_length=128, blank = False)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
##eto instance sdelki, hotyaaa
#voobshe, ya bi nazval eto product_instance, hotya kto suda polezet?
class product(models.Model):
    #fk na product_type
    #fk na raion(tipo mesto v kakom raione prychetsya)
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
