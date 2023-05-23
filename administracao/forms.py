from django import forms
from django.contrib.auth.models import User
from clientes.models import Cliente

class EmailEmMassaForm(forms.Form):
    assunto = forms.CharField(label='Assunto', max_length=100)
    corpo = forms.CharField(label='Corpo', widget=forms.Textarea)
    clientes = forms.MultipleChoiceField(widget=forms.SelectMultiple)

    def __init__(self, *args, **kwargs):
        super(EmailEmMassaForm, self).__init__(*args, **kwargs)
        self.fields['clientes'].choices = [(cliente.id, cliente.user.username) for cliente in Cliente.objects.filter(propaganda=True)]




from django import forms
from produtos.models import Category

class SelecionarPeriodoForm(forms.Form):
    data_inicial = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data Inicial')
    data_final = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data Final')
    categoria = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Todas as categorias', required=False)



