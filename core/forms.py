from django import forms
from .models import *

class raionForm(forms.ModelForm):
    class Meta:
        model = raion
        fields = '__all__'
        exclude = ['pre_full_name']
        widgets = {}
    def __init__(self, *args, **kwargs):
        super(raionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'        
    

class product_typeForm(forms.ModelForm):
    class Meta:
        model = product_type
        fields = '__all__'
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Название'}),
        'price': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Цена за ед. продукта, если пусто, то дефолту с неё берется ценник на товары'}),
        }
    def __init__(self, *args, **kwargs):
        super(product_typeForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'        


class productForm(forms.ModelForm):
    class Meta:
        model = product
        fields = '__all__'
        widgets = {}
    def __init__(self, *args, **kwargs):
        super(productForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class abonentForm(forms.ModelForm):
    class Meta:
        model = abonent
        fields = '__all__'
        exclude = ['payment_instance', 'transaction_instance']
        widgets = {}

    def __init__(self, *args, **kwargs):
        super(abonentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class site_settingsForm(forms.ModelForm):
    class Meta:
        model = site_settings
        fields = '__all__'
        widgets = {}
    def __init__(self, *args, **kwargs):
        super(site_settingsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'        

