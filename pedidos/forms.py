from django import forms
from django.contrib.sites import requests

from .models import EnderecoEntrega
class EnderecoEntregaForm(forms.ModelForm):
    class Meta:
        model = EnderecoEntrega
        fields = ['cep', 'rua', 'numero', 'bairro', 'cidade', 'estado', 'complemento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cep'].widget.attrs.update({'class': 'form-control', 'placeholder': 'CEP'})
        self.fields['rua'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Rua'})
        self.fields['numero'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Número'})
        self.fields['bairro'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Bairro'})
        self.fields['cidade'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Cidade'})
        self.fields['estado'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Estado'})
        self.fields['complemento'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Complemento (opcional)'})

    def clean_cep(self):
        cep = self.cleaned_data['cep']
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        if response.status_code == 200:
            data = response.json()
            if 'erro' in data:
                raise forms.ValidationError('CEP inválido')
            else:
                self.cleaned_data['rua'] = data['logradouro']
                self.cleaned_data['bairro'] = data['bairro']
                self.cleaned_data['cidade'] = data['localidade']
                self.cleaned_data['estado'] = data['uf']
        else:
            raise forms.ValidationError('Erro ao consultar CEP')
        return cep