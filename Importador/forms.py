# forms.py
from django import forms

class ImportClientesForm(forms.Form):
    file = forms.FileField(label='Arquivo CSV')


