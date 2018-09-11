from django.conf.urls import url
from . import views
urlpatterns = [
    #telegram api
    url(r'^j128302dwiq0ej833fcu8iaqhj8c932$', views.telegram_api, name='telegram_api'),
    #qiwi api

    #login
    url(r'^dengji$', views.sign, name='sign'),
    #staff
    
    #admin
    url(r'^main_page/cp$', views.main, name='main'),
    url(r'^main_page/cp/formpage$', views.formpage, name='formpage'),
]