from django import forms
from .models import *

class raionForm(forms.ModelForm):
    class Meta:
        model = raion
        fields = '__all__'
        widgets = {}

class product_typeForm(forms.ModelForm):
    class Meta:
        model = product_type
        fields = '__all__'
        widgets = {}

class productForm(forms.ModelForm):
    class Meta:
        model = product
        fields = '__all__'
        widgets = {}